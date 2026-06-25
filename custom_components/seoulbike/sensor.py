"""Sensors for Seoul Bike."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SeoulBikeNearestStationSensor(coordinator),
        ]
    )


class SeoulBikeNearestStationSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "Seoul Bike Nearest Station"
        self._attr_unique_id = "seoulbike_nearest_station"

    @property
    def native_value(self):
        data = self.coordinator.data

        if not data or "nearest_station" not in data:
            return None

        station = data["nearest_station"]

        return f"{station.get('station_name')} ({station.get('bikes', 0)} bikes)"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data

        if not data or "nearest_station" not in data:
            return {}

        station = data["nearest_station"]

        return {
            "station_id": station.get("station_id"),
            "latitude": station.get("latitude"),
            "longitude": station.get("longitude"),
            "available_bikes": station.get("bikes", 0),
        }