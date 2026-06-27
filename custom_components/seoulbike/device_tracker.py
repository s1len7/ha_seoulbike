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

            entity = SeoulBikeTracker(coordinator, station_id)
            entities[station_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    create_entities()
    coordinator.async_add_listener(create_entities)


# =========================
# 🎨 SVG 마커 생성
# =========================
def build_marker_svg(bikes, racks):

    try:
        bikes = int(bikes or 0)
        racks = int(racks or 0)
    except Exception:
        bikes = 0
        racks = 0

    ratio = (bikes / racks) if racks else 0

    if bikes == 0:
        color = "#e74c3c"
    elif ratio < 0.3:
        color = "#f39c12"
    else:
        color = "#2ecc71"

    svg = f"""
    <svg width="64" height="64" viewBox="0 0 64 64"
         xmlns="http://www.w3.org/2000/svg">

        <circle cx="32" cy="32" r="28"
                fill="white"
                stroke="{color}"
                stroke-width="6"/>

        <text x="32" y="30"
              text-anchor="middle"
              font-size="18">🚲</text>

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

    def __init__(self, coordinator, station_id):

        super().__init__(coordinator)

        self._station_id = station_id

        self._attr_unique_id = f"{DOMAIN}.device_tracker.{station_id}"
        self._attr_name = station_id

        # UI용
        self._attr_icon = "mdi:bicycle"

        # 지도 필수
        self._attr_source_type = "gps"

    # 📍 위치
    @property
    def latitude(self):
        s = self._get_station()
        try:
            return float(s.get("lat"))
        except:
            return None

    @property
    def longitude(self):
        s = self._get_station()
        try:
            return float(s.get("lon"))
        except:
            return None

    # 📊 상태
    @property
    def state(self):
        s = self._get_station()
        try:
            return int(s.get("bikes") or 0)
        except:
            return 0

    # 📦 attributes
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

    # 🚲 지도 마커 (핵심)
    @property
    def entity_picture(self):

        s = self._get_station()

        return build_marker_svg(
            s.get("bikes"),
            s.get("racks"),
        )

    # 🔍 최신 데이터
    def _get_station(self):

        data = self.coordinator.data or {}
        stations = data.get("top_stations", [])

        for s in stations:
            if s.get("station_id") == self._station_id:
                return s

        return {}