# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Added `is_valid_host` to the `duck.utils.net` module.
- Added two built-in template tags and one filter: `smart_truncate`, `expand_exception`, and `to_spaced_camel_case`.
  - `smart_truncate` and `to_spaced_camel_case` are powered by utilities from the `duck.utils.string` module.
- Added improved default blueprint scaffolding:
  - New blueprints now include a `ui/` directory by default.
  - `views.py` is now generated automatically.
  - Blueprints can now automatically resolve static assets from `ui/static/`.
  - Blueprints can now automatically resolve templates from `ui/templates/`.
- Added a built-in Dashboard blueprint for monitoring and managing Duck applications, including request metrics, response statistics, latency tracking, error reporting, route inspection, logs, and real-time server state monitoring.
- Added support for log handlers in the `duck.logging.handler` module, allowing custom actions and integrations to be triggered whenever log messages are emitted.
- Added a built-in Dashboard accessible through the `/dashboard` route, providing visibility into requests, responses, errors, logs, routes, performance metrics, and other server diagnostics.
- Added support for the `ENABLE_DASHBOARD` setting, allowing the Dashboard to be enabled or disabled without requiring manual blueprint registration.
- Added `DASHBOARD_USERNAME` and `DASHBOARD_PWD` settings for securing Dashboard access during development and debugging.

### Changed

- Renamed `duck.etc.apps` to `duck.etc.blueprints` to better reflect its purpose and usage.
- Renamed the built-in blueprint `duck.etc.apps.defaultsite.blueprint.Ducksite` to `duck.etc.blueprints.welcome.blueprint.Welcome`.
- Removed `simple_response` from `duck.contrib.responses`.
- Renamed `template_response` to `make_response` for improved clarity and consistency.
- Added an asynchronous equivalent, `async_make_response`.
- Refined middleware implementations and improved middleware debugging messages.
- Improved and modernized Duck's default pages and error pages with a cleaner, more polished user interface.
- Simplified and reduced complexity within `duck.contrib.responses.errors`.

### Fixed

- Fixed various issues related to blueprint generation and resource discovery.
- Fixed inconsistencies in default blueprint structure and asset resolution.
- Fixed middlewares' `process_response` not running on error response - middleware `process_response` now being executed everytime.

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
