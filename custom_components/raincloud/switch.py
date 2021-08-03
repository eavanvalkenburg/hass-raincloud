"""Support for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

import logging
from typing import Callable, Generator

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from raincloudy.core import RainCloudy

from .base_entity import RainCloudEntity
from .const import DEFAULT_WATERING_TIME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable[[], None]
) -> None:
    """Set up a sensor for a raincloud device."""
    raincloud: RainCloudy = hass.data[DOMAIN][entry.entry_id]["raincloud"]
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    def generate_switches() -> Generator[RainCloudEntity, None, None]:
        """Generator function for the sensors."""
        for controller in raincloud.controllers:
            for faucet in controller.faucets:
                for zone in faucet.zones:
                    yield RainCloudAutoWateringSwitch(coordinator, zone)
                    yield RainCloudManualWateringSwitch(coordinator, zone)

    async_add_entities(generate_switches)


class RainCloudAutoWateringSwitch(RainCloudEntity, SwitchEntity):
    """A switch implementation for raincloud device."""

    def __init__(self, coordinator, rc_object):
        """Initialize a switch for raincloud device."""
        super().__init__(coordinator, rc_object, "auto_watering")

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            self.rc_object._set_auto_watering(self.rc_object.id, True)
        )
        self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            self.rc_object._set_auto_watering(self.rc_object.id, False)
        )
        self.coordinator.async_request_refresh()

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud switch: %s", self._attr_name)
        self._attr_is_on = self.rc_object.auto_watering


class RainCloudManualWateringSwitch(RainCloudEntity, SwitchEntity):
    """A switch implementation for raincloud device."""

    def __init__(self, coordinator, rc_object):
        """Initialize a switch for raincloud device."""
        super().__init__(coordinator, rc_object, "manual_watering")
        self._default_watering_timer = DEFAULT_WATERING_TIME
        self._attr_extra_state_attributes[
            "default_manual_timer"
        ] = self._default_watering_timer

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            self.rc_object._set_manual_watering_time(
                self.rc_object.id, self._default_watering_timer
            )
        )
        self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            self.rc_object._set_manual_watering_time(self.rc_object.id, "off")
        )
        self.coordinator.async_request_refresh()

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud switch: %s", self._attr_name)
        self._attr_is_on = bool(self.rc_object.manual_watering)
