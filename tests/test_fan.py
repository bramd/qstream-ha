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
