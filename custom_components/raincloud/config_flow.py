"""Config flow for Raincloud integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from raincloudy.core import RainCloudy
from requests.exceptions import ConnectTimeout, HTTPError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


class RaincloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for youless."""

    VERSION = 1
    _reauth_entry = None

    def __init__(self):
        """Start the Brunt config flow."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        errors = None
        try:
            raincloud = RainCloudy(
                username=user_input[CONF_USERNAME], password=user_input[CONF_PASSWORD]
            )
            if not raincloud.is_connected:
                raise HTTPError
        except (ConnectTimeout, HTTPError) as ex:
            _LOGGER.warning("Could not connect with error: %s", ex)
            errors = {"base": "cannot_connect"}
        # except ClientResponseError as exc:
        #     if exc.status == 403:
        #         errors = {"base": "invalid_auth"}
        #     else:
        #         _LOGGER.warning("Unknown error when connecting to Raincloud: %s", exc)
        #         errors = {"base": "unknown"}
        # except ServerDisconnectedError:
        #     errors = {"base": "cannot_connect"}
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.warning("Unknown error when connecting to Raincloud: %s", exc)
            errors = {"base": "unknown"}
        finally:
            raincloud.logout()
        if errors is not None:
            return self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA, errors=errors
            )

        await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
        if self._reauth_entry is None or self._reauth_entry.unique_id != self.unique_id:
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_USERNAME],
                data=user_input,
            )

        self.hass.config_entries.async_update_entry(self._reauth_entry, data=user_input)
        await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)

        return self.async_abort(reason="reauth_successful")

    async def async_step_import(self, import_config):
        """Import config from configuration.yaml."""
        await self.async_set_unique_id(import_config[CONF_USERNAME].lower())
        self._abort_if_unique_id_configured()
        return await self.async_step_user(import_config)

    async def async_step_reauth(self, user_input=None):
        """Perform reauth if the user credentials have changed."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_user()


# TODO: Optionsflow for CONF_WATERING_TIME and SCAN_INTERVAL
