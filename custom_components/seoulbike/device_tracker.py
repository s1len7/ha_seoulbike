from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = {}

    def create_entities():

        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:

            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in entities:
                continue

            entity = SeoulBikeTracker(coordinator, station_id, s)
            entities[station_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    create_entities()

    coordinator.async_add_listener(lambda: create_entities())


class SeoulBikeTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator, station_id, station):

        super().__init__(coordinator)

        self._station_id = station_id
        self._station = station

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{station_id}"
        self._attr_name = station.get("name") or station_id
        self._attr_icon = "mdi:bicycle"

    @property
    def latitude(self):
        try:
            return float(self._get_station().get("lat"))
        except Exception:
            return None

    @property
    def longitude(self):
        try:
            return float(self._get_station().get("lon"))
        except Exception:
            return None

    @property
    def state(self):
        try:
            return int(self._get_station().get("bikes") or 0)
        except Exception:
            return 0

    @property
    def extra_state_attributes(self):

        station = self._get_station()

        return {
            "station_id": station.get("station_id"),
            "name": station.get("name"),
            "distance_km": station.get("distance_km"),
            "bikes": station.get("bikes"),
            "racks": station.get("racks"),
            "availability_ratio": station.get("availability_ratio"),
            "latitude": station.get("lat"),
            "longitude": station.get("lon"),
        }

    def _get_station(self):
        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return self._station