"""Sensors."""
print("SEOULBIKE SENSOR LOADED")
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SeoulBikeSensor(coordinator),
        ]
    )


class SeoulBikeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "Seoul Bike Nearest Station"
        self._attr_unique_id = "seoulbike_nearest"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        station = data.get("nearest")

        if not station:
            return "No data"

        return f"{station.get('name')} ({station.get('bikes', 0)} bikes)"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        station = data.get("nearest")

        if not station:
            return {}

        return {
            "station_id": station.get("id"),
            "available_bikes": station.get("bikes", 0),
            "lat": station.get("lat"),
            "lon": station.get("lon"),
        }