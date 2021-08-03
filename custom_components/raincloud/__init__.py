"""Support for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from raincloudy.core import RainCloudy, RainCloudyController

from .const import DOMAIN, RAIN_DELAY_DAYS_ATTR, RAIN_DELAY_SERVICE_ATTR, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Component setup, run import config flow for each entry in config."""
    if DOMAIN not in config:
        return True
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Melnor RainCloud component."""
    hass.data.setdefault(DOMAIN, {})
    raincloud = RainCloudy(
        username=entry.data[CONF_USERNAME], password=entry.data[CONF_PASSWORD]
    )

    async def async_refresh() -> list[RainCloudyController]:
        """Call Raincloud hub to refresh information."""
        _LOGGER.debug("Updating RainCloud Hub component")
        # TODO: async call update
        try:
            await hass.async_add_executor_job(raincloud.update())
        except Exception as exc:
            raise UpdateFailed(
                f"Update for raincloud failed with exception: {exc}"
            ) from exc
        return raincloud.controllers

    # Call the Raincloud API to refresh updates
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="raincloud",
        update_method=async_refresh,
        update_interval=SCAN_INTERVAL,
    )
    await coordinator.async_config_entry_first_refresh()

    async def async_handle_rain_delay(call):
        """Set the rain delay for all valves"""
        days = call.data.get(RAIN_DELAY_DAYS_ATTR, 0)

        for controller in raincloud.controllers:
            for faucet in controller.faucets:
                for zone in faucet.zones:
                    await hass.async_add_executor_job(
                        zone._set_rain_delay(zone.id, days)
                    )
        await coordinator.async_request_refresh()
        return True

    await hass.services.async_register(
        DOMAIN, RAIN_DELAY_SERVICE_ATTR, async_handle_rain_delay
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "raincloud": raincloud,
        "coordinator": coordinator,
    }
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True
