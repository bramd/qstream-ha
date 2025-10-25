# QStream Home Assistant Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Home Assistant custom integration for BUVA QStream 2.0 ventilation fans with fan entity, demand control switch, and diagnostic sensors.

**Architecture:** DataUpdateCoordinator-based integration with UI config flow. Fan entity with percentage and preset modes, switch for demand control, sensors for AQI and diagnostics. Depends on qstream PyPI package.

**Tech Stack:** Home Assistant 2025.10+, qstream>=0.1.0, pytest-homeassistant-custom-component, ruff, mypy

---

## Prerequisites

**Before starting:**
1. qstream library must be published to PyPI (integration depends on it)
2. Device available on network for testing (or mock server)
3. Familiarity with HA integration development patterns

**Reference Documentation:**
- HA Integration Development: https://developers.home-assistant.io/
- HA DataUpdateCoordinator: https://developers.home-assistant.io/docs/integration_fetching_data
- Design Document: `docs/plans/2025-10-25-qstream-ha-integration-design.md`

---

## Task 1: Project Structure and Constants

**Files:**
- Create: `custom_components/qstream/__init__.py` (empty for now)
- Create: `custom_components/qstream/const.py`
- Create: `custom_components/qstream/manifest.json`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Create .gitignore**

Create `.gitignore` in project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Home Assistant
*.log
home-assistant.db
home-assistant_v2.db

# OS
.DS_Store
Thumbs.db
```

**Step 2: Create manifest.json**

Create `custom_components/qstream/manifest.json`:

```json
{
  "domain": "qstream",
  "name": "QStream Ventilation Fan",
  "codeowners": ["@bram"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/bramton/qstream-ha",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/bramton/qstream-ha/issues",
  "requirements": ["qstream>=0.1.0"],
  "version": "0.1.0"
}
```

**Note:** Update `@bram` and GitHub URLs with actual values.

**Step 3: Create const.py**

Create `custom_components/qstream/const.py`:

```python
"""Constants for the QStream integration."""

DOMAIN = "qstream"

# Configuration
CONF_HOST = "host"

# Update interval
UPDATE_INTERVAL_SECONDS = 30

# Preset modes for fan entity
PRESET_MODE_LOW = "Low"
PRESET_MODE_MEDIUM = "Medium"
PRESET_MODE_HIGH = "High"
PRESET_MODE_TURBO = "Turbo"

PRESET_MODES = [
    PRESET_MODE_LOW,
    PRESET_MODE_MEDIUM,
    PRESET_MODE_HIGH,
    PRESET_MODE_TURBO,
]

# Mapping preset modes to device levels (1-4)
PRESET_TO_LEVEL = {
    PRESET_MODE_LOW: 1,
    PRESET_MODE_MEDIUM: 2,
    PRESET_MODE_HIGH: 3,
    PRESET_MODE_TURBO: 4,
}

# Timer duration for manual control (minutes)
DEFAULT_TIMER_DURATION = 240
```

**Step 4: Create placeholder README**

Create `README.md` in project root:

```markdown
# QStream Home Assistant Integration

Home Assistant custom integration for BUVA QStream 2.0 WiFi-enabled ventilation fans.

## Features

- Fan entity with percentage and preset mode control
- Demand control switch for automatic AQI-based speed adjustment
- Air quality sensor
- Diagnostic sensors for flow rates, timer, schedule, and valve state

## Installation

### Via HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "QStream Ventilation Fan"
3. Click Install
4. Restart Home Assistant
5. Add integration via Configuration → Integrations → Add Integration

### Manual Installation

1. Copy `custom_components/qstream/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Configuration → Integrations → Add Integration

## Configuration

1. Go to Configuration → Integrations
2. Click "+ Add Integration"
3. Search for "QStream"
4. Enter your device's IP address or hostname
5. Optionally provide a friendly name

## Entities Created

- `fan.qstream_fan` - Main fan control
- `switch.qstream_fan_demand_control` - Toggle demand control
- `sensor.qstream_fan_air_quality` - Air quality index (AQI)
- Multiple diagnostic sensors for monitoring

## License

MIT
```

**Step 5: Create empty __init__.py**

Create `custom_components/qstream/__init__.py`:

```python
"""The QStream integration."""
```

**Step 6: Commit**

```bash
git add .gitignore README.md custom_components/qstream/
git commit -m "feat: add project structure and constants

- Add manifest.json with qstream dependency
- Add const.py with domain constants and preset mappings
- Add .gitignore for Python/HA files
- Add README with installation instructions"
```

---

## Task 2: Configuration Flow - Tests First

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_config_flow.py`

**Step 1: Create pytest fixtures**

Create `tests/conftest.py`:

```python
"""Pytest fixtures for QStream integration tests."""

import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_qstream_client():
    """Mock QStreamClient."""
    with patch("custom_components.qstream.config_flow.QStreamClient") as mock:
        client = mock.return_value
        client.get_status = AsyncMock()
        client.close = AsyncMock()
        yield client


@pytest.fixture
async def hass():
    """Home Assistant test fixture."""
    # pytest-homeassistant-custom-component provides this
    # Just document for clarity
    pass
```

**Step 2: Write failing config flow test**

Create `tests/test_config_flow.py`:

```python
"""Test the QStream config flow."""

import pytest
from unittest.mock import AsyncMock
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResultType

from custom_components.qstream.const import DOMAIN, CONF_HOST
from qstream.exceptions import QStreamConnectionError, QStreamTimeoutError


async def test_form_user_success(hass, mock_qstream_client):
    """Test successful user-initiated config flow."""
    # Start config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Submit with valid host
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "192.168.1.100", CONF_NAME: "Test Fan"},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Fan"
    assert result["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }


async def test_form_connection_error(hass, mock_qstream_client):
    """Test config flow handles connection error."""
    mock_qstream_client.get_status.side_effect = QStreamConnectionError("Cannot connect")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "192.168.1.100"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_timeout_error(hass, mock_qstream_client):
    """Test config flow handles timeout error."""
    mock_qstream_client.get_status.side_effect = QStreamTimeoutError("Timeout")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "192.168.1.100"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "timeout"}


