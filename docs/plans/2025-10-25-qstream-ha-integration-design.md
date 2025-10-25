# QStream Home Assistant Integration - Design Document

**Date:** 2025-10-25
**Status:** Approved
**Version:** 1.0

## Overview

Home Assistant custom integration for BUVA QStream 2.0 WiFi-enabled ventilation fans. Provides native HA control through fan entity, demand control switch, and diagnostic sensors. Designed for HACS distribution with local installation support.

## Requirements

### Functional Requirements
- Control fan speed via percentage (0-100%) and preset modes (Low/Medium/High/Turbo)
- Toggle demand control (automatic speed adjustment based on AQI sensor)
- Monitor air quality index from device sensor
- Display diagnostic information (flow rates, timer status, schedule state, valve position)
- Configure devices through HA UI (config flow)

### Non-Functional Requirements
- HACS-compatible repository structure
- Support manual installation to custom_components
- Depend on qstream PyPI package (clean separation)
- 30-second polling interval for device state
- Graceful handling of network errors and device unavailability

### Out of Scope
- HA Core integration (future consideration)
- Device discovery (devices don't support mDNS/SSDP)
- Schedule management (read-only schedule state)
- Firmware updates

## Architecture

### Repository Structure

```
qstream-ha/
├── custom_components/
│   └── qstream/
│       ├── __init__.py          # Integration setup & coordinator
│       ├── manifest.json        # HA integration metadata
│       ├── config_flow.py       # UI configuration flow
│       ├── fan.py               # Fan entity platform
│       ├── switch.py            # Demand control switch platform
│       ├── sensor.py            # Diagnostic sensor platform
│       ├── const.py             # Constants and mappings
│       └── strings.json         # UI translations
├── tests/
│   ├── test_config_flow.py
│   ├── test_coordinator.py
│   ├── test_fan.py
│   ├── test_switch.py
│   └── test_sensor.py
├── .github/
│   └── workflows/
│       └── validate.yml         # CI for linting and tests
├── docs/
│   └── plans/
├── hacs.json                    # HACS metadata
├── README.md                    # User documentation
├── pyproject.toml               # Development dependencies
├── .gitignore
└── LICENSE
```

### Dependency Management

**Runtime Dependencies (manifest.json):**
- `qstream>=0.1.0` (installed by HA from PyPI)

**Development Dependencies (pyproject.toml):**
- `homeassistant` - Type stubs and testing framework
- `pytest` + `pytest-homeassistant-custom-component` - Testing
- `ruff` - Linting
- `mypy` - Type checking

**Key Decision:** Integration depends on published qstream PyPI package rather than bundling library code. This ensures clean separation, proper versioning, and easier maintenance.

## Component Design

### 1. Configuration Flow

**File:** `config_flow.py`

**User Flow:**
1. User adds integration via HA UI
2. Form requests: host (IP/hostname), optional name
3. Validation: Attempt connection using `QStreamClient.get_status()`
4. Success: Create config entry with unique_id based on host
5. Failure: Show appropriate error message

**Config Entry Data:**
```python
{
    "host": "192.168.1.100",
    "name": "Bathroom Fan"  # Optional friendly name
}
```

**Reconfiguration:**
- Options flow allows changing host and name
- No authentication required (device has no auth)

**No Discovery:**
- Devices don't advertise via mDNS/SSDP
- Manual host entry is simple and sufficient
- Can add discovery later if firmware supports it

### 2. Data Coordinator

**File:** `__init__.py`

**QStreamDataUpdateCoordinator:**

**Purpose:** Centralized device polling and state management

**Behavior:**
- Polls device every 30 seconds using `client.get_status()`
- Shares single `QStreamClient` instance (uses HA's shared aiohttp session)
- Distributes data to all entities (fan, switch, sensors)
- Handles errors gracefully (marks entities unavailable, retries automatically)

**Update Interval:**
- Default: 30 seconds
- Rationale: Balance between responsiveness and network load
- Device state doesn't change rapidly enough to warrant faster polling

**Error Handling:**
- `QStreamConnectionError`: Log warning, mark unavailable, keep retrying
- `QStreamTimeoutError`: Same as connection error
- `QStreamResponseError`: Log error with raw response for debugging

**Integration Lifecycle:**

```python
async def async_setup_entry(hass, entry):
    # Use HA's shared aiohttp session
    session = async_get_clientsession(hass)

    # Create client for device
    client = QStreamClient(entry.data["host"], session=session)

    # Create coordinator
    coordinator = QStreamDataUpdateCoordinator(
        hass, client, update_interval=timedelta(seconds=30)
    )

    # Initial refresh
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["fan", "switch", "sensor"]
    )
```

### 3. Fan Entity

**File:** `fan.py`

**QStreamFan Entity (extends `FanEntity`):**

**Supported Features:**
- `FanEntityFeature.SET_SPEED` - Percentage control (0-100%)
- `FanEntityFeature.PRESET_MODE` - Named presets for device levels
- `FanEntityFeature.TURN_ON` / `TURN_OFF` - Basic control

**Preset Modes:**

Preset modes map to device levels 1-4, which are user-configurable on the device:

```python
PRESET_MODE_LOW = "Low"       # Device level 1
PRESET_MODE_MEDIUM = "Medium" # Device level 2
PRESET_MODE_HIGH = "High"     # Device level 3
PRESET_MODE_TURBO = "Turbo"   # Device level 4
```

**Initialization:**
- Query all device levels (1-4) on startup via `client.get_level(index)`
- Cache level percentages for preset mode mapping
- Example: Level 2 might be 55%, so "Medium" preset = 55%

**State Properties:**

```python
@property
def is_on(self) -> bool:
    return self.coordinator.data.actual_flow > 0

@property
def percentage(self) -> int:
    return self.coordinator.data.actual_flow

@property
def preset_mode(self) -> str | None:
    # Match current flow to cached device levels
    # Return closest preset or None if manual percentage
```

**Control Methods:**

```python
async def turn_on(self, percentage=None, preset_mode=None, **kwargs):
    """Turn on fan with speed or preset."""
    current_demand = self.coordinator.data.demand_control_enabled

    if preset_mode:
        # Use cached device level percentage
        percentage = self._preset_percentages[preset_mode]
    elif percentage is None:
        # Default to 50% or last known speed
        percentage = 50

    # Set timer with 4-hour duration for "manual" control
    await self.coordinator.client.set_timer(
        duration_minutes=240,
        speed_percentage=percentage,
        demand_control=current_demand
    )
    await self.coordinator.async_request_refresh()

async def turn_off(self):
    """Turn off fan by canceling timer."""
    await self.coordinator.client.cancel_timer()
    await self.coordinator.async_request_refresh()

async def set_percentage(self, percentage: int):
    """Set exact speed percentage."""
    current_demand = self.coordinator.data.demand_control_enabled
    await self.coordinator.client.set_timer(
        duration_minutes=240,
        speed_percentage=percentage,
        demand_control=current_demand
    )
    await self.coordinator.async_request_refresh()

async def set_preset_mode(self, preset_mode: str):
    """Set fan to preset mode."""
    await self.turn_on(preset_mode=preset_mode)
```

**Timer Duration Strategy:**
- Use 240 minutes (4 hours) for manual control operations
- This ensures fan stays at set speed without timing out
- User can still set custom timers if needed (future service)

**Preset vs Percentage Behavior:**
- When both provided to `turn_on()`, preset takes precedence (standard HA)
- Percentage parameter ignored when preset specified
- HA UI shows separate controls (slider vs preset selector)

### 4. Switch Entity

**File:** `switch.py`

**QStreamDemandControlSwitch Entity (extends `SwitchEntity`):**

**Purpose:** Toggle demand control feature (automatic speed adjustment based on AQI)

**Entity ID:** `switch.qstream_fan_demand_control`

**State:**
```python
@property
def is_on(self) -> bool:
    return self.coordinator.data.demand_control_enabled
```

**Control Methods:**

```python
async def turn_on(self):
    """Enable demand control."""
    status = self.coordinator.data
    await self.coordinator.client.set_timer(
        duration_minutes=240,
        speed_percentage=status.set_flow,
        demand_control=True
    )
    await self.coordinator.async_request_refresh()

async def turn_off(self):
    """Disable demand control."""
    status = self.coordinator.data
    await self.coordinator.client.set_timer(
        duration_minutes=240,
        speed_percentage=status.set_flow,
        demand_control=False
    )
    await self.coordinator.async_request_refresh()
```

**Behavior:**
- Preserves current fan speed when toggling
- Uses same timer duration strategy as fan entity
- State updates automatically via coordinator polling

**Rationale for Switch Entity:**
- Most intuitive UI for binary setting
- Standard HA pattern for toggleable features
- More discoverable than custom service
- Allows easy automation (turn on/off in scenes, automations)

### 5. Sensor Entities

**File:** `sensor.py`

**Primary Sensor - Air Quality Index:**

```python
Entity ID: sensor.qstream_fan_air_quality
State Class: measurement
Device Class: aqi
Unit: AQI index
Value: await client.get_air_quality()
Update: Every coordinator refresh (30s)
```

**Diagnostic Sensors (Flow Rates):**

```python
sensor.qstream_fan_analog_flow
  - Description: Flow percentage demanded by analog sensor
  - Unit: %
  - Value: status.analog_flow

sensor.qstream_fan_set_flow
  - Description: Target flow percentage
  - Unit: %
  - Value: status.set_flow

sensor.qstream_fan_actual_flow
  - Description: Current actual flow percentage
  - Unit: %
  - Value: status.actual_flow
```

**Schedule Sensors:**

```python
sensor.qstream_fan_schedule_mode
  - Description: Current schedule mode
  - Options: DAY, NIGHT
  - Value: status.schedule_mode.value

sensor.qstream_fan_timer_remaining
  - Description: Timer remaining minutes
  - Unit: minutes
  - Value: status.timer_remaining_minutes
  - Enabled: Only when timer active
```

**Binary Sensors:**

```python
binary_sensor.qstream_fan_valve
  - Description: Valve position
  - Device Class: opening
  - Value: status.valve_open

binary_sensor.qstream_fan_timer_active
  - Description: Timer active state
  - Device Class: running
  - Value: status.timer_active

binary_sensor.qstream_fan_schedule_enabled
  - Description: Schedule enabled state
  - Device Class: running
  - Value: status.schedule_enabled
```

**Entity Categories:**
- All sensors except AQI should be marked as `diagnostic` (EntityCategory.DIAGNOSTIC)
- This groups them in a separate section in HA UI
- AQI is primary sensor, shown prominently

## HACS Distribution

### hacs.json

```json
{
  "name": "QStream Ventilation Fan",
  "render_readme": true,
  "domains": ["fan", "sensor", "switch"]
}
```

### manifest.json

```json
{
  "domain": "qstream",
  "name": "QStream Ventilation Fan",
  "codeowners": ["@bram"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/[username]/qstream-ha",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/[username]/qstream-ha/issues",
  "requirements": ["qstream>=0.1.0"],
  "version": "0.1.0"
}
```

**Key Fields:**
- `config_flow: true` - Enables UI configuration
- `iot_class: local_polling` - Describes communication pattern
- `requirements` - HA will install qstream from PyPI automatically

### Installation Methods

**Via HACS:**
1. Add custom repository URL in HACS
2. Search for "QStream Ventilation Fan"
3. Click Install
4. Restart Home Assistant
5. Add integration via Configuration → Integrations → Add Integration

**Manual Installation:**
1. Copy `custom_components/qstream/` to HA config directory
2. Restart Home Assistant
3. Add integration via Configuration → Integrations → Add Integration

### Prerequisites

**Before Distribution:**
1. Publish qstream library to PyPI (HA will auto-install it)
2. Create GitHub repository
3. Add proper README with installation instructions
4. Add LICENSE file (MIT)
5. Tag release (v0.1.0)

## Development Workflow

### Project Initialization

```bash
cd C:\Users\bram\src\qstream-ha
git init
uv init --no-package
uv add --dev homeassistant pytest pytest-homeassistant-custom-component ruff mypy
```

### Testing Strategy

**Unit Tests:**
- Mock `QStreamClient` responses using pytest fixtures
- Test coordinator update logic and error handling
- Test fan entity state calculations and control methods
- Test switch entity toggle behavior
- Test sensor state mapping from coordinator data
- Test config flow validation and error cases

**Integration Tests:**
- Mark with `@pytest.mark.integration`
- Require actual device on network or mock HTTP server
- Test full flow: config entry → coordinator setup → entity creation
- Test end-to-end control and state updates

**Local Testing:**
1. Create symlink: `[HA config]/custom_components/qstream` → `[repo]/custom_components/qstream`
2. Restart Home Assistant
3. Add integration via UI with local device IP
4. Test all entities, controls, and error scenarios
5. Check HA logs for errors

### CI/CD Pipeline

**GitHub Actions (.github/workflows/validate.yml):**

```yaml
- Validate manifest.json schema
- Validate hacs.json schema
- Run ruff linting
- Run mypy type checking
- Run pytest unit tests (skip integration tests in CI)
```

**Pre-commit Hooks:**
- Ruff formatting and linting
- Mypy type checking
- Prevent committing with TODOs

## Implementation Phases

### Phase 1: Repository Setup
- Initialize git repository
- Set up uv project with dev dependencies
- Create directory structure
- Add .gitignore, LICENSE, README skeleton

### Phase 2: Core Integration
- Implement `__init__.py` with coordinator
- Create `manifest.json` and `const.py`
- Implement config flow with validation

### Phase 3: Fan Entity
- Implement fan platform with percentage control
- Add preset mode support with device level querying
- Test fan controls (turn on/off, speed, presets)

### Phase 4: Switch & Sensors
- Implement demand control switch
- Create AQI sensor
- Add diagnostic sensors and binary sensors

### Phase 5: HACS Preparation
- Create hacs.json
- Write comprehensive README
- Add strings.json for translations
- Create GitHub repository and push

### Phase 6: Testing & Validation
- Write unit tests for all components
- Test local installation
- Validate HACS compatibility
- Test with actual device

## Risk Mitigation

**Risk:** qstream library not yet on PyPI
**Mitigation:** Publish qstream to PyPI before distributing HA integration

**Risk:** Device API changes in firmware updates
**Mitigation:** Document tested firmware version, add version detection in future

**Risk:** Network instability causing frequent unavailable states
**Mitigation:** Coordinator automatically retries, exponential backoff on errors

**Risk:** User confusion about demand control
**Mitigation:** Clear entity naming, descriptions in strings.json, README documentation

## Success Criteria

- [ ] Integration installs via HACS without errors
- [ ] Config flow completes successfully with valid device
- [ ] Fan entity shows correct state and responds to controls
- [ ] Preset modes map to device levels correctly
- [ ] Demand control switch toggles feature properly
- [ ] AQI sensor updates and displays in HA
- [ ] All diagnostic sensors show accurate data
- [ ] Integration handles device offline gracefully
- [ ] Code passes ruff linting and mypy type checking
- [ ] Unit tests achieve >80% coverage

## Future Enhancements

**Not in Scope for v1.0, Consider for Future:**

- Custom service for timer with specific duration/speed
- Schedule management (currently read-only)
- Device discovery via network scan
- Multiple device support in single config entry
- Device firmware version detection
- Historical AQI tracking and graphing
- Preset mode customization (user-defined names/speeds)
- Integration with HA Energy dashboard
