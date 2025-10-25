"""Data update coordinator for QStream integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from qstream import QStreamClient
from qstream.models import QStreamStatus
from qstream.exceptions import QStreamError

_LOGGER = logging.getLogger(__name__)


class QStreamDataUpdateCoordinator(DataUpdateCoordinator[QStreamStatus]):
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

    async def _async_update_data(self) -> QStreamStatus:
        """Fetch data from API endpoint."""
        try:
            return await self.client.get_status()
        except QStreamError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
