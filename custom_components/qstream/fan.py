"""Fan platform for QStream integration."""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_TIMER_DURATION,
    DOMAIN,
    PRESET_MODES,
    PRESET_TO_LEVEL,
)
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream fan from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    # Query device levels for preset modes
    preset_percentages = {}
    for preset_name, level_index in PRESET_TO_LEVEL.items():
        try:
            percentage = await coordinator.client.get_level(level_index)
            preset_percentages[preset_name] = percentage
        except Exception as err:
            _LOGGER.warning("Failed to query level %s: %s", level_index, err)
            # Default to evenly spaced percentages
            preset_percentages[preset_name] = level_index * 25

    async_add_entities(
        [QStreamFan(coordinator, entry.entry_id, name, preset_percentages)]
    )


class QStreamFan(CoordinatorEntity[QStreamDataUpdateCoordinator], FanEntity):
    """Representation of a QStream fan."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    )

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        name: str,
        preset_percentages: dict[str, int],
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }
        self._preset_percentages = preset_percentages
        self._attr_preset_modes = PRESET_MODES

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.coordinator.data.status.actual_flow > 0

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self.coordinator.data.status.actual_flow

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        current_flow = self.coordinator.data.status.actual_flow
        # Match current flow to cached preset percentages
        for preset_name, preset_percentage in self._preset_percentages.items():
            if abs(current_flow - preset_percentage) < 5:  # 5% tolerance
                return preset_name
        return None

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        demand_control = self.coordinator.data.status.demand_control_enabled

        if preset_mode:
            percentage = self._preset_percentages[preset_mode]
        elif percentage is None:
            percentage = 50  # Default

        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=percentage,
            demand_control=demand_control,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.client.cancel_timer()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        demand_control = self.coordinator.data.status.demand_control_enabled
        await self.coordinator.client.set_timer(
            duration_minutes=DEFAULT_TIMER_DURATION,
            speed_percentage=percentage,
            demand_control=demand_control,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        await self.async_turn_on(preset_mode=preset_mode)
