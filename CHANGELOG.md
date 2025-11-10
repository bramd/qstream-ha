# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-11-10

### Bug Fixes
- Fix failing test_init.py tests (#5)
  - Changed test_clear_timer_service_registered from YAML-based setup to proper config entry setup
  - Replaced MagicMock with MockConfigEntry in test_clear_timer_service_calls_cancel
  - Replaced MagicMock with MockConfigEntry in test_clear_timer_service_idempotent
  - All tests now properly use config entry-based setup

**Full Changelog**: https://github.com/bramd/qstream-ha/compare/v0.2.0...v0.2.1

## [0.2.0] - 2025-11-10

### Features
- Add clear_timer service to clear timer and return fan to base program (#4)
- Add Dutch (Nederlands) translation support (#3)
- Add release skill to repository for contributors

### Bug Fixes
- Unregister service when last entry removed
- Update hacs.json to current spec (remove unsupported keys)
- Correct coordinator failure test to check last_update_success
- Update coordinator tests to use async_refresh
- Enable custom integrations in pytest fixtures
- Configure pytest asyncio mode
- Add custom_components to Python path for tests

### Documentation
- Add QStream skills documentation
- Add services.yaml for clear_timer service
- Add brand assets creation and submission design
- Clarify skill documentation structure
- Add Dutch translation design
- Add release skill design

### CI/Build
- Bump actions/checkout from 4 to 5 (#1)
- Bump actions/setup-python from 5 to 6 (#2)
- Add Dependabot configuration
- Add HACS action validation workflow
- Add hassfest validation workflow

**Full Changelog**: https://github.com/bramd/qstream-ha/compare/v0.1.0...v0.2.0

## [0.1.0] - 2025-10-26

Initial release of QStream Home Assistant integration.
