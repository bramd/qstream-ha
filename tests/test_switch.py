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
