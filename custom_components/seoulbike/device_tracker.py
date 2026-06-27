from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    existing = {}  # station_id -> entity

    def create_entity(station):
        return SeoulBikeStationTracker(coordinator, station)

    def setup_initial():
        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:
            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in existing:
                continue

            entity = create_entity(s)
            existing[station_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    def handle_update():
        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:
            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in existing:
                continue

            entity = create_entity(s)
            existing[station_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    setup_initial()
    coordinator.async_add_listener(handle_update)


class SeoulBikeStationTracker(TrackerEntity, CoordinatorEntity):

    def __init__(self, coordinator, station):

        CoordinatorEntity.__init__(self, coordinator)

        self._station_id = station.get("station_id")

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{self._station_id}"
        self._attr_name = station.get("name") or self._station_id

        self._attr_icon = "mdi:bicycle"

    # 📍 위치
    @property
    def latitude(self):
        station = self._get_station()
        return station.get("lat")

    @property
    def longitude(self):
        station = self._get_station()
        return station.get("lon")

    # 📌 상태 = 자전거 수
    @property
    def state(self):
        station = self._get_station()

        try:
            return max(int(station.get("bikes") or 0), 0)
        except (TypeError, ValueError):
            return 0

    # 📌 상세 정보
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

    @property
    def source_type(self):
        return "gps"

    # 내부에서 항상 최신 coordinator 기준으로 station 가져오기
    def _get_station(self):
        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return {}