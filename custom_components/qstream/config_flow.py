"""Config flow for QStream integration."""

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from qstream import QStreamClient
from qstream.exceptions import QStreamConnectionError, QStreamTimeoutError

from .const import DOMAIN, CONF_HOST


class QStreamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for QStream."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME, "QStream Fan")

            # Validate by attempting connection
            session = async_get_clientsession(self.hass)
            client = QStreamClient(host, session=session)

            try:
                await client.get_status()
            except QStreamConnectionError:
                errors["base"] = "cannot_connect"
            except QStreamTimeoutError:
                errors["base"] = "timeout"
            except Exception:
                errors["base"] = "unknown"
            else:
                # Success - create entry
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default="QStream Fan"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