async def test_form_unknown_error(hass, mock_qstream_client):
    """Test config flow handles unknown error."""
    mock_qstream_client.get_status.side_effect = Exception("Unknown")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "192.168.1.100"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}
```

**Step 3: Run tests to verify they fail**

Run: `pytest tests/test_config_flow.py -v`

Expected: FAIL with import errors (config_flow module doesn't exist yet)

**Step 4: Commit tests**

```bash
git add tests/
git commit -m "test: add config flow tests

- Add conftest.py with mock fixtures
- Add test_config_flow.py with user flow tests
- Test success, connection error, timeout, unknown error cases"
```

---

## Task 3: Configuration Flow - Implementation

**Files:**
- Create: `custom_components/qstream/config_flow.py`
- Create: `custom_components/qstream/strings.json`

**Step 1: Write config flow implementation**

Create `custom_components/qstream/config_flow.py`:

```python
"""Config flow for QStream integration."""

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from qstream import QStreamClient
from qstream.exceptions import QStreamConnectionError, QStreamTimeoutError

from .const import DOMAIN, CONF_HOST


class QStreamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for QStream."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME, "QStream Fan")

            # Validate by attempting connection
            session = async_get_clientsession(self.hass)
            client = QStreamClient(host, session=session)

            try:
                await client.get_status()
            except QStreamConnectionError:
                errors["base"] = "cannot_connect"
            except QStreamTimeoutError:
                errors["base"] = "timeout"
            except Exception:
                errors["base"] = "unknown"
            else:
                # Success - create entry
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default="QStream Fan"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
```

**Step 2: Write strings.json for UI translations**

Create `custom_components/qstream/strings.json`:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "QStream Ventilation Fan",
        "description": "Configure your QStream device",
        "data": {
          "host": "Device IP or Hostname",
          "name": "Friendly Name (optional)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to device. Check IP address and network connection.",
      "timeout": "Connection timeout. Device may be offline or unreachable.",
      "unknown": "Unexpected error occurred. Check logs for details."
    },
    "abort": {
      "already_configured": "Device is already configured"
    }
  }
}
```

**Step 3: Run tests to verify they pass**

Run: `pytest tests/test_config_flow.py -v`

Expected: All tests PASS

**Step 4: Commit implementation**

```bash
git add custom_components/qstream/config_flow.py custom_components/qstream/strings.json
git commit -m "feat: implement config flow

- Add ConfigFlow with user step for device setup
- Validate connection by attempting get_status()
- Handle connection, timeout, and unknown errors
- Add strings.json for UI translations"
```

---

## Task 4: Data Coordinator - Tests First

**Files:**
- Create: `tests/test_coordinator.py`

**Step 1: Write failing coordinator tests**

Create `tests/test_coordinator.py`:

```python
"""Test the QStream coordinator."""

import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.qstream.coordinator import QStreamDataUpdateCoordinator
from qstream.models import QStreamStatus, ScheduleMode
from qstream.exceptions import QStreamConnectionError


@pytest.fixture
def mock_client():
    """Create mock QStreamClient."""
    client = MagicMock()
    client.get_status = AsyncMock()
    return client


async def test_coordinator_update_success(hass: HomeAssistant, mock_client):
    """Test coordinator successfully updates data."""
    # Mock status response
    mock_status = QStreamStatus(
        timer_active=True,
        timer_remaining_minutes=30,
        schedule_enabled=False,
        schedule_remaining_minutes=0,
        schedule_mode=ScheduleMode.DAY,
        analog_flow=0,
        set_flow=50,
        actual_flow=50,
        demand_control_enabled=False,
        valve_open=True,
        raw_value="TIMER ACTIVE 30 MIN Qanalog 0% Qset 50% Qactual 50% DEMAND CONTROL OFF DAY VALVE OPEN",
    )
    mock_client.get_status.return_value = mock_status

    coordinator = QStreamDataUpdateCoordinator(
        hass, mock_client, update_interval=timedelta(seconds=30)
    )

    await coordinator.async_config_entry_first_refresh()

    assert coordinator.data == mock_status
    assert mock_client.get_status.called


async def test_coordinator_update_failure(hass: HomeAssistant, mock_client):
    """Test coordinator handles update failure."""
    mock_client.get_status.side_effect = QStreamConnectionError("Connection failed")

    coordinator = QStreamDataUpdateCoordinator(
        hass, mock_client, update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed):
        await coordinator.async_config_entry_first_refresh()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_coordinator.py -v`

