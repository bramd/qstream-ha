"""Data update coordinator for QStream integration."""

import logging
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
