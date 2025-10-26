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
