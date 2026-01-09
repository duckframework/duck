# 🌐 Duck Service Management

The following commands allow you to create, start, stop, enable, disable, reload, and check the status of the Duck service using `systemd` on Linux-based systems. These commands help manage the service for your Duck web server.

## Requirements

- **Linux-based system** with `systemd` installed.
- **Python** installed, along with the required dependencies for the Duck framework.
- The system must support the use of `systemctl` for managing services.

## Commands Overview

The following commands are available for managing the Duck service:

### `autorun`

Creates and runs the systemd service for Duck.

**Usage:**  

```bash
duck service autorun
```

This command generates a `systemd` service file based on the configuration settings in the Duck framework and saves it in the systemd service directory (`/etc/systemd/system/`). The service will be configured to run the Duck web server with the specified settings.

``` {note}
This automatically creates and runs the **Duck** service at latest changes, you do not need to reload systemd, everything will be done for you.
```

### `create`

Creates the systemd service for Duck.

**Usage:**  

```bash
duck service create
```

This command generates a `systemd` service file based on the configuration settings in the Duck framework and saves it in the systemd service directory (`/etc/systemd/system/`). The service will be configured to run the Duck web server with the specified settings.

### `start`

Starts the Duck service.

**Usage:**  

```bash
duck service start
```

This command starts the Duck service by invoking `systemctl start`. The Duck web server will begin running with the specified configuration.

### `stop`

Stops the Duck service.

**Usage:**  

```bash
duck service stop
```

This command stops the Duck service using `systemctl stop`. If the service is currently running, it will be terminated.

### `enable`

Enables the Duck service to start on boot.

**Usage:**  

```bash
duck service enable
```

This command enables the Duck service to automatically start when the system boots, using `systemctl enable`.

### `disable`

Disables the Duck service from starting on boot.

**Usage:**  

```bash
duck service disable
```

This command disables the Duck service from starting on boot using `systemctl disable`.

### `status`

Checks the status of the Duck service and prints detailed information.

**Usage:**  

```bash
duck service status
```

This command retrieves the current status of the Duck service using `systemctl status` and prints relevant details like the service's state (active/running), the PID, and how long the service has been running. It also shows the last few log lines from the service.

### `reload-systemd`

Reloads systemd to apply new or modified services.

**Usage:**  

```bash
duck service reload-systemd
```

This command reloads `systemd` to apply any changes made to the service configuration.
