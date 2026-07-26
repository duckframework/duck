# Duck Sync

Dependency sync tool for Duck Framework projects. Reads `duck.toml` and installs
Python and system packages in one command, across any platform.

---

## Installation

Duck Sync ships with Duck Framework. No separate install needed.

---

## duck.toml

Place `duck.toml` at your project root and commit it to version control.

```toml
# duck.toml

[dependencies]
# Python packages (pip/uv)
python = ["requests", "psycopg2"]

# System packages (apt, brew, pacman, etc.)
# Write generic names — Duck Sync resolves per platform.
system = ["postgresql-client", "gdal"]

# Optional: requirements.txt installed alongside python list
# requirements = "requirements.txt"

# Optional: extra args for every pip/uv install in this group
# python_args = ["--no-cache-dir"]

# Optional: extra args for every system install in this group
# system_args = ["--no-install-recommends"]


[development]
# Only installed when --dev or --with-dev is passed
python = ["pytest", "ruff", "mypy"]
system = []


[sync]
# Pin sudo behaviour (optional — auto-detected by default)
# true  = always use sudo for system installs
# false = never use sudo (e.g. already root inside a container)
# use_sudo = true


[overrides]
# Override the resolved package name for a specific backend.
#
# [overrides.mypackage]
# apt    = "libmypackage-dev"
# brew   = "mypackage"
# pacman = "mypackage"
```

---

## Commands

### `duck sync`

Install project dependencies.

```
duck sync [OPTIONS]
```

| Option | Short | Description |
|---|---|---|
| `--with-dev` | | Install `[dependencies]` and `[development]` |
| `--dev` | `-d` | Install `[development]` only |
| `--dry-run` | | Print planned installs without running them |
| `--config PATH` | `-c` | Explicit path to `duck.toml` (auto-discovered by default) |
| `--pip-args TEXT` | | Extra args appended to every pip/uv install |
| `--system-args TEXT` | | Extra args appended to every system install |
| `--sudo / --no-sudo` | | Force sudo on or off for system installs |
| `--backend TEXT` | `-b` | Override the auto-detected package manager |

#### Examples

```bash
# Install [dependencies] only
duck sync

# Install [development] only
duck sync --dev

# Install everything
duck sync --with-dev

# Preview without installing
duck sync --dry-run
duck sync --with-dev --dry-run

# Use a specific package manager
duck sync --backend brew
duck sync --backend pacman
duck sync --backend "some_command -i"

# Force sudo
duck sync --sudo
duck sync --no-sudo

# Pass extra pip flags
duck sync --pip-args "--no-cache-dir"
duck sync --pip-args "--extra-index-url https://download.pytorch.org/whl/cu118"

# Pass extra system flags
duck sync --system-args "--no-install-recommends"

# Point to a different config
duck sync -c path/to/duck.toml
```

---

## Package name resolution

System packages are written as generic names in `duck.toml`. Duck Sync maps them
to the correct name for the active package manager automatically.

| Generic name | apt | brew | dnf | pacman | choco |
|---|---|---|---|---|---|
| `gdal` | `gdal-bin libgdal-dev` | `gdal` | `gdal gdal-devel` | `gdal` | `gdal` |
| `geos` | `libgeos-dev` | `geos` | `geos geos-devel` | `geos` | `geos` |
| `postgresql-client` | `libpq-dev` | `libpq` | `libpq-devel` | `postgresql-libs` | `postgresql` |
| `jpeg` | `libjpeg-dev` | `jpeg` | `libjpeg-turbo-devel` | `libjpeg-turbo` | `libjpeg-turbo` |
| `ffmpeg` | `ffmpeg` | `ffmpeg` | `ffmpeg` | `ffmpeg` | `ffmpeg` |
| `spatialite` | `libsqlite3-mod-spatialite` | `libspatialite` | `libspatialite` | `libspatialite` | `spatialite` |

For any package not in the built-in registry, the generic name is passed through
unchanged. Most packages share the same name across managers so this works fine.

### Overriding a name

Add an `[overrides]` block to `duck.toml` to override for any backend:

```toml
[overrides.mypackage]
apt    = "libmypackage-dev"
brew   = "mypackage"
pacman = "mypackage"
```

---

## Backend selection

Duck Sync detects the system package manager automatically:

| Platform | Detection |
|---|---|
| macOS | `brew` |
| Debian / Ubuntu | `apt` |
| Fedora / RHEL | `dnf` |
| Arch Linux | `pacman` |
| Windows | `choco` |
| Android (Termux) | `pkg` |

Override detection for a single run with `--backend`:

```bash
# Force a known backend
duck sync --backend apt

# Use a completely custom install command
# The package name is appended as the last argument
duck sync --backend "nix-env -iA nixpkgs"
duck sync --backend "some_command -i"
```

---

## Sudo behaviour

| Situation | Behaviour |
|---|---|
| Running as a normal user | `sudo` is prepended automatically |
| Running as root (e.g. inside a container) | `sudo` is skipped |
| `use_sudo = true` in `duck.toml` | Always use `sudo` |
| `use_sudo = false` in `duck.toml` | Never use `sudo` |
| `--sudo` flag | Force `sudo` for this run |
| `--no-sudo` flag | Skip `sudo` for this run |

Precedence (highest to lowest): CLI flag → `duck.toml` → auto-detect.

Backends that never use sudo (`brew`, `choco`, `pkg`) ignore this setting entirely.

---

## Per-package extra args

Override install args for a specific package inside a group:

```toml
[dependencies]
python = ["torch", "requests"]

[dependencies.python_package_args]
torch = ["--index-url", "https://download.pytorch.org/whl/cu118"]

[dependencies.system_package_args]
gdal = ["--no-install-recommends"]
```

Group-level args (`python_args`, `system_args`) are applied first, then
per-package args, then any `--pip-args` / `--system-args` passed on the CLI.

---

## Errors

| Error | Cause |
|---|---|
| `ConfigNotFoundError` | No `duck.toml` found in the directory tree |
| `ConfigParseError` | `duck.toml` exists but contains invalid TOML |
| `UnsupportedPlatformError` | OS is unrecognised or no supported package manager is on PATH |
| `InstallationError` | A package manager command exited non-zero |

All errors inherit from `DuckSyncError`, so you can catch them in one place:

```python
from duck.cli.commands.sync.exceptions import DuckSyncError
from duck.cli.commands.sync.sync import DuckSync

try:
    DuckSync().run()
except DuckSyncError as e:
    print(f"Sync failed: {e}")
```