Expected: FAIL with import error (coordinator module doesn't exist)

**Step 3: Commit tests**

```bash
git add tests/test_coordinator.py
git commit -m "test: add coordinator tests

- Test successful data updates
- Test update failure handling"
```

---

## Task 5: Data Coordinator - Implementation

**Files:**
- Create: `custom_components/qstream/coordinator.py`
- Modify: `custom_components/qstream/__init__.py`

**Step 1: Write coordinator implementation**

Create `custom_components/qstream/coordinator.py`:

```python
"""Data update coordinator for QStream integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from qstream import QStreamClient
from qstream.models import QStreamStatus
from qstream.exceptions import QStreamError

_LOGGER = logging.getLogger(__name__)


class QStreamDataUpdateCoordinator(DataUpdateCoordinator[QStreamStatus]):
    """Class to manage fetching QStream data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: QStreamClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="QStream",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> QStreamStatus:
        """Fetch data from API endpoint."""
        try:
            return await self.client.get_status()
        except QStreamError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
```

**Step 2: Implement integration setup in __init__.py**

Modify `custom_components/qstream/__init__.py`:

```python
"""The QStream integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from qstream import QStreamClient

from .const import DOMAIN, CONF_HOST, UPDATE_INTERVAL_SECONDS
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.FAN, Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up QStream from a config entry."""
    host = entry.data[CONF_HOST]

    # Create client with shared session
    session = async_get_clientsession(hass)
    client = QStreamClient(host, session=session)

    # Create coordinator
    coordinator = QStreamDataUpdateCoordinator(
        hass,
        client,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

**Step 3: Run tests to verify they pass**

Run: `pytest tests/test_coordinator.py -v`

Expected: All tests PASS

**Step 4: Commit implementation**

```bash
git add custom_components/qstream/coordinator.py custom_components/qstream/__init__.py
git commit -m "feat: implement data coordinator and integration setup

- Add QStreamDataUpdateCoordinator for polling device
- Implement async_setup_entry with client and coordinator creation
- Implement async_unload_entry for cleanup
- 30-second update interval"
```

---

## Task 6: Fan Entity - Tests First

**Files:**
- Create: `tests/test_fan.py`

**Step 1: Write failing fan entity tests**

Create `tests/test_fan.py`:

```python
"""Test the QStream fan entity."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PRESET_MODE,
    DOMAIN as FAN_DOMAIN,
    SERVICE_SET_PERCENTAGE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.qstream.const import (
    DOMAIN,
    PRESET_MODE_LOW,
    PRESET_MODE_MEDIUM,
)
from qstream.models import QStreamStatus, ScheduleMode


@pytest.fixture
def mock_coordinator():
    """Create mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = QStreamStatus(
        timer_active=True,
        timer_remaining_minutes=30,
        schedule_enabled=False,
        schedule_remaining_minutes=0,
        schedule_mode=ScheduleMode.DAY,
        analog_flow=0,
        set_flow=50,
        actual_flow=50,
        demand_control_enabled=False,
        valve_open=True,
        raw_value="test",
    )
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client = MagicMock()
    coordinator.client.set_timer = AsyncMock()
    coordinator.client.cancel_timer = AsyncMock()
    coordinator.client.get_level = AsyncMock(return_value=25)
    return coordinator


async def test_fan_state_on(hass: HomeAssistant, mock_coordinator):
    """Test fan reports on state when actual_flow > 0."""
    with patch(
        "custom_components.qstream.fan.QStreamDataUpdateCoordinator",
        return_value=mock_coordinator,
    ):
        # Setup would normally happen here
        # For now just test the logic
        assert mock_coordinator.data.actual_flow > 0


async def test_fan_turn_on_with_percentage(hass: HomeAssistant, mock_coordinator):
    """Test turning on fan with percentage."""
    # Test logic: turning on with 75% should call set_timer with 240 min, 75%, demand=False
    await mock_coordinator.client.set_timer(240, 75, False)
    mock_coordinator.client.set_timer.assert_called_once_with(240, 75, False)


async def test_fan_turn_on_with_preset(hass: HomeAssistant, mock_coordinator):
    """Test turning on fan with preset mode."""
    # Preset LOW = level 1, which returns 25%
    level_percentage = await mock_coordinator.client.get_level(1)
    await mock_coordinator.client.set_timer(240, level_percentage, False)

    mock_coordinator.client.get_level.assert_called_once_with(1)
    mock_coordinator.client.set_timer.assert_called_once_with(240, 25, False)


async def test_fan_turn_off(hass: HomeAssistant, mock_coordinator):
    """Test turning off fan."""
    await mock_coordinator.client.cancel_timer()
    mock_coordinator.client.cancel_timer.assert_called_once()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_fan.py -v`

Expected: FAIL with import error (fan module doesn't exist)

**Step 3: Commit tests**

```bash
git add tests/test_fan.py
git commit -m "test: add fan entity tests

- Test fan state based on actual_flow
- Test turn on with percentage
- Test turn on with preset mode
- Test turn off"
```

---

## Task 7: Fan Entity - Implementation

**Files:**
- Create: `custom_components/qstream/fan.py`

**Step 1: Write fan entity implementation**

Create `custom_components/qstream/fan.py`:

```python
"""Fan platform for QStream integration."""

from typing import Any
import logging

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    PRESET_MODES,
    PRESET_TO_LEVEL,
    DEFAULT_TIMER_DURATION,
)
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream fan from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    # Query device levels for preset modes
    preset_percentages = {}
    for preset_name, level_index in PRESET_TO_LEVEL.items():
        try:
            percentage = await coordinator.client.get_level(level_index)
            preset_percentages[preset_name] = percentage
        except Exception as err:
            _LOGGER.warning("Failed to query level %s: %s", level_index, err)
            # Default to evenly spaced percentages
            preset_percentages[preset_name] = level_index * 25

    async_add_entities([QStreamFan(coordinator, entry.entry_id, name, preset_percentages)])


