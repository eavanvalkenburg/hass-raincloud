"""Support for Melnor RainCloud sprinkler water timer."""
import logging

from raincloudy.core import RainCloudy

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_MONITORED_CONDITIONS
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import BINARY_SENSORS, DOMAIN, ICON_MAP
from . import RainCloudEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a sensor for a raincloud device."""
    raincloud: RainCloudy = hass.data[DOMAIN]["raincloud"]
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN]["coordinator"]

    sensors = []
    for sensor_type in BINARY_SENSORS:
        if sensor_type == "status":
            for controller in raincloud.controllers:
                sensors.append(
                    RainCloudBinarySensor(coordinator, controller, sensor_type)
                )

                for faucet in controller.faucets:
                    sensors.append(
                        RainCloudBinarySensor(coordinator, faucet, sensor_type)
                    )

        else:
            # create a sensor for each zone managed by controller and faucet
            for controller in raincloud.controllers:
                for faucet in controller.faucets:
                    for zone in faucet.zones:
                        sensors.append(
                            RainCloudBinarySensor(coordinator, zone, sensor_type)
                        )

    add_entities(sensors, True)
    return True


class RainCloudBinarySensor(RainCloudEntity, BinarySensorEntity):
    """A sensor implementation for raincloud device."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    def update(self):
        """Get the latest data and updates the state."""
        _LOGGER.debug("Updating RainCloud sensor: %s", self._attr_name)
        self._state = getattr(self.data, self._sensor_type)
        if self._sensor_type == "status":
            self._state = self._state == "Online"

    @property
    def icon(self):
        """Return the icon of this device."""
        if self._sensor_type == "is_watering":
            return "mdi:water" if self.is_on else "mdi:water-off"
        if self._sensor_type == "status":
            return "mdi:pipe" if self.is_on else "mdi:pipe-disconnected"
        return ICON_MAP.get(self._sensor_type)