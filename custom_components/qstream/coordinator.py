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
        self._last_aqi: int | None = None  # Cache last successful AQI value
        super().__init__(
            hass,
            _LOGGER,
            name="QStream",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> QStreamData:
        """Fetch data from API endpoint.

        Note: AQI failures are logged but don't fail the entire update,
        since fan control (status) is more critical than air quality data.
        The coordinator will retry on the next interval (30s).
        """
        try:
            status = await self.client.get_status()
        except QStreamError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

        # Fetch AQI separately - don't fail entire update if AQI unavailable
        # Some devices may not have AQI or endpoint may be temporarily busy
        # Keep last known value if fetch fails (AQI changes slowly)
        try:
            aqi = await self.client.get_air_quality()
            self._last_aqi = aqi  # Cache successful value
            _LOGGER.debug("Fetched AQI: %s", aqi)
        except QStreamError as err:
            # Keep last known AQI - it changes slowly, stale better than unknown
            _LOGGER.debug(
                "AQI not available (%s), using cached value: %s", err, self._last_aqi
            )
        except Exception as err:
            _LOGGER.warning(
                "Unexpected error fetching air quality: %s",
                err,
                exc_info=True,
            )

        return QStreamData(status=status, air_quality=self._last_aqi)
