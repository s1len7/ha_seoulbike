from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeNearestTracker(coordinator)
    ])


class SeoulBikeNearestTracker(TrackerEntity, CoordinatorEntity):

    def __init__(self, coordinator):
        CoordinatorEntity.__init__(self, coordinator)

        self._attr_unique_id = "seoulbike_nearest_tracker"
        self._attr_name = "SeoulBike Nearest Station"
        self._attr_icon = "mdi:bicycle"   # 👈 이거 추가

    # 📍 지도 좌표
    @property
    def latitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lat")

    @property
    def longitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lon")

    # 📌 상태
    @property
    def state(self):
        return (self.coordinator.data or {}).get("nearest", {}).get("name", "unknown")

    # 📌 Map popup에 표시될 핵심 정보
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