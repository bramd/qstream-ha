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
    client.get_air_quality = AsyncMock(return_value=50)
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

    await coordinator.async_refresh()

    assert coordinator.data.status == mock_status
    assert mock_client.get_status.called


async def test_coordinator_update_failure(hass: HomeAssistant, mock_client):
    """Test coordinator handles update failure."""
    mock_client.get_status.side_effect = QStreamConnectionError("Connection failed")

    coordinator = QStreamDataUpdateCoordinator(
        hass, mock_client, update_interval=timedelta(seconds=30)
    )

    # async_refresh() doesn't raise, it sets last_update_success to False
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False
