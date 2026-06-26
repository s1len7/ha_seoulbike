from homeassistant.components.device_tracker import TrackerEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        SeoulBikeNearestTracker(coordinator)
    ])


class SeoulBikeNearestTracker(TrackerEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator

        self._attr_unique_id = "seoulbike_nearest_tracker"
        self._attr_name = "SeoulBike Nearest"

    @property
    def latitude(self):
        return (self.coordinator.data or {}).get("nearest", {}).get("lat")

    @property
    def longitude(self):
        return (self.coordinator.data or {}).get("nearest", {}).get("lon")

    @property
    def state(self):
        return "home"

    @property
    def source_type(self):
        return "gps"