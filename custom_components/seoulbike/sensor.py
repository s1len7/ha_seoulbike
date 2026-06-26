from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        SeoulBikeNearest(coordinator),
        SeoulBikeTop5(coordinator),
    ])


class SeoulBikeNearest(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Nearest"

    @property
    def state(self):

        data = self.coordinator.data

        if not data or not data["stations"]:
            return None

        return data["stations"][0]["name"]

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data

        if not data or not data["stations"]:
            return {}

        s = data["stations"][0]

        return {
            "distance_km": s.get("distance_km"),
            "bikes": s.get("bikes"),
            "docks": s.get("docks"),
        }


class SeoulBikeTop5(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Top5"

    @property
    def state(self):

        data = self.coordinator.data

        if not data:
            return 0

        return len(data.get("top5", []))

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data

        if not data:
            return {}

        return {
            "stations": data.get("top5", [])
        }