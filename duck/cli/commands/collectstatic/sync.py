"""
Module containing synchronous collectstatic command class.
"""

import os
import pathlib

from typing import Dict, Generator, List, Tuple

from duck.logging import console
from duck.routes import Blueprint

from duck.contrib.storage.backends import StorageBackend, UploadContext
from duck.utils.fileio import FileIOStream
from duck.utils.caching import InMemoryCache


FILE_CACHE = InMemoryCache(maxkeys=1024)


class CollectStaticCommand:
    # collectstatic command

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
        cls.collectstatic(skip_confirmation)

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
    def collect_entries(cls) -> List[Tuple[str, str]]:
        """
        Lists every static file as a pair of source path and storage key.

        Global static directories map to the root of the storage. Blueprint
        files are placed under the blueprint name. When two files share a key,
        the later one wins.

        Returns:
            A list of (source_path, key) tuples.
        """
        from duck.settings import SETTINGS

        entries: Dict[str, str] = {}

        # Global static directories map to the storage root
        for static_dir in SETTINGS["GLOBAL_STATIC_DIRS"] or []:
            for source in cls.recursive_getfiles(static_dir):
                key = pathlib.Path(source).relative_to(static_dir).as_posix()
                entries[key] = source

        # Blueprint files are namespaced by blueprint name
        for static_dir, blueprint in cls.find_blueprint_static_dirs(prepare_django_now=True):
            for source in cls.recursive_getfiles(static_dir):
                relative = pathlib.Path(source).relative_to(static_dir).as_posix()
                entries[f"{blueprint.name}/{relative}"] = source

        return list(entries.items())

    @classmethod
    def upload(cls, storage: StorageBackend, entries: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Uploads each static file to the storage backend.

        Args:
            storage: Backend that receives the files.
            entries: (source_path, key) pairs from `collect_entries`.
        
        Returns:
            List of (key, source_path) pairs that were uploaded.
        """
        total = len(entries)
        uploaded: List[Tuple[str, str]] = []
        
        for index, (key, source) in enumerate(entries, start=1):
            
            with FileIOStream(source, mode="rb", open_now=True, cache_backend=FILE_CACHE) as handle:
                # Check if the file is unchanged to skip upload
                mtime = pathlib.Path(source).stat().st_mtime

                if storage.is_unchanged(key, UploadContext(filename=key, payload=handle.read(), source_mtime=mtime)):
                    console.log_raw(f"[{index}/{total}] {key} (unchanged)", level=console.DEBUG, custom_color=console.Fore.YELLOW)
                    continue

                # Upload the file to the storage backend
                storage.save_as(handle, key, source_mtime=mtime)

            # Add the upload to the list of uploaded files
            uploaded.append((key, source))

            # Log the upload progress
            console.log_raw(f"[{index}/{total}] {key} [done]", level=console.DEBUG)

        return uploaded

    @classmethod
    def collectstatic(cls, skip_confirmation: bool = False) -> None:
        """
        Collects static files and uploads them to the configured storage.

        Args:
            skip_confirmation: Skips the confirmation prompt when True.
        """
        entries = cls.collect_entries()

        if not entries:
            console.log_raw("\nNo staticfiles found!", level=console.WARNING)
            return

        storage = cls.get_storage()
        destination = type(storage).__name__

        if not skip_confirmation:
            # Show confirmation prompt
            console.log_raw(
                f"\nWould you like to copy {len(entries)} staticfile(s) to {destination} (y/N): ",
                end="",
                level=console.DEBUG,
            )

            # Obtain confirmation from console
            choice = input("")

            if not choice.lower().startswith("y"):
                console.log_raw("\nCancelled, bye!", level=console.WARNING)
                return
        
        # Create a blank line before the upload progress
        console.log_raw("")

        # Upload the static files to the storage backend
        uploaded = cls.upload(storage, entries)

        console.log_raw(
            f"\nSuccessfully copied {len(uploaded)} staticfile(s) to {destination}",
            level=console.SUCCESS,
        )

    @classmethod
    def recursive_getfiles(cls, directory: str) -> Generator[str, None, None]: # type: ignore
        """
        Yields every file path within a directory and its subdirectories.

        Args:
            directory: Directory to search.

        Yields:
            Path of each file found.
        """
        directory: pathlib.Path = pathlib.Path(directory)

        if directory.is_dir():
            for dir_entry in os.scandir(directory):
                if dir_entry.is_file():
                    yield dir_entry.path
                else:
                    yield from cls.recursive_getfiles(dir_entry.path)

    @classmethod
    def find_blueprint_static_dirs(cls, prepare_django_now: bool = False) -> Generator[Tuple[str, Blueprint], None, None]:
        """
        Finds static directories from all blueprints that enable them.

        Returns:
            Generator of (static_directory, blueprint) pairs.
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
