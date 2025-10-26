"""The QStream integration."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from qstream import QStreamClient  # type: ignore[import-untyped,attr-defined]

from .const import CONF_HOST, DOMAIN, UPDATE_INTERVAL_SECONDS
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.FAN, Platform.SENSOR, Platform.SWITCH]

SERVICE_CLEAR_TIMER = "clear_timer"


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

    # Register services (only once for first entry)
    if len(hass.data[DOMAIN]) == 1:

        async def async_clear_timer(call: ServiceCall) -> None:
            """Handle clear_timer service call."""
            # Get all coordinators (handles multiple devices)
            for coord in hass.data[DOMAIN].values():
                if isinstance(coord, QStreamDataUpdateCoordinator):
                    try:
                        await coord.client.cancel_timer()
                        # Small delay to let device process command
                        await asyncio.sleep(0.5)
                        await coord.async_refresh()
                    except Exception as err:
                        _LOGGER.error("Failed to clear timer: %s", err)

        hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_TIMER,
            async_clear_timer,
        )

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
