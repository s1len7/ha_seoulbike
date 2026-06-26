from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeNearestTracker(coordinator)
    ])


class SeoulBikeNearestTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_unique_id = "seoulbike_nearest_tracker"
        self._attr_name = "SeoulBike Nearest"

    # ✔ Map 표시 핵심 (무조건 필요)
    @property
    def latitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return float(nearest.get("lat", 0))

    @property
    def longitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return float(nearest.get("lon", 0))

    # ✔ state (Map에는 필수 아님, 하지만 권장)
    @property
    def state(self):
        return "home"

    # ✔ 필수 아님이지만 HA 호환성 위해 유지
    @property
    def source_type(self):
        return "gps"