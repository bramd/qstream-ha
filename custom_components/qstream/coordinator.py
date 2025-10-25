"""Data update coordinator for QStream integration."""

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from qstream import QStreamClient  # type: ignore[import-untyped,attr-defined]
from qstream.exceptions import QStreamError  # type: ignore[import-untyped]
from qstream.models import QStreamStatus  # type: ignore[import-untyped]

_LOGGER = logging.getLogger(__name__)


@dataclass
class QStreamData:
    """QStream coordinator data."""

    status: QStreamStatus
    air_quality: int | None


class QStreamDataUpdateCoordinator(DataUpdateCoordinator[QStreamData]):
    """Class to manage fetching QStream data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: QStreamClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="QStream",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> QStreamData:
        """Fetch data from API endpoint."""
        try:
            status = await self.client.get_status()

            # Fetch AQI separately - don't fail entire update if AQI fails
            air_quality = None
            try:
                air_quality = await self.client.get_air_quality()
                _LOGGER.debug("Fetched AQI: %s", air_quality)
            except QStreamError as err:
                _LOGGER.warning("Failed to fetch air quality (QStreamError): %s", err)
            except Exception as err:
                _LOGGER.warning(
                    "Failed to fetch air quality (unexpected error): %s",
                    err,
                    exc_info=True,
                )

            return QStreamData(status=status, air_quality=air_quality)
        except QStreamError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
