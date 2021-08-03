"""Raincloud constants."""

from datetime import timedelta

from homeassistant.const import PERCENTAGE, TIME_DAYS, TIME_MINUTES

ALLOWED_WATERING_TIME = [5, 10, 15, 30, 45, 60]
ATTRIBUTION = "Data provided by Melnor Aquatimer.com"

CONF_WATERING_TIME = "watering_minutes"

NOTIFICATION_ID = "raincloud_notification"
NOTIFICATION_TITLE = "Rain Cloud Setup"

DOMAIN = "raincloud"
DEFAULT_WATERING_TIME = 15

KEY_MAP = {
    "auto_watering": "Automatic Watering",
    "battery": "Battery",
    "is_watering": "Watering",
    "manual_watering": "Manual Watering",
    "next_cycle": "Next Cycle",
    "rain_delay": "Rain Delay",
    "status": "Status",
    "watering_time": "Remaining Watering Time",
}

ICON_MAP = {
    "auto_watering": "mdi:autorenew",
    "is_watering": "",
    "status": "",
    "battery": "",
    "manual_watering": "mdi:water-pump",
    "next_cycle": "mdi:calendar-clock",
    "rain_delay": "mdi:weather-rainy",
    "watering_time": "mdi:water-pump",
}

UNIT_OF_MEASUREMENT_MAP = {
    "auto_watering": "",
    "battery": PERCENTAGE,
    "is_watering": "",
    "manual_watering": "",
    "next_cycle": "",
    "rain_delay": TIME_DAYS,
    "status": "",
    "watering_time": TIME_MINUTES,
}

BINARY_SENSORS = ["is_watering", "status"]
SENSORS = ["battery", "next_cycle", "rain_delay", "watering_time"]
ZONE_SENSORS = ["next_cycle", "rain_delay", "watering_time"]
SWITCHES = ["auto_watering", "manual_watering"]

RAIN_DELAY_SERVICE_ATTR = "rain_delay"
RAIN_DELAY_DAYS_ATTR = "days"
SCAN_INTERVAL = timedelta(seconds=10)
SIGNAL_UPDATE_RAINCLOUD = "raincloud_update"