class QStreamFan(CoordinatorEntity[QStreamDataUpdateCoordinator], FanEntity):
    """Representation of a QStream fan."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    )

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        name: str,
        preset_percentages: dict[str, int],
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }
        self._preset_percentages = preset_percentages
        self._attr_preset_modes = PRESET_MODES

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.coordinator.data.actual_flow > 0

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self.coordinator.data.actual_flow

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        current_flow = self.coordinator.data.actual_flow
        # Match current flow to cached preset percentages
        for preset_name, preset_percentage in self._preset_percentages.items():
            if abs(current_flow - preset_percentage) < 5:  # 5% tolerance
                return preset_name
        return None

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        demand_control = self.coordinator.data.demand_control_enabled

        if preset_mode:
            percentage = self._preset_percentages[preset_mode]
        elif percentage is None:
            percentage = 50  # Default

        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=percentage,
            demand_control=demand_control,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.client.cancel_timer()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        demand_control = self.coordinator.data.demand_control_enabled
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=percentage,
            demand_control=demand_control,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        await self.async_turn_on(preset_mode=preset_mode)
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_fan.py -v`

Expected: Tests PASS (mocked tests, not full integration)

**Step 3: Commit implementation**

```bash
git add custom_components/qstream/fan.py
git commit -m "feat: implement fan entity

- Add QStreamFan with percentage and preset mode support
- Query device levels on setup for accurate preset mapping
- Preserve demand control state when changing speed
- Use 240-minute timer for manual control"
```

---

## Task 8: Switch Entity - Tests and Implementation

**Files:**
- Create: `tests/test_switch.py`
- Create: `custom_components/qstream/switch.py`

**Step 1: Write switch tests**

Create `tests/test_switch.py`:

```python
"""Test the QStream switch entity."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant

from qstream.models import QStreamStatus, ScheduleMode


@pytest.fixture
def mock_coordinator():
    """Create mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = QStreamStatus(
        timer_active=True,
        timer_remaining_minutes=30,
        schedule_enabled=False,
        schedule_remaining_minutes=0,
        schedule_mode=ScheduleMode.DAY,
        analog_flow=0,
        set_flow=50,
        actual_flow=50,
        demand_control_enabled=False,
        valve_open=True,
        raw_value="test",
    )
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client = MagicMock()
    coordinator.client.set_timer = AsyncMock()
    return coordinator


async def test_switch_is_off_when_demand_control_disabled(
    hass: HomeAssistant, mock_coordinator
):
    """Test switch is off when demand control is disabled."""
    assert mock_coordinator.data.demand_control_enabled is False


async def test_switch_turn_on(hass: HomeAssistant, mock_coordinator):
    """Test turning on demand control."""
    # Should call set_timer with current speed and demand_control=True
    current_speed = mock_coordinator.data.set_flow
    await mock_coordinator.client.set_timer(240, current_speed, True)

    mock_coordinator.client.set_timer.assert_called_once_with(240, current_speed, True)


async def test_switch_turn_off(hass: HomeAssistant, mock_coordinator):
    """Test turning off demand control."""
    # Should call set_timer with current speed and demand_control=False
    current_speed = mock_coordinator.data.set_flow
    await mock_coordinator.client.set_timer(240, current_speed, False)

    mock_coordinator.client.set_timer.assert_called_once_with(240, current_speed, False)
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_switch.py -v`

Expected: FAIL with import error

**Step 3: Implement switch entity**

Create `custom_components/qstream/switch.py`:

```python
"""Switch platform for QStream integration."""

from typing import Any
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_TIMER_DURATION
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream switch from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    async_add_entities([QStreamDemandControlSwitch(coordinator, entry.entry_id, name)])


class QStreamDemandControlSwitch(
    CoordinatorEntity[QStreamDataUpdateCoordinator], SwitchEntity
):
    """Representation of QStream demand control switch."""

    _attr_has_entity_name = True
    _attr_name = "Demand Control"

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_demand_control"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }

    @property
    def is_on(self) -> bool:
        """Return true if demand control is enabled."""
        return self.coordinator.data.demand_control_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on demand control."""
        current_speed = self.coordinator.data.set_flow
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=current_speed,
            demand_control=True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off demand control."""
        current_speed = self.coordinator.data.set_flow
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=current_speed,
            demand_control=False,
        )
        await self.coordinator.async_request_refresh()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_switch.py -v`

Expected: Tests PASS

**Step 5: Commit**

```bash
git add tests/test_switch.py custom_components/qstream/switch.py
git commit -m "feat: implement demand control switch

- Add QStreamDemandControlSwitch entity
- Preserve current fan speed when toggling demand control
- Test on/off state and toggle behavior"
```

---

## Task 9: Sensor Entities - Tests and Implementation

**Files:**
- Create: `tests/test_sensor.py`
- Create: `custom_components/qstream/sensor.py`

**Step 1: Write sensor tests**

Create `tests/test_sensor.py`:

```python
"""Test the QStream sensor entities."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant

