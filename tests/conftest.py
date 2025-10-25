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
