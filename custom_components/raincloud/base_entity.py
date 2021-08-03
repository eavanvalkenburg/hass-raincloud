"""Base entity for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

import logging
from abc import abstractmethod

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    ICON_MAP,
    KEY_MAP,
    UNIT_OF_MEASUREMENT_MAP,
)

_LOGGER = logging.getLogger(__name__)


class RainCloudEntity(CoordinatorEntity):
    """Entity class for RainCloud devices."""

    def __init__(self, coordinator, rc_object, sensor_type):
        """Initialize the RainCloud entity."""
        super().__init__(coordinator=coordinator)
        self.rc_object = rc_object
        self._sensor_type = sensor_type
        if self.rc_object.name is "":
            if hasattr(self.rc_object, "_faucet"):
                self._attr_name = f"{self.rc_object._faucet.id}: Zone {self.rc_object.id} {KEY_MAP.get(self._sensor_type)}"
            else:
                self._attr_name = (
                    f"{self.rc_object.id} {KEY_MAP.get(self._sensor_type)}"
                )
        else:
            self._attr_name = f"{self.rc_object.name} {KEY_MAP.get(self._sensor_type)}"

        if hasattr(self.rc_object, "_faucet"):
            self._attr_unique_id = f"{self.rc_object._faucet.serial}_{self._sensor_type}_{self.rc_object.id}"
        else:
            self._attr_unique_id = f"{self.rc_object.serial}_{self._sensor_type}"
        self._attr_unit_of_measurement = UNIT_OF_MEASUREMENT_MAP.get(self._sensor_type)
        self._attr_extra_state_attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "identifier": self.rc_object.serial,
        }
        self._attr_icon = ICON_MAP.get(self._sensor_type)

    async def async_added_to_hass(self):
        """Register callbacks."""
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._state_update))
        # self.async_on_remove(
        #     async_dispatcher_connect(
        #         self.hass, SIGNAL_UPDATE_RAINCLOUD, self._update_callback
        #     )
        # )

    @callback
    @abstractmethod
    def _state_update(self):
        """Abstract method for updating the state after the controller finishes."""