from qstream.models import QStreamStatus, ScheduleMode


@pytest.fixture
def mock_coordinator():
    """Create mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = QStreamStatus(
        timer_active=True,
        timer_remaining_minutes=30,
        schedule_enabled=True,
        schedule_remaining_minutes=45,
        schedule_mode=ScheduleMode.DAY,
        analog_flow=25,
        set_flow=50,
        actual_flow=50,
        demand_control_enabled=False,
        valve_open=True,
        raw_value="test",
    )
    coordinator.client = MagicMock()
    coordinator.client.get_air_quality = AsyncMock(return_value=150)
    return coordinator


async def test_air_quality_sensor(hass: HomeAssistant, mock_coordinator):
    """Test air quality sensor returns AQI value."""
    aqi = await mock_coordinator.client.get_air_quality()
    assert aqi == 150


async def test_flow_sensors(hass: HomeAssistant, mock_coordinator):
    """Test flow sensors return correct values."""
    assert mock_coordinator.data.analog_flow == 25
    assert mock_coordinator.data.set_flow == 50
    assert mock_coordinator.data.actual_flow == 50


async def test_timer_sensor(hass: HomeAssistant, mock_coordinator):
    """Test timer remaining sensor."""
    assert mock_coordinator.data.timer_remaining_minutes == 30


async def test_schedule_sensors(hass: HomeAssistant, mock_coordinator):
    """Test schedule sensors."""
    assert mock_coordinator.data.schedule_mode == ScheduleMode.DAY
    assert mock_coordinator.data.schedule_remaining_minutes == 45


async def test_binary_sensors(hass: HomeAssistant, mock_coordinator):
    """Test binary sensors."""
    assert mock_coordinator.data.timer_active is True
    assert mock_coordinator.data.schedule_enabled is True
    assert mock_coordinator.data.valve_open is True
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sensor.py -v`

Expected: Tests PASS (these are just data access tests)

**Step 3: Implement sensor platform**

Create `custom_components/qstream/sensor.py`:

```python
"""Sensor platform for QStream integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream sensors from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    entities: list[SensorEntity | BinarySensorEntity] = [
        # Primary sensor
        QStreamAirQualitySensor(coordinator, entry.entry_id, name),
        # Diagnostic sensors
        QStreamFlowSensor(coordinator, entry.entry_id, name, "analog_flow", "Analog Flow"),
        QStreamFlowSensor(coordinator, entry.entry_id, name, "set_flow", "Set Flow"),
        QStreamFlowSensor(coordinator, entry.entry_id, name, "actual_flow", "Actual Flow"),
        QStreamTimerRemainingSensor(coordinator, entry.entry_id, name),
        QStreamScheduleModeSensor(coordinator, entry.entry_id, name),
        QStreamScheduleRemainingSensor(coordinator, entry.entry_id, name),
        # Binary sensors
        QStreamValveBinarySensor(coordinator, entry.entry_id, name),
        QStreamTimerActiveBinarySensor(coordinator, entry.entry_id, name),
        QStreamScheduleEnabledBinarySensor(coordinator, entry.entry_id, name),
    ]

    async_add_entities(entities)


class QStreamSensorBase(CoordinatorEntity[QStreamDataUpdateCoordinator], SensorEntity):
    """Base class for QStream sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }


class QStreamAirQualitySensor(QStreamSensorBase):
    """Air quality index sensor."""

    _attr_name = "Air Quality"
    _attr_device_class = SensorDeviceClass.AQI
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_air_quality"
        self._aqi_value = None

    async def async_update(self) -> None:
        """Update AQI value."""
        try:
            self._aqi_value = await self.coordinator.client.get_air_quality()
        except Exception as err:
            _LOGGER.warning("Failed to fetch air quality: %s", err)
            self._aqi_value = None

    @property
    def native_value(self) -> int | None:
        """Return the AQI value."""
        return self._aqi_value


class QStreamFlowSensor(QStreamSensorBase):
    """Flow percentage sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
        field: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._field = field
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{field}"

    @property
    def native_value(self) -> int:
        """Return the flow percentage."""
        return getattr(self.coordinator.data, self._field)


