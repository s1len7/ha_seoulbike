from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .marker import build_marker_svg, get_availability_marker


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

            entity = SeoulBikeTracker(coordinator, station_id)
            entities[station_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    create_entities()
    coordinator.async_add_listener(create_entities)


class SeoulBikeTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator, station_id):

        super().__init__(coordinator)

        self._station_id = station_id
        station = self._get_station()

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{station_id}"
        self._attr_name = station.get("station_name")
        self._attr_icon = "mdi:bicycle"
        self._attr_source_type = "gps"

    @property
    def latitude(self):
        s = self._get_station()
        try:
            return float(s.get("lat"))
        except (TypeError, ValueError):
            return None

    @property
    def longitude(self):
        s = self._get_station()
        try:
            return float(s.get("lon"))
        except (TypeError, ValueError):
            return None

    @property
    def state(self):
        s = self._get_station()
        try:
            return int(s.get("bikes") or 0)
        except (TypeError, ValueError):
            return 0

    @property
    def extra_state_attributes(self):
        s = self._get_station()
        marker_color, availability = get_availability_marker(s.get("bikes"))

        return {
            "station_id": s.get("station_id"),
            "station_name": s.get("station_name"),
            "distance_km": s.get("distance_km"),
            "bikes": s.get("bikes"),
            "racks": s.get("racks"),
            "availability_ratio": s.get("availability_ratio"),
            "availability": availability,
            "marker_color": marker_color,
            "latitude": s.get("lat"),
            "longitude": s.get("lon"),
        }

    @property
    def entity_picture(self):
        s = self._get_station()
        return build_marker_svg(s.get("bikes"))

    def _get_station(self):

        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return {}