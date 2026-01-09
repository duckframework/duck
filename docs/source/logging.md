# 📝 Duck Logging System

[![Logging](https://img.shields.io/badge/Feature-Logging-blue?style=for-the-badge)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck provides an **extensive and customizable logging system** to track your application’s behavior and errors.

By default, every Duck app session is logged to a file. To **disable file logging**, set:

```py
LOG_TO_FILE = False
```

---

## ⚡ Other Logging Options

### SILENT

Disables **all logging**, including console output and log files.  
- Useful in testing environments to avoid unnecessary logs.

### DJANGO_SILENT

Disables logging **only for Django integration** (`USE_DJANGO=True`).

### LOGGING_DIR

Directory to store log files.  
- Default: `assets/logs`  
- Can be customized to any directory path.

### LOG_FILE_FORMAT

Controls the **filename format** for log files.  
- Default: Uses `[year, month, day]_[hour, minutes, seconds]`  
- Avoids `:` in time for Windows compatibility.

### PREFERRED_LOG_STYLE

Choose the preferred log style:

- `"duck"` → Clean, readable logs (default)  
- `"django"` → Django-style logs  
- `None` → Auto-selects based on `USE_DJANGO` setting

### VERBOSE_LOGGING

Provides **detailed exceptions with tracebacks**.  
- Always `True` in `DEBUG` mode.  
- Set to `False` to reduce verbosity.

---

## 🖥️ Logs CLI

Duck comes with a **command-line tool** for managing logs.

```sh
cd myduckproject
duck logs list   # List all logs
duck purge       # Delete all logs
```

### CLI Flags

| Flag  | Description |
|-------|-------------|
| `-s`  | Sort logs by `"oldest"`, `"newest"`, `"largest"` |
| `-ss` | Show log sizes in human-readable units (KB, MB) |
| `-n`  | Target a specific number of logs |

### Other Commands

- `size` → Shows total size of all logs  
- `count` → Counts total number of logs  

---

✨ Duck logging allows you to **track, analyze, and manage logs efficiently**, whether for development, debugging, or production monitoring.
