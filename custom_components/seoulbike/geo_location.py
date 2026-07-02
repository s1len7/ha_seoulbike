from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    known = set()

    def create():

        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for station in stations:

            station_id = station.station_id

            if station_id in known:
                continue

            entity = SeoulBikeGeoLocation(coordinator, station_id)
            known.add(station_id)
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    create()
    coordinator.async_add_listener(create)


class SeoulBikeGeoLocation(CoordinatorEntity, Entity):

    def __init__(self, coordinator, station_id):

        super().__init__(coordinator)

        self._station_id = station_id

        self._attr_unique_id = f"{DOMAIN}.geo_location.{station_id}"
        self._attr_name = self._get_station().station_name if self._get_station() else None
        self._attr_icon = "mdi:map-marker"

    def _get_station(self):

        data = self.coordinator.data or {}

        return data.get("stations_by_id", {}).get(self._station_id)

    @property
    def latitude(self):

        station = self._get_station()
        return station.lat if station else None

    @property
    def longitude(self):

        station = self._get_station()
        return station.lon if station else None

    @property
    def state(self):

        station = self._get_station()
        return station.parking_bike_total_count if station else 0

    @property
    def extra_state_attributes(self):

        station = self._get_station()

        if not station:
            return {}

        return {
            "station_id": station.station_id,
            "station_name": station.station_name,
            "distance_km": station.distance_km,
            "parking_bike_total_count": station.parking_bike_total_count,
            "rack_total_count": station.rack_total_count,
            "shared": station.shared,
            "availability_ratio": station.availability_ratio,
            "marker_color": station.marker_color,
            "latitude": station.lat,
            "longitude": station.lon,
        }

    @property
    def entity_picture(self):

        station = self._get_station()

        return station.marker_svg if station else None