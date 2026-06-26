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

        self._attr_unique_id = f"{DOMAIN}.seoulbike_tracker_nearest_station"
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
        return nearest.get("name", "unknown")

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