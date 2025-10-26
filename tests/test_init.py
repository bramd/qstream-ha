"""Tests for QStream integration initialization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.qstream.const import DOMAIN


@pytest.fixture
def mock_client():
    """Mock QStreamClient."""
    client = MagicMock()
    client.get_status = AsyncMock()
    client.get_air_quality = AsyncMock(return_value=50)
    client.cancel_timer = AsyncMock()
    return client


async def test_clear_timer_service_registered(hass: HomeAssistant, mock_client):
    """Test that clear_timer service is registered."""
    with patch(
        "custom_components.qstream.QStreamClient",
        return_value=mock_client,
    ):
        # Set up integration with mock config entry
        assert await async_setup_component(
            hass,
            DOMAIN,
            {
                DOMAIN: {
                    "host": "192.168.1.100",
                }
            },
        )
        await hass.async_block_till_done()

    # Verify service is registered
    assert hass.services.has_service(DOMAIN, "clear_timer")


async def test_clear_timer_service_calls_cancel(hass: HomeAssistant, mock_client):
    """Test that clear_timer service calls cancel_timer on client."""
    with (
        patch(
            "custom_components.qstream.QStreamClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.qstream.coordinator.QStreamDataUpdateCoordinator.async_config_entry_first_refresh"
        ),
    ):
        # Set up integration
        entry = MagicMock()
        entry.data = {"host": "192.168.1.100"}
        entry.entry_id = "test_entry"

        from custom_components.qstream import async_setup_entry

        await async_setup_entry(hass, entry)
        await hass.async_block_till_done()

    # Call service
    await hass.services.async_call(
        DOMAIN,
        "clear_timer",
        {},
        blocking=True,
    )

    # Verify cancel_timer was called
    mock_client.cancel_timer.assert_called_once()


async def test_clear_timer_service_idempotent(hass: HomeAssistant, mock_client):
    """Test that clear_timer service succeeds even if no timer active."""
    # This test verifies idempotent behavior - service should not raise
    # exceptions even if cancel_timer is called when no timer is running
    with (
        patch(
            "custom_components.qstream.QStreamClient",
            return_value=mock_client,
        ),
        patch(
            "custom_components.qstream.coordinator.QStreamDataUpdateCoordinator.async_config_entry_first_refresh"
        ),
    ):
        entry = MagicMock()
        entry.data = {"host": "192.168.1.100"}
        entry.entry_id = "test_entry"

        from custom_components.qstream import async_setup_entry

        await async_setup_entry(hass, entry)
        await hass.async_block_till_done()

    # Call service multiple times
    await hass.services.async_call(DOMAIN, "clear_timer", {}, blocking=True)
    await hass.services.async_call(DOMAIN, "clear_timer", {}, blocking=True)

    # Should succeed both times
    assert mock_client.cancel_timer.call_count == 2
