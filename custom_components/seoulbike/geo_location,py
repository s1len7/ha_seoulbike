from homeassistant.components.geo_location import GeolocationEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = {}
    last_ids = set()

    def create_entities():
        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:
            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in last_ids:
                continue

            entity = SeoulBikeGeoLocation(coordinator, s)
            last_ids.add(station_id)
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    # 초기 생성
    create_entities()

    # 업데이트 시 추가
    def _update_listener():
        create_entities()

    coordinator.async_add_listener(_update_listener)


class SeoulBikeGeoLocation(CoordinatorEntity, GeolocationEntity):

    def __init__(self, coordinator, station):

        super().__init__(coordinator)

        self._station_id = station.get("station_id")
        self._station = station

        self._attr_unique_id = f"{DOMAIN}.geo_location.{self._station_id}"
        self._attr_name = station.get("name") or self._station_id

    # 📍 latitude
    @property
    def latitude(self):
        station = self._get_station()
        try:
            return float(station.get("lat"))
        except (TypeError, ValueError):
            return None

    # 📍 longitude
    @property
    def longitude(self):
        station = self._get_station()
        try:
            return float(station.get("lon"))
        except (TypeError, ValueError):
            return None

    # 📌 state (지도에서는 설명용)
    @property
    def state(self):
        station = self._get_station()
        return station.get("bikes")

    # 📌 attributes
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

    # 🔥 coordinator fallback 안정성
    def _get_station(self):
        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return self._station or {}