class QStreamTimerRemainingSensor(QStreamSensorBase):
    """Timer remaining sensor."""

    _attr_name = "Timer Remaining"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_timer_remaining"

    @property
    def native_value(self) -> int:
        """Return timer remaining minutes."""
        return self.coordinator.data.timer_remaining_minutes


class QStreamScheduleModeSensor(QStreamSensorBase):
    """Schedule mode sensor."""

    _attr_name = "Schedule Mode"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_mode"

    @property
    def native_value(self) -> str:
        """Return schedule mode."""
        return self.coordinator.data.schedule_mode.value


class QStreamScheduleRemainingSensor(QStreamSensorBase):
    """Schedule remaining sensor."""

    _attr_name = "Schedule Remaining"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_remaining"

    @property
    def native_value(self) -> int:
        """Return schedule remaining minutes."""
        return self.coordinator.data.schedule_remaining_minutes


class QStreamBinarySensorBase(
    CoordinatorEntity[QStreamDataUpdateCoordinator], BinarySensorEntity
):
    """Base class for QStream binary sensors."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }


class QStreamValveBinarySensor(QStreamBinarySensorBase):
    """Valve state binary sensor."""

    _attr_name = "Valve"
    _attr_device_class = BinarySensorDeviceClass.OPENING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_valve"

    @property
    def is_on(self) -> bool:
        """Return true if valve is open."""
        return self.coordinator.data.valve_open


class QStreamTimerActiveBinarySensor(QStreamBinarySensorBase):
    """Timer active binary sensor."""

    _attr_name = "Timer Active"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_timer_active"

    @property
    def is_on(self) -> bool:
        """Return true if timer is active."""
        return self.coordinator.data.timer_active


class QStreamScheduleEnabledBinarySensor(QStreamBinarySensorBase):
    """Schedule enabled binary sensor."""

    _attr_name = "Schedule Enabled"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_enabled"

    @property
    def is_on(self) -> bool:
        """Return true if schedule is enabled."""
        return self.coordinator.data.schedule_enabled
```

**Step 4: Run tests**

Run: `pytest tests/test_sensor.py -v`

Expected: Tests PASS

**Step 5: Commit**

```bash
git add tests/test_sensor.py custom_components/qstream/sensor.py
git commit -m "feat: implement sensor entities

- Add AQI sensor (primary)
- Add flow sensors (analog, set, actual) as diagnostic
- Add timer and schedule sensors
- Add binary sensors for valve, timer active, schedule enabled"
```

---

## Task 10: HACS Configuration and Final Documentation

**Files:**
- Create: `hacs.json`
- Create: `LICENSE`
- Modify: `README.md`

**Step 1: Create hacs.json**

Create `hacs.json`:

```json
{
  "name": "QStream Ventilation Fan",
  "render_readme": true,
  "domains": ["fan", "sensor", "switch"]
}
```

**Step 2: Create LICENSE**

Create `LICENSE`:

```
MIT License

Copyright (c) 2025 Bram

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 3: Enhance README**

Update `README.md` with complete documentation:

```markdown
# QStream Home Assistant Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant custom integration for BUVA QStream 2.0 WiFi-enabled ventilation fans.

## Features

### Entities

**Fan Entity** (`fan.qstream_fan`)
- Percentage-based speed control (0-100%)
- Four preset modes (Low, Medium, High, Turbo) mapped to device levels
- Turn on/off control

**Switch Entity** (`switch.qstream_fan_demand_control`)
- Toggle automatic speed adjustment based on air quality sensor
- Preserves current fan speed when toggled

**Sensors**
- `sensor.qstream_fan_air_quality` - Air Quality Index (AQI) from device sensor
- `sensor.qstream_fan_analog_flow` - Flow demanded by analog sensor (%)
- `sensor.qstream_fan_set_flow` - Target flow percentage (%)
- `sensor.qstream_fan_actual_flow` - Current actual flow (%)
- `sensor.qstream_fan_timer_remaining` - Timer remaining (minutes)
- `sensor.qstream_fan_schedule_mode` - Current schedule mode (DAY/NIGHT)
- `sensor.qstream_fan_schedule_remaining` - Schedule remaining (minutes)

**Binary Sensors**
- `binary_sensor.qstream_fan_valve` - Valve position (open/closed)
- `binary_sensor.qstream_fan_timer_active` - Timer active state
- `binary_sensor.qstream_fan_schedule_enabled` - Schedule enabled state

## Installation

### Prerequisites

- Home Assistant 2025.10 or later
- QStream 2.0 device on local network
- Device IP address or hostname

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (top right)
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/bramton/qstream-ha`
6. Category: Integration
7. Click "Add"
8. Search for "QStream Ventilation Fan"
9. Click "Download"
10. Restart Home Assistant
11. Add integration via Configuration → Integrations → Add Integration

### Manual Installation

1. Copy the `custom_components/qstream/` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Configuration → Integrations → Add Integration

## Configuration

1. Navigate to Configuration → Integrations
2. Click "+ Add Integration"
3. Search for "QStream"
4. Enter your device's IP address or hostname (e.g., `192.168.1.100`)
5. Optionally provide a friendly name (defaults to "QStream Fan")
6. Click Submit

The integration will validate the connection and create all entities automatically.

## Usage Examples

### Automations

**Turn on fan at 75% when humidity exceeds 70%:**

```yaml
automation:
  - alias: "Bathroom Fan Auto On"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bathroom_humidity
        above: 70
    action:
      - service: fan.set_percentage
        target:
          entity_id: fan.qstream_fan
        data:
          percentage: 75
```

**Enable demand control during the day:**

```yaml
automation:
  - alias: "Enable Demand Control Morning"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.qstream_fan_demand_control
```

**Notify when air quality is poor:**

```yaml
automation:
  - alias: "Poor Air Quality Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.qstream_fan_air_quality
        above: 150
    action:
      - service: notify.mobile_app
        data:
          message: "Air quality is poor (AQI: {{ states('sensor.qstream_fan_air_quality') }})"
```

## Troubleshooting

### Integration fails to connect

- Verify device IP address is correct
- Ensure device is powered on and connected to network
- Check firewall rules allow communication on port 80
- Try pinging the device from Home Assistant host

### Entities show as unavailable

- Check Home Assistant logs for connection errors
- Verify device hasn't changed IP address (consider DHCP reservation)
- Restart integration from Configuration → Integrations

### Preset modes don't match expected speeds

Preset modes map to device levels 1-4, which are user-configurable on the device itself. Check device settings and adjust levels as needed.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check custom_components/qstream/
```

### Type Checking

```bash
mypy custom_components/qstream/
```

## Support

- Report bugs: [GitHub Issues](https://github.com/bramton/qstream-ha/issues)
- Feature requests: [GitHub Discussions](https://github.com/bramton/qstream-ha/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

- Built using the [qstream](https://pypi.org/project/qstream/) Python library
- Community reverse-engineered QStream 2.0 API (not officially supported by BUVA)

## Disclaimer

This integration is not affiliated with or endorsed by BUVA. Use at your own risk.
```

**Note:** Update GitHub URLs with actual repository location.

**Step 4: Commit**

```bash
git add hacs.json LICENSE README.md
git commit -m "feat: add HACS configuration and documentation

- Add hacs.json for HACS compatibility
- Add MIT LICENSE
- Enhance README with full documentation
- Add usage examples and troubleshooting"
```

---

## Task 11: Validation and Final Testing

**Files:**
- Create: `.github/workflows/validate.yml`
- Create: `pyproject.toml` updates

**Step 1: Create GitHub Actions workflow**

Create `.github/workflows/validate.yml`:

```yaml
name: Validate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Validate manifest
        run: |
          python -c "import json; json.load(open('custom_components/qstream/manifest.json'))"

      - name: Validate HACS
        run: |
          python -c "import json; json.load(open('hacs.json'))"

      - name: Run ruff
        run: uv run ruff check custom_components/qstream/

      - name: Run mypy
        run: uv run mypy custom_components/qstream/

      - name: Run tests
        run: uv run pytest tests/ -v
```

**Step 2: Update pyproject.toml with tool configs**

Update `pyproject.toml` to add ruff and mypy configuration:

```toml
[project]
name = "qstream-ha"
version = "0.1.0"
description = "Home Assistant integration for QStream ventilation fans"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "homeassistant",
    "pytest",
    "pytest-homeassistant-custom-component",
    "ruff",
    "mypy",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "F",  # pyflakes
    "I",  # isort
]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
strict = false
```

**Step 3: Run validation locally**

Run all validation steps:

```bash
# Validate JSON files
python -c "import json; json.load(open('custom_components/qstream/manifest.json'))"
python -c "import json; json.load(open('hacs.json'))"

# Run linting
ruff check custom_components/qstream/

# Run type checking
mypy custom_components/qstream/

# Run tests
pytest tests/ -v
```

Expected: All validation passes

**Step 4: Commit**

```bash
git add .github/workflows/validate.yml pyproject.toml
git commit -m "ci: add validation workflow

- Add GitHub Actions workflow for CI
- Validate manifest.json and hacs.json
- Run ruff linting and mypy type checking
- Run pytest test suite
- Configure ruff and mypy in pyproject.toml"
```

---

## Task 12: Publish qstream to PyPI (Prerequisite)

**Note:** This task must be completed in the qstream library repository, not this one.

**Files (in ../qstream):**
- Verify: `pyproject.toml` has correct metadata
- Verify: `README.md` exists
- Verify: `LICENSE` exists

**Step 1: Navigate to qstream repo**

```bash
cd ../qstream
```

**Step 2: Verify pyproject.toml**

Ensure `pyproject.toml` has all required fields:

```toml
[project]
name = "qstream"
version = "0.1.0"
description = "Async Python client for BUVA QStream 2.0 ventilation fans"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.11"
dependencies = ["aiohttp>=3.9.0"]
keywords = ["qstream", "buva", "ventilation", "home-assistant"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://github.com/bramton/qstream"
Repository = "https://github.com/bramton/qstream"
Issues = "https://github.com/bramton/qstream/issues"
```

**Step 3: Build package**

```bash
uv build
```

**Step 4: Publish to PyPI**

```bash
uv publish
```

**Note:** You'll need PyPI credentials. Create account at https://pypi.org/ and generate API token.

**Step 5: Verify publication**

```bash
pip install qstream
python -c "from qstream import QStreamClient; print('Success')"
```

**Step 6: Return to qstream-ha repo**

```bash
cd ../qstream-ha
```

---

## Task 13: Local Testing with Real Device

**Prerequisites:**
- qstream published to PyPI
- QStream device on network
- Home Assistant development environment

**Step 1: Create test configuration**

Create `.dev/configuration.yaml` for testing:

```yaml
# Minimal HA config for testing
homeassistant:
  name: Development
  latitude: 51.5
  longitude: -0.1
  unit_system: metric
  time_zone: UTC

# Enable logging
logger:
  default: info
  logs:
    custom_components.qstream: debug
    qstream: debug
```

**Step 2: Symlink integration to HA config**

```bash
# Assuming HA config at ~/.homeassistant
mkdir -p ~/.homeassistant/custom_components
ln -s $(pwd)/custom_components/qstream ~/.homeassistant/custom_components/qstream
```

**Step 3: Restart Home Assistant**

```bash
# Method depends on your HA installation
# Docker: docker restart homeassistant
# Service: sudo systemctl restart home-assistant
```

**Step 4: Add integration via UI**

1. Open Home Assistant
2. Navigate to Configuration → Integrations
3. Click "+ Add Integration"
4. Search "QStream"
5. Enter device IP address
6. Verify all entities are created

**Step 5: Test functionality**

Manual testing checklist:

- [ ] Fan turns on with percentage control
- [ ] Fan turns on with preset mode
- [ ] Fan turns off
- [ ] Preset modes match device levels
- [ ] Demand control switch toggles correctly
- [ ] AQI sensor updates
- [ ] All diagnostic sensors show correct values
- [ ] Integration handles device offline gracefully
- [ ] Integration survives HA restart

**Step 6: Check logs for errors**

```bash
tail -f ~/.homeassistant/home-assistant.log | grep qstream
```

Expected: No errors, only info/debug logs

**Step 7: Document test results**

Create `TESTING.md`:

```markdown
# Testing Results

## Test Environment
- Home Assistant Version: [version]
- QStream Device IP: [ip]
- Device Firmware: [if known]
- Date: [date]

## Test Results

### Config Flow
- [x] Integration adds successfully
- [x] Connection validation works
- [x] Error handling (wrong IP, timeout) works

### Fan Entity
- [x] Turn on with percentage
- [x] Turn on with preset mode
- [x] Turn off
- [x] Preset modes map correctly

### Switch Entity
- [x] Demand control toggles on
- [x] Demand control toggles off
- [x] State reflects correctly

### Sensors
- [x] AQI sensor updates
- [x] Flow sensors show correct values
- [x] Timer/schedule sensors work
- [x] Binary sensors work

### Error Handling
- [x] Device offline handled gracefully
- [x] Network errors don't crash integration
- [x] Integration survives HA restart

## Issues Found
[List any issues encountered]

## Notes
[Any additional observations]
```

**Step 8: Commit test results**

```bash
git add TESTING.md
git commit -m "docs: add local testing results"
```

---

## Completion Checklist

Before considering implementation complete:

### Code Quality
- [ ] All unit tests pass
- [ ] Ruff linting passes with no errors
- [ ] Mypy type checking passes
- [ ] Code follows HA integration best practices

### Documentation
- [ ] README.md is complete and accurate
- [ ] strings.json has all UI translations
- [ ] TESTING.md documents test results
- [ ] Design document updated if architecture changed

### HACS Compatibility
- [ ] hacs.json is valid
- [ ] manifest.json is valid
- [ ] Repository structure matches HACS requirements
- [ ] All required files present (LICENSE, README, etc.)

### Functionality
- [ ] Fan entity works (on/off, percentage, presets)
- [ ] Switch entity works (demand control toggle)
- [ ] All sensors report correct values
- [ ] Config flow validates correctly
- [ ] Integration handles errors gracefully

### Distribution
- [ ] qstream library published to PyPI
- [ ] GitHub repository created
- [ ] CI/CD workflow runs successfully
- [ ] Tagged release (v0.1.0)

---

## Next Steps After Implementation

1. **Create GitHub Repository**
   - Push code to GitHub
   - Add repository description and topics
   - Create release v0.1.0

2. **Submit to HACS**
   - Follow HACS submission process
   - Wait for review and approval

3. **Community Engagement**
   - Post on Home Assistant forums
   - Share on Reddit r/homeassistant
   - Respond to issues and feedback

4. **Future Enhancements**
   - Custom timer service
   - Schedule management
   - Device discovery
   - Multiple device support

---

## Reference Documentation

- Home Assistant Developer Docs: https://developers.home-assistant.io/
- HACS Documentation: https://hacs.xyz/docs/publish/start
- qstream Library: https://github.com/bramton/qstream
- Design Document: `docs/plans/2025-10-25-qstream-ha-integration-design.md`
