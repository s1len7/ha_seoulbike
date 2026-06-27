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

        for entity in new_entities:
            entity.async_write_ha_state()

    create_entities()

    coordinator.async_add_listener(create_entities)


class SeoulBikeTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator, station_id, station):

        super().__init__(coordinator)

        self._station_id = station_id
        self._station = station

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{station_id}"
        self._attr_name = station.get("name") or station_id

        # 🚲 mdi 유지 (요구사항)
        self._attr_icon = "mdi:bicycle"

        # 지도 필수
        self._attr_source_type = "gps"

    # 📍 위치
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

    # 📊 상태 (자전거 수)
    @property
    def state(self):
        try:
            return int(self._get_station().get("bikes") or 0)
        except Exception:
            return 0

    # 🎨 핵심: 상태 기반 색상 (mdi에도 적용됨)
    @property
    def icon_color(self):

        s = self._get_station()

        try:
            bikes = int(s.get("bikes") or 0)
            racks = int(s.get("racks") or 0)
        except Exception:
            bikes = 0
            racks = 0

        ratio = (bikes / racks) if racks else 0

        if bikes == 0:
            return "#e74c3c"   # red
        elif ratio < 0.3:
            return "#f39c12"   # orange
        else:
            return "#2ecc71"   # green

    # 📦 popup 정보
    @property
    def extra_state_attributes(self):

        s = self._get_station()

        return {
            "station_id": s.get("station_id"),
            "name": s.get("name"),
            "distance_km": s.get("distance_km"),
            "bikes": s.get("bikes"),
            "racks": s.get("racks"),
            "availability_ratio": s.get("availability_ratio"),
            "latitude": s.get("lat"),
            "longitude": s.get("lon"),
        }

    # 🔍 최신 데이터
    def _get_station(self):

        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return self._station