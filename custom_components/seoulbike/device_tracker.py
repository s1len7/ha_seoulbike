from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeNearestStationTracker(coordinator)
    ])


class SeoulBikeNearestStationTracker(TrackerEntity, CoordinatorEntity):

    def __init__(self, coordinator):
        CoordinatorEntity.__init__(self, coordinator)

        self._attr_unique_id = f"{DOMAIN}.device_tracker.nearest_station"
        self._attr_name = self._attr_unique_id
        self._attr_icon = "mdi:bicycle"

    # 📍 위치
    @property
    def latitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lat")

    @property
    def longitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lon")

    # 📌 상태 (Map 표시용 + 의미값)
    @property
    def state(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})

        bikes = nearest.get("bikes", 0)

        try:
            return int(bikes)
        except (TypeError, ValueError):
            return 0

    # 📌 popup 정보
    @property
    def extra_state_attributes(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})

        return {
            "station_id": nearest.get("station_id"),
            "name": nearest.get("name"),
            "distance_km": nearest.get("distance_km"),
            "bikes": nearest.get("bikes"),
            "racks": nearest.get("racks"),
            "latitude": nearest.get("lat"),
            "longitude": nearest.get("lon"),
        }

    @property
    def source_type(self):
        return "gps"
    
    # # 🚲 핵심: Map marker 이미지 (S 제거용)
    # @property
    # def entity_picture(self):
    #     bikes = (self.coordinator.data or {}).get("nearest", {}).get("bikes", 0)

    #     try:
    #         bikes = int(bikes)
    #     except (TypeError, ValueError):
    #         bikes = 0

    #     # ✔ 상태에 따라 아이콘 변화
    #     if bikes == 0:
    #         # 비어있음 → 빨간 자전거
    #         return "https://cdn-icons-png.flaticon.com/512/854/854878.png"
    #     elif bikes <= 3:
    #         # 부족
    #         return "https://cdn-icons-png.flaticon.com/512/854/854894.png"
    #     else:
    #         # 충분
    #         return "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6b2.png"
