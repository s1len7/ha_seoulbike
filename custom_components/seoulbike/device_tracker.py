from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []
    known_ids = set()

    def create_entities():
        data = coordinator.data or {}
        stations = data.get("top_stations", [])

        new_entities = []

        for s in stations:
            station_id = s.get("station_id")
            if not station_id:
                continue

            if station_id in known_ids:
                continue

            entity = SeoulBikeStationTracker(coordinator, s)
            known_ids.add(station_id)
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    # 초기 생성
    create_entities()

    # 업데이트 시 신규만 추가
    def _update_listener():
        create_entities()

    coordinator.async_add_listener(_update_listener)


class SeoulBikeStationTracker(TrackerEntity, CoordinatorEntity):

    def __init__(self, coordinator, station):

        CoordinatorEntity.__init__(self, coordinator)

        # 🔥 station을 "고정 저장" (중요: 지도 안정성 핵심)
        self._station = station

        self._station_id = station.get("station_id")

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{self._station_id}"
        self._attr_name = station.get("name") or self._station_id

        self._attr_icon = "mdi:bicycle"

    # 📍 latitude (필수 - None 절대 금지)
    @property
    def latitude(self):
        station = self._get_station()
        try:
            return float(station.get("lat"))
        except (TypeError, ValueError):
            return None

    # 📍 longitude (필수 - None 절대 금지)
    @property
    def longitude(self):
        station = self._get_station()
        try:
            return float(station.get("lon"))
        except (TypeError, ValueError):
            return None

    # 📌 state = 자전거 수
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

    # 🔥 coordinator 변화에도 안전하게 station 유지
    def _get_station(self):
        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        # fallback: 초기값 유지
        return self._station or {}