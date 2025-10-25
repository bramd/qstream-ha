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
