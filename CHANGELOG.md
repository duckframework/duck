# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Added the `UnsupportedBrowserBanner` component to the `duck.html.components.unsupported_browser` module.
- Added the `glacier` variant to the `Snackbar` component, providing a modern frosted-glass appearance.

### Changed

- Updated the `Snackbar` and `Progress` components to support dynamic color updates after initialization.
- Updated `lively.js` and `lively.min.js` to support the new page progress bar and snackbar behavior.
- Simplified the `Page` component implementation.
- Refined Lively's WebSocket connection notifications to display only meaningful status changes, removing the initial **"Connected"** toast.

### Fixed

- Fixed several issues related to snackbar state synchronization and dynamic updates.

---

## [2.1.0] - June 20, 2026

### Added

- Added `is_valid_host` to the `duck.utils.net` module.
- Added two built-in template tags and one filter:
  - `smart_truncate`
  - `expand_exception`
  - `to_spaced_camel_case`
  `smart_truncate` and `to_spaced_camel_case` are powered by utilities from the `duck.utils.string` module.

- Improved default blueprint scaffolding:
  - New blueprints now include a `ui/` directory by default.
  - `views.py` is generated automatically.
  - Static assets are automatically discovered from `ui/static/`.
  - Templates are automatically discovered from `ui/templates/`.

- Added a built-in Dashboard blueprint for monitoring and managing Duck applications, including:
  - Request and response metrics
  - Latency tracking
  - Error reporting
  - Route inspection
  - Log monitoring
  - Real-time server state monitoring
  
- Added support for log handlers in the `duck.logging.handler` module, enabling custom integrations and actions to be executed whenever log messages are emitted.
- Added a built-in Dashboard accessible via the `/dashboard` route, providing visibility into:
  - Requests and responses
  - Errors and exceptions
  - Logs and routes
  - Performance metrics
  - Server diagnostics
  
- Added support for the `ENABLE_DASHBOARD` setting, allowing the Dashboard to be enabled or disabled without manual blueprint registration.
- Added `DASHBOARD_USERNAME` and `DASHBOARD_PWD` settings for securing Dashboard access during development and debugging.
- Added `get_user_id` to `duck.contrib.auth` for efficiently retrieving the authenticated user's ID from supported authentication backends such as `jwt` and `session`, avoiding the overhead of loading the full user object when only the identifier is required.
- Added the `duck.security` package for security-related utilities.
- Added a `user_id` argument to `duck.contrib.auth.login` and `duck.contrib.auth.async_login`, enabling fast authentication when the user ID is already known.
- Added a `force_reparent` argument to `InnerHtmlComponent.add_child` and `InnerHtmlComponent.add_children` that automatically detaches a component from any existing parent and component tree before reattaching it. This is useful when reusing components that were temporarily attached elsewhere during construction.
- Added `remove_ansi_escape_codes_str` to the `duck.utils.ansi` module.
- Added the `duck.security.passwords` module for password strength validation and security checks.

### Changed

- Renamed `duck.etc.apps` to `duck.etc.blueprints` to better reflect its purpose.
- Renamed the built-in blueprint:
  
  ```python
  duck.etc.apps.defaultsite.blueprint.Ducksite
  ```
  
  to:
  
  ```python
  duck.etc.blueprints.welcome.blueprint.Welcome
  ```

- Removed `simple_response` from `duck.contrib.responses`.
- Renamed `template_response` to `make_response` for improved clarity and consistency.
- Added `async_make_response` as the asynchronous equivalent of `make_response`.
- Refined middleware implementations and improved middleware debugging messages.
- Modernized Duck's default pages and error pages with a cleaner, more polished user experience.
- Simplified and reduced complexity within `duck.contrib.responses.errors`.
- Dashboard functionality is now only enabled when securely configured.
- Moved the `duck.ansi` module to `duck.utils.ansi`.
- Added `https://fonts.googleapis.com` and `https://fonts.gstatic.com` to the default Content Security Policy (CSP) rules.
- `duck.utils.fileio.FileIOStream` now caches read and write operations to improve performance during repeated access.

