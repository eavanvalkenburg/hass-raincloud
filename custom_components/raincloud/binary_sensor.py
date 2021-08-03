"""Support for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

import logging
from typing import Callable, Generator

from raincloudy.core import RainCloudy

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .base_entity import RainCloudEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable[[], None]
) -> None:
    """Set up a sensor for a raincloud device."""
    raincloud: RainCloudy = hass.data[DOMAIN][entry.entry_id]["raincloud"]
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    def generate_sensors() -> Generator[RainCloudEntity, None, None]:
        """Generator function for the sensors."""
        for controller in raincloud.controllers:
            yield RainCloudStatus(coordinator, controller)
            for faucet in controller.faucets:
                yield RainCloudStatus(coordinator, faucet)
                for zone in faucet.zones:
                    yield RainCloudIsWatering(coordinator, zone)

    async_add_entities(generate_sensors)


class RainCloudStatus(RainCloudEntity, BinarySensorEntity):
    """A binary sensor implementation for status raincloud device."""

    def __init__(self, coordinator, rc_object):
        """Create a binary sensor for status."""
        super().__init__(coordinator, rc_object, "status")

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud sensor: %s", self._attr_name)
        self._attr_is_on = self.rc_object.status == "Online"
        self._attr_icon = "mdi:pipe" if self._attr_is_on else "mdi:pipe-disconnected"


class RainCloudIsWatering(RainCloudEntity, BinarySensorEntity):
    """A binary sensor implementation for is_watering raincloud device."""

    def __init__(self, coordinator, rc_object):
        """Create a binary sensor for status."""
        super().__init__(coordinator, rc_object, "is_watering")

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud sensor: %s", self._attr_name)
        self._attr_is_on = self.rc_object.is_watering
        self._attr_icon = "mdi:water" if self._attr_is_on else "mdi:water-off"
