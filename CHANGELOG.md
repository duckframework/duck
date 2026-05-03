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
- Added a method `update_now` to `LivelyWebsocketView` for syncing the current state of an HTML/Lively component with the client. 
  It behaves more like `ForceUpdate` and can be used in the middle of component event event handler.
- Added session persistence for Lively events: sessions are now automatically saved when modified within a Lively event handler.

### Changed
- Refactored functions `static` and `media` to support external URLs. Supported only internal URL's before.
- Refined AI guidelines in [ai](./ai/) directory.
- Made the middleware `duck.http.middlewares.contrib.WWWRedirectMiddleware` optional, it's no longer included in MIDDLEWARES by default.

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