### Fixed

- Fixed various issues related to blueprint generation and resource discovery.
- Fixed inconsistencies in default blueprint structure and automatic asset resolution.
- Fixed middleware `process_response` hooks not executing for error responses. `process_response` is now always executed whenever a request object is available.
- Fixed `InnerHtmlComponent.add_children` to iterate over a copy of the provided children collection, preventing issues caused by mutations during iteration.
- Fixed several subtle bugs in `duck.utils.xsocket`.
- Fixed an issue with the `duck collectstatic` command.

---

## [2.0.0] - June 8, 2026

### Added

- Added `static_filepath` and `media_filepath` helpers to the `duck.shortcuts` module.
- Added an `absolute` argument to the `media` and `static` shortcut functions.
- Added a `log_results` argument to the `exec_time` and `async_exec_time` decorators in `duck.utils.performance`.
- Added support for `selected` and `value` keyword arguments to the `Option` HTML/Lively component and improved the `Select` component.
- Added `update_now()` to `LivelyWebsocketView`, allowing immediate synchronization of component state with the client during event execution.
- Added automatic session persistence for Lively events when session data is modified.
- Added the `set_meta()` method to the `Page` component.
- Added the `csrf_exempt` decorator to `duck.views`.
- Introduced a cleaner application architecture where all applications inherit from `duck.app.base.BaseApp`.
- Added a `server_url` argument to `BaseApp` for improved reverse-proxy and deployment support.
- Added support for application events through the `events` argument on core applications from `duck.apps`.
- Added first-class JWT support, modeled after Duck's session system. JWT payloads can now be accessed and modified directly using syntax such as:

  ```python
  request.JWT["key"] = value
  ```

- Added authentication utilities to `duck.contrib.auth`:
  - `authenticate`
  - `login`
  - `logout`
  - `get_user_from_session`
  - `get_user_from_jwt`
- Added `JWTMiddleware` to Duck's default middleware stack.
- Added encrypted cache support through `duck.utils.caching.encrypted`.

### Changed

- Refactored the `static` and `media` helpers to support external URLs in addition to internal assets.
- Refined AI guidelines in the [`ai/`](./ai/) directory.
- Made `duck.http.middlewares.contrib.WWWRedirectMiddleware` optional and removed it from the default middleware configuration.
- Renamed `SessionStore.create()` to `assign_new_session_key()` for improved clarity.
- Made request sessions lazily loaded on first access or modification.
- Renamed `_extract_and_process_request_data()` to `_set_request_fields()`.
- Renamed `duck.utils.port_recorder` to `duck.utils.port_registry` and fully refactored its internals.
- Improved and refined the `ssl-gen` command.
- Improved `SessionStorageConnector` shutdown performance by executing storage cleanup operations in background threads.
- Improved and refined the `duck.app.microapp` module.
- Renamed the `FORCE_HTTPS` setting to `HTTPS_REDIRECT`.
- Improved the `App` API and internal application lifecycle.
- Removed default self-signed certificate generation settings; certificate generation is now entirely optional.
- Reduced the default `DJANGO_SERVER_WAIT_TIME` to 1 second.
- Improved how Lively synchronizes SESSION, JWT, and other server-side state after mutations. Synchronization now uses a secure server-issued flow that updates credentials through a protected `fetch()` request while preserving support for `HttpOnly` cookies.
- Improved session storage security.

### Fixed

- Fixed a Lively navigation issue when navigating from URLs containing fragments (e.g. `https://duckframework.com#section`) to internal routes.

---

## [1.0.2] - March 6, 2026

### Added

- Added minor features and quality-of-life improvements.

### Changed

- Refactored various parts of the codebase to improve maintainability.

### Fixed

- Fixed several minor bugs and stability issues.
