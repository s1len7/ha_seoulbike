from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeTracker(coordinator)
    ])


class SeoulBikeTracker(CoordinatorEntity, TrackerEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "seoulbike_tracker"
        self._attr_name = "SeoulBike Nearest"

    @property
    def state(self):
        return "home"

    @property
    def latitude(self):
        data = self.coordinator.data.get("nearest", {})
        return float(data.get("lat", 0))

    @property
    def longitude(self):
        data = self.coordinator.data.get("nearest", {})
        return float(data.get("lon", 0))

    @property
    def source_type(self):
        return "gps"