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
