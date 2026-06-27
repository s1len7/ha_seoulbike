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

        # 🔥 tracker 활성 유지
        for entity in new_entities:
            entity.async_write_ha_state()

    create_entities()

    coordinator.async_add_listener(create_entities)


# =========================
# 🚲 SVG 마커 생성 함수
# =========================
def build_marker_svg(bikes: int, racks: int):

    try:
        bikes = int(bikes or 0)
        racks = int(racks or 0)
    except Exception:
        bikes = 0
        racks = 0

    ratio = (bikes / racks) if racks else 0

    # 🎨 상태별 색상 (테두리)
    if bikes == 0:
        color = "#e74c3c"   # red
    elif ratio < 0.3:
        color = "#f39c12"   # orange
    else:
        color = "#2ecc71"   # green

    svg = f"""
    <svg width="64" height="64" viewBox="0 0 64 64"
         xmlns="http://www.w3.org/2000/svg">

        <!-- outer ring -->
        <circle cx="32" cy="32" r="28"
                fill="white"
                stroke="{color}"
                stroke-width="6"/>

        <!-- bike icon -->
        <text x="32" y="30"
              text-anchor="middle"
              font-size="18"
              fill="#333">🚲</text>

        <!-- number (state) -->
        <text x="32" y="48"
              text-anchor="middle"
              font-size="14"
              font-weight="bold"
              fill="{color}">{bikes}</text>

    </svg>
    """

    return "data:image/svg+xml;charset=utf-8," + svg.replace("\n", "")


# =========================
# 🚲 Tracker Entity
# =========================
class SeoulBikeTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator, station_id, station):

        super().__init__(coordinator)

        self._station_id = station_id
        self._station = station

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{station_id}"
        self._attr_name = station.get("name") or station_id

        # self._attr_icon = "mdi:bicycle"
        # ❌ 기본 mdi 제거 (SVG 마커가 대신함)
        self._attr_icon = "mdi:map-marker"

        # 🔥 Map 인식 필수
        self._attr_source_type = "gps"

    # =========================
    # 📍 위치
    # =========================
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

    # =========================
    # 📊 상태 (잔여 자전거 수)
    # =========================
    @property
    def state(self):
        try:
            return int(self._get_station().get("bikes") or 0)
        except Exception:
            return 0

    # =========================
    # 📦 상세 정보
    # =========================
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

    # =========================
    # 🚲 핵심: 지도 마커 UI
    # =========================
    @property
    def entity_picture(self):

        station = self._get_station()

        bikes = station.get("bikes", 0)
        racks = station.get("racks", 0)

        return build_marker_svg(bikes, racks)

    # =========================
    # 🔍 데이터 최신화
    # =========================
    def _get_station(self):

        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return self._station