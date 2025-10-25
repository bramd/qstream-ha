"""Sensor platform for QStream integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QStreamDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up QStream sensors from config entry."""
    coordinator: QStreamDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "QStream Fan")

    entities: list[SensorEntity | BinarySensorEntity] = [
        # Primary sensor
        QStreamAirQualitySensor(coordinator, entry.entry_id, name),
        # Diagnostic sensors
        QStreamFlowSensor(coordinator, entry.entry_id, name, "analog_flow", "Analog Flow"),
        QStreamFlowSensor(coordinator, entry.entry_id, name, "set_flow", "Set Flow"),
        QStreamFlowSensor(coordinator, entry.entry_id, name, "actual_flow", "Actual Flow"),
        QStreamTimerRemainingSensor(coordinator, entry.entry_id, name),
        QStreamScheduleModeSensor(coordinator, entry.entry_id, name),
        QStreamScheduleRemainingSensor(coordinator, entry.entry_id, name),
        # Binary sensors
        QStreamValveBinarySensor(coordinator, entry.entry_id, name),
        QStreamTimerActiveBinarySensor(coordinator, entry.entry_id, name),
        QStreamScheduleEnabledBinarySensor(coordinator, entry.entry_id, name),
    ]

    async_add_entities(entities)


class QStreamSensorBase(CoordinatorEntity[QStreamDataUpdateCoordinator], SensorEntity):
    """Base class for QStream sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }


class QStreamAirQualitySensor(QStreamSensorBase):
    """Air quality index sensor."""

    _attr_name = "Air Quality"
    _attr_device_class = SensorDeviceClass.AQI
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_air_quality"
        self._aqi_value = None

    async def async_update(self) -> None:
        """Update AQI value."""
        try:
            self._aqi_value = await self.coordinator.client.get_air_quality()
        except Exception as err:
            _LOGGER.warning("Failed to fetch air quality: %s", err)
            self._aqi_value = None

    @property
    def native_value(self) -> int | None:
        """Return the AQI value."""
        return self._aqi_value


class QStreamFlowSensor(QStreamSensorBase):
    """Flow percentage sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
        field: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._field = field
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{field}"

    @property
    def native_value(self) -> int:
        """Return the flow percentage."""
        return getattr(self.coordinator.data, self._field)


class QStreamTimerRemainingSensor(QStreamSensorBase):
    """Timer remaining sensor."""

    _attr_name = "Timer Remaining"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_timer_remaining"

    @property
    def native_value(self) -> int:
        """Return timer remaining minutes."""
        return self.coordinator.data.timer_remaining_minutes


class QStreamScheduleModeSensor(QStreamSensorBase):
    """Schedule mode sensor."""

    _attr_name = "Schedule Mode"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_mode"

    @property
    def native_value(self) -> str:
        """Return schedule mode."""
        return self.coordinator.data.schedule_mode.value


class QStreamScheduleRemainingSensor(QStreamSensorBase):
    """Schedule remaining sensor."""

    _attr_name = "Schedule Remaining"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_remaining"

    @property
    def native_value(self) -> int:
        """Return schedule remaining minutes."""
        return self.coordinator.data.schedule_remaining_minutes


class QStreamBinarySensorBase(
    CoordinatorEntity[QStreamDataUpdateCoordinator], BinarySensorEntity
):
    """Base class for QStream binary sensors."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": device_name,
            "manufacturer": "BUVA",
            "model": "QStream 2.0",
        }


class QStreamValveBinarySensor(QStreamBinarySensorBase):
    """Valve state binary sensor."""

    _attr_name = "Valve"
    _attr_device_class = BinarySensorDeviceClass.OPENING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_valve"

    @property
    def is_on(self) -> bool:
        """Return true if valve is open."""
        return self.coordinator.data.valve_open


class QStreamTimerActiveBinarySensor(QStreamBinarySensorBase):
    """Timer active binary sensor."""

    _attr_name = "Timer Active"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_timer_active"

    @property
    def is_on(self) -> bool:
        """Return true if timer is active."""
        return self.coordinator.data.timer_active


class QStreamScheduleEnabledBinarySensor(QStreamBinarySensorBase):
    """Schedule enabled binary sensor."""

    _attr_name = "Schedule Enabled"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: QStreamDataUpdateCoordinator,
        entry_id: str,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, device_name)
        self._attr_unique_id = f"{entry_id}_schedule_enabled"

    @property
    def is_on(self) -> bool:
        """Return true if schedule is enabled."""
        return self.coordinator.data.schedule_enabled
