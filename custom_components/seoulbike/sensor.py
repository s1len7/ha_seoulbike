from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        SeoulBikeNearestSensor(coordinator),
        SeoulBikeTop5Sensor(coordinator),
    ])


class SeoulBikeNearestSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Nearest Station"

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

        nearest = data["stations"][0]

        return {
            "distance_km": nearest["distance_km"],
            "bikes": nearest.get("bikes"),
            "docks": nearest.get("docks"),
        }


class SeoulBikeTop5Sensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Top 5 Stations"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        return len(data.get("top5", []))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}

        return {
            "stations": data.get("top5", [])
        }