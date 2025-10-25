"""Pytest fixtures for QStream integration tests."""

import sys
from pathlib import Path

# Add custom_components to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant

# This tells pytest-homeassistant-custom-component where to find our integration
pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_qstream_client():
    """Mock QStreamClient."""
    with patch("custom_components.qstream.config_flow.QStreamClient") as mock:
        client = mock.return_value
        client.get_status = AsyncMock(return_value=None)
        client.close = AsyncMock()
        yield client
