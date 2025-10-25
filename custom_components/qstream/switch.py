"""Switch platform for QStream integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_TIMER_DURATION, DOMAIN
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream switch from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    async_add_entities([QStreamDemandControlSwitch(coordinator, entry.entry_id, name)])


class QStreamDemandControlSwitch(
    CoordinatorEntity[QStreamDataUpdateCoordinator], SwitchEntity
):
    """Representation of QStream demand control switch."""

    _attr_has_entity_name = True
    _attr_name = "Demand Control"

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_demand_control"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }

    @property
    def is_on(self) -> bool:
        """Return true if demand control is enabled."""
        return self.coordinator.data.demand_control_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on demand control."""
        current_speed = self.coordinator.data.set_flow
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=current_speed,
            demand_control=True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off demand control."""
        current_speed = self.coordinator.data.set_flow
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=current_speed,
            demand_control=False,
        )
        await self.coordinator.async_request_refresh()
