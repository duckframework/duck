# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

---

## [Unreleased]

### Added

- Functions `static_filepath` & `media_filepath` from `duck.shortcuts` module.
- Added argument `absolute` to functions `media` & `static` from `duck.shortcuts` module.
- Added argument `log_results` to decorators `exec_time` & `async_exec_time` of `duck.utils.performance` module.
- Added support for keyword arguments `selected` & `value` to `Option` HTML/Lively component and improved the `Select` component as well.
- Added a method `update_now` to `LivelyWebsocketView` for syncing the current state of an HTML/Lively component with the client. It behaves more like `ForceUpdate` and can be used in the middle of component event event handler.
- Added session persistence for Lively events: sessions are now automatically saved when modified within a Lively event handler.
- Added method `set_meta` to Page component.
- Added `csrf_exempt` decorator in `duck.views` module.
- Added clean app structure - All app instances now inherit from `duck.app.base.BaseApp`
- Added `server_url` argument to `BaseApp` to better support reverse proxies and deployment setups where the application instance is not accessed directly.

### Changed

- Refactored functions `static` and `media` to support external URLs. Supported only internal URL's before.
- Refined AI guidelines in [ai](./ai/) directory.
- Made the middleware `duck.http.middlewares.contrib.WWWRedirectMiddleware` optional, it's no longer included in MIDDLEWARES by default.
- Changed `create()` method of `SessionStore` to a clearer name `assign_new_session_key`.
- Made request sessions to be lazily loaded upon access or modification.
- Improved Request object and changed method `_extract_and_process_request_data` to a clearer name `_set_request_fields`
- Removed the requirement for `ENABLE_HTTPS` to be enabled when `FORCE_HTTPS` is set.
- Renamed module `duck.utils.port_recorder` to `duck.utils.port_registry`, including a full refactor of its internal APIs and contents to better reflect its responsibility as a centralized port management registry.
- Improved and refined `ssl-gen` command.
- Improved `SessionStorageConnector` shutdown behavior by offloading close() operations to background threads, allowing the main application to exit faster without blocking on storage cleanup tasks.
- Improved and refined `duck.app.microapp` module.
- Renamed setting `FORCE_HTTPS` to `HTTPS_REDIRECT` for clearer intent and improved consistency with its actual behavior of redirecting HTTP traffic to HTTPS.
- Improved `App` class to use better arguments, also improved the core App logic.

### Fixed

- Lively Navigation bug when trying to navigate from a URL with a fragment e.g. https://duckframework.com#something -> any internal URL.

---

## [1.0.2] - March 6, 2026

### Added
- Minor features

### Changed
- Refactored some parts of the codebase

### Fixed
- Some minor bugs
