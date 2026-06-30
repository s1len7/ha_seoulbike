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

        return nearest.get("station_name")

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return {}

        return {
            "station_id": nearest.get("station_id"),
            "station_name": nearest.get("station_name"),
            "lat": nearest.get("lat"),
            "lon": nearest.get("lon"),
            "distance_km": nearest.get("distance_km"),
            "bikes": nearest.get("bikes"),
            "racks": nearest.get("racks"),
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
            cleaned.append({
                "station_id": s.get("station_id"),
                "station_name": s.get("station_name"),
                "lat": s.get("lat"),
                "lon": s.get("lon"),
                "distance_km": s.get("distance_km"),
                "bikes": s.get("bikes"),
                "racks": s.get("racks"),
            })

        return {
            "stations": cleaned
        }