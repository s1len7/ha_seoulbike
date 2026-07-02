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

        return nearest.station_name

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return {}

        return {
            "station_id": nearest.station_id,
            "station_name": nearest.station_name,
            "lat": nearest.lat,
            "lon": nearest.lon,
            "distance_km": nearest.distance_km,
            "parking_bike_total_count": nearest.parking_bike_total_count,
            "rack_total_count": nearest.rack_total_count,
            "shared": nearest.shared,
            "availability_ratio": nearest.availability_ratio,
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

        return {
            "stations": [
                {
                    "station_id": station.station_id,
                    "station_name": station.station_name,
                    "lat": station.lat,
                    "lon": station.lon,
                    "distance_km": station.distance_km,
                    "parking_bike_total_count": station.parking_bike_total_count,
                    "rack_total_count": station.rack_total_count,
                    "shared": station.shared,
                    "availability_ratio": station.availability_ratio,
                }
                for station in top
            ]
        }