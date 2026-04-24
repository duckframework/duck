# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

---

## [Unreleased]

### Added
- Functions `static_filepath` & `media_filepath` from `duck.shortcuts` module.
- Added argument `absolute` to functions `media` & `static` from `duck.shortcuts` module.

### Changed
- Refactored functions `static` and `media` to support external URLs. Supported only internal URL's before.
- Refined AI guidelines in [ai](./ai/) directory.

### Fixed
- Lively Navigation bug when trying to navigate from a URL with a fragment e.g. https://duckframework.com#something -> any internal URL.

---

## [1.0.2]

### Added
- Minor features

### Changed
- Refactored some parts of the codebase

### Fixed
- Some minor bugs
