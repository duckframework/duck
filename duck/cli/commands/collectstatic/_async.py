"""
Module containing asynchronous collectstatic command class.
"""

import os
import pathlib
import asyncio
import itertools

from typing import Dict, Generator, List, Tuple

from duck.logging import console
from duck.routes import Blueprint

from duck.contrib.storage.backends import StorageBackend, UploadContext
from duck.contrib.sync import ensure_async
from duck.utils.fileio import AsyncFileIOStream
from duck.utils.caching import InMemoryCache


# Shared cache for FileIOStream
FILE_CACHE = InMemoryCache(maxkeys=1024)

# Upper bound on simultaneous uploads, keeps open file handles and threads in check
MAX_CONCURRENCY = 32


class AsyncCollectStaticCommand:
    """
    Collects static files and uploads them to the configured storage backend.
    """

    @classmethod
    def setup(cls) -> None:
        """
        Prepares the environment before collecting static files.
        """
        pass

    @classmethod
    def main(cls, skip_confirmation: bool = False) -> None:
        """
        Runs the collectstatic command.

        Args:
            skip_confirmation: Skips the confirmation prompt when True.
        """
        cls.setup()
        asyncio.run(cls.collectstatic(skip_confirmation))

    @classmethod
    def get_storage(cls) -> StorageBackend:
        """
        Builds the storage backend that receives the static files.

        Returns:
            The configured StorageBackend.
        """
        from duck.settings.loaded import SettingsLoaded

        return SettingsLoaded.STATICFILES_BACKEND.getresult()

    @classmethod
    async def collect_entries(cls) -> List[Tuple[str, str]]:
        """
        Lists every static file as a pair of storage key and source path.

        Global static directories map to the root of the storage. Blueprint
        files are placed under the blueprint name. When two files share a key,
        the later one wins. All directories are scanned concurrently.

        Returns:
            A list of (key, source_path) tuples.
        """
        from duck.settings import SETTINGS

        # Each job is a (static_dir, key_prefix) pair, global dirs come first
        jobs: List[Tuple[str, str]] = [
            (static_dir, "") for static_dir in SETTINGS["GLOBAL_STATIC_DIRS"] or []
        ]
        jobs.extend(
            (static_dir, f"{blueprint.name}/")
            for static_dir, blueprint in cls.find_blueprint_static_dirs(prepare_django_now=True)
        )

        # Scan every directory at the same time
        results = await asyncio.gather(*(cls.recursive_getfiles(static_dir) for static_dir, _ in jobs))

        # Merge in job order so later directories override earlier ones
        entries: Dict[str, str] = {}

        for (static_dir, prefix), sources in zip(jobs, results):
            for source in sources:
                relative = pathlib.Path(source).relative_to(static_dir).as_posix()
                entries[f"{prefix}{relative}"] = source

        return list(entries.items())

    @classmethod
    async def upload_file(cls, storage: StorageBackend, key: str, source: str) -> bool:
        """
        Uploads a single static file unless the storage already has it.

        This is blocking and meant to run in a worker thread.

        Args:
            storage: Backend that receives the file.
            key: Storage key of the file.
            source: Path of the file on disk.

        Returns:
            True if the file was uploaded, False if it was unchanged.
        """
        mtime = pathlib.Path(source).stat().st_mtime

        async with AsyncFileIOStream(source, mode="rb", open_now=True, cache_backend=FILE_CACHE) as handle:
            payload = await handle.read()

            # Skip the upload when the file is unchanged
            if await storage.async_is_unchanged(key, UploadContext(filename=key, payload=payload, source_mtime=mtime)):
                return False

            # Rewind because reading the payload consumed the stream
            handle.seek(0)

            # Upload the file to the storage backend
            await storage.async_save_as(handle, key, source_mtime=mtime)
            
        return True

    @classmethod
    async def upload(
        cls,
        storage: StorageBackend,
        entries: List[Tuple[str, str]],
    ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, Exception]]]:
        """
        Uploads all static files to the storage backend concurrently.

        A failed upload does not stop the others, it is reported in the result.

        Args:
            storage: Backend that receives the files.
            entries: (key, source_path) pairs from `collect_entries`.

        Returns:
            A tuple of the uploaded (key, source_path) pairs and the
            (key, error) pairs that failed.
        """
        total = len(entries)
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        counter = itertools.count(1)

        async def worker(key: str, source: str) -> bool:
            async with semaphore:
                uploaded = await ensure_async(cls.upload_file)(storage, key, source)

            # Log progress as each file completes
            index = next(counter)

            if uploaded:
                console.log_raw(f"[{index}/{total}] {key} [done]", level=console.DEBUG)
            else:
                console.log_raw(f"[{index}/{total}] {key} (unchanged)", level=console.DEBUG, custom_color=console.Fore.YELLOW)

            return uploaded

        results = await asyncio.gather(
            *(worker(key, source) for key, source in entries),
            return_exceptions=True,
        )

        # Separate the uploaded files from the failed ones
        uploaded: List[Tuple[str, str]] = []
        failed: List[Tuple[str, Exception]] = []

        for (key, source), result in zip(entries, results):
            if isinstance(result, Exception):
                failed.append((key, result))

            elif result:
                uploaded.append((key, source))

        return uploaded, failed

    @classmethod
    async def collectstatic(cls, skip_confirmation: bool = False) -> None:
        """
        Collects static files and uploads them to the configured storage.

        Args:
            skip_confirmation: Skips the confirmation prompt when True.
        """
        entries = await cls.collect_entries()

        if not entries:
            console.log_raw("\nNo staticfiles found!", level=console.WARNING)
            return

        # Build the storage backend and show a confirmation prompt
        storage = cls.get_storage()
        destination = type(storage).__name__

        if not skip_confirmation:
            # Show confirmation prompt
            console.log_raw(
                f"\nWould you like to copy {len(entries)} staticfile(s) to {destination} (y/N): ",
                end="",
                level=console.DEBUG,
            )

            # Read the answer in a thread so the event loop is not blocked
            choice = await ensure_async(input)("")

            if not choice.lower().startswith("y"):
                console.log_raw("\nCancelled, bye!", level=console.WARNING)
                return

        # Create a blank line before the upload progress
        console.log_raw("")

        # Upload the static files to the storage backend
        uploaded, failed = await cls.upload(storage, entries)

        console.log_raw(
            f"\nSuccessfully copied {len(uploaded)} staticfile(s) to {destination}",
            level=console.SUCCESS,
        )

        # Report every file that could not be uploaded
        if failed:
            console.log_raw(f"\nFailed to copy {len(failed)} staticfile(s):", level=console.ERROR)

            for key, error in failed:
                console.log_raw(f"  {key}: {error}", level=console.ERROR)

    @classmethod
    async def recursive_getfiles(cls, directory: str) -> List[str]:
        """
        Lists every file path within a directory and its subdirectories.

        Subdirectories are scanned concurrently.

        Args:
            directory: Directory to search.

        Returns:
            Path of each file found, empty if the directory does not exist.
        """
        def scan(path: str) -> Tuple[List[str], List[str]]:
            files: List[str] = []
            subdirs: List[str] = []

            with os.scandir(path) as scanner:
                # Scan the directory
                for dir_entry in scanner:
                    if dir_entry.is_dir():
                        subdirs.append(dir_entry.path)

                    elif dir_entry.is_file():
                        files.append(dir_entry.path)

            return files, subdirs

        if not pathlib.Path(directory).is_dir():
            return []

        # Scan the directory and its subdirectories concurrently
        files, subdirs = await ensure_async(scan)(str(directory))
        nested = await asyncio.gather(*(cls.recursive_getfiles(subdir) for subdir in subdirs))

        for sub_files in nested:
            files.extend(sub_files)

        return files

    @classmethod
    def find_blueprint_static_dirs(cls, prepare_django_now: bool = False) -> Generator[Tuple[str, Blueprint], None, None]:
        """
        Finds static directories from all blueprints that enable them.

        Yields:
            (static_directory, blueprint) pairs.
        """
        from duck.backend.django.setup import prepare_django, DjangoSetupWarning
        from duck.settings import SETTINGS
        from duck.settings.loaded import SettingsLoaded
        from duck.utils.path import joinpaths

        blueprints = SettingsLoaded.BLUEPRINTS

        # Some blueprints import Django models, so set up Django first
        try:
            prepare_django(prepare_django_now)
            
        except Exception as e:
            console.warn(f"Django setup failed: {e}", DjangoSetupWarning)

            if SETTINGS["DEBUG"]:
                console.log_exception(e)

        for blueprint in blueprints:
            if blueprint.enable_static_dir:
                static_dir = (
                    blueprint.static_dir
                    if blueprint.static_dir_is_absolute
                    else joinpaths(blueprint.root_directory, blueprint.static_dir)
                )

                if pathlib.Path(static_dir).is_dir():
                    yield (static_dir, blueprint)
