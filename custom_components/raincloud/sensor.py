"""Support for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

import logging
from typing import Callable, Generator

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from raincloudy.core import RainCloudy

from .base_entity import RainCloudEntity
from .const import DOMAIN, ZONE_SENSORS

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
            for faucet in controller.faucets:
                yield RainCloudBattery(coordinator, faucet)
                for zone in faucet.zones:
                    for sensor_type in ZONE_SENSORS:
                        yield RainCloudSensor(coordinator, zone, sensor_type)

    async_add_entities(generate_sensors)


class RainCloudSensor(RainCloudEntity):
    """A sensor implementation for raincloud device."""

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud sensor: %s", self._attr_name)
        self._attr_state = getattr(self.rc_object, self._sensor_type)


class RainCloudBattery(RainCloudEntity):
    """A sensor implementation for raincloud device."""

    def __init__(self, coordinator, rc_object):
        """Create a binary sensor for status."""
        super().__init__(coordinator, rc_object, "battery")

    @callback
    def _state_update(self):
        """Update the state of the entity after the coordinator finishes."""
        _LOGGER.debug("Updating RainCloud sensor: %s", self._attr_name)
        self._attr_state = self.rc_object.battery
        self._attr_icon = icon_for_battery_level(
            battery_level=int(self._attr_state), charging=False
        )
