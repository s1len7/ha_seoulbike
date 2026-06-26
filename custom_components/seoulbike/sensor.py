import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeNearestStation(coordinator),
        SeoulBikeNearbyStations(coordinator),
    ])


class SeoulBikeNearestStation(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_has_entity_name = True

        self._attr_unique_id = f"{DOMAIN}.sensor.nearest_station"
        self._attr_name = self._attr_unique_id
        self._attr_icon = "mdi:information"

    @property
    def state(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return None

        return nearest.get("name")

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return {}

        return {
            "station_id": nearest.get("station_id"),
            "name": nearest.get("name"),
            "lat": float(nearest.get("lat", 0.0)),
            "lon": float(nearest.get("lon", 0.0)),
            "distance_km": float(nearest.get("distance_km", 0.0)),
            "bikes": int(nearest.get("bikes", 0)),
            "racks": int(nearest.get("racks", 0)),
        }


class SeoulBikeNearbyStations(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_has_entity_name = True

        self._attr_unique_id = f"{DOMAIN}.sensor.list_nearby_stations"
        self._attr_name = self._attr_unique_id
        self._attr_icon = "mdi:information"

    @property
    def state(self):

        data = self.coordinator.data or {}
        top = data.get("top_stations", [])

        return len(top)

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        top = data.get("top_stations", [])

        cleaned = []

        for s in top:
            try:
                cleaned.append({
                    "station_id": s.get("station_id"),
                    "name": s.get("name"),
                    "lat": float(s.get("lat", 0.0)),
                    "lon": float(s.get("lon", 0.0)),
                    "distance_km": float(s.get("distance_km", 0.0)),
                    "bikes": int(s.get("bikes", 0)),
                    "racks": int(s.get("racks", 0)),
                })
            except (TypeError, ValueError):
                continue

        return {
            "stations": cleaned
        }