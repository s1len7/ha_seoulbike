from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .marker import build_marker_svg, get_availability_marker


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    known = set()

    def create():
        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:
            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in known:
                continue

            entity = SeoulBikeGeoLocation(coordinator, s)
            known.add(station_id)
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    create()

    def _update():
        create()

    coordinator.async_add_listener(_update)


class SeoulBikeGeoLocation(CoordinatorEntity, Entity):

    def __init__(self, coordinator, station):

        super().__init__(coordinator)

        self._station_id = station.get("station_id")
        self._station = station

        self._attr_unique_id = f"{DOMAIN}.geo_location.{self._station_id}"
        self._attr_name = station.get("name") or self._station_id
        self._attr_icon = "mdi:map-marker"

    @property
    def latitude(self):
        station = self._get_station()
        try:
            return float(station.get("lat"))
        except (TypeError, ValueError):
            return None

    @property
    def longitude(self):
        station = self._get_station()
        try:
            return float(station.get("lon"))
        except (TypeError, ValueError):
            return None

    @property
    def state(self):
        station = self._get_station()
        return station.get("bikes")

    @property
    def extra_state_attributes(self):
        station = self._get_station()
        marker_color, availability = get_availability_marker(station.get("bikes"))

        return {
            "station_id": station.get("station_id"),
            "name": station.get("name"),
            "distance_km": station.get("distance_km"),
            "bikes": station.get("bikes"),
            "racks": station.get("racks"),
            "availability_ratio": station.get("availability_ratio"),
            "availability": availability,
            "marker_color": marker_color,
            "latitude": station.get("lat"),
            "longitude": station.get("lon"),
        }

    @property
    def entity_picture(self):
        station = self._get_station()
        return build_marker_svg(station.get("bikes"))

    def _get_station(self):
        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return self._station or {}
