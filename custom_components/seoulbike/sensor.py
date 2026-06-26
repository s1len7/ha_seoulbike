from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        SeoulBikeNearest(coordinator),
        SeoulBikeTopN(coordinator),
    ])


class SeoulBikeNearest(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Nearest"

    @property
    def unique_id(self):
        return "seoulbike_nearest"

    @property
    def state(self):

        data = self.coordinator.data

        nearest = data.get("nearest") if data else None

        if not nearest:
            return None

        return nearest.get("name")

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data

        nearest = data.get("nearest") if data else None

        if not nearest:
            return {}

        return {
            "distance_km": nearest.get("distance_km"),
            "bikes": nearest.get("bikes"),
            "docks": nearest.get("docks"),
        }


class SeoulBikeTopN(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "SeoulBike Top N"

    @property
    def unique_id(self):
        return "seoulbike_top_n"

    @property
    def state(self):

        data = self.coordinator.data

        if not data:
            return 0

        return len(data.get("top_stations", []))

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data

        if not data:
            return {}

        return {
            "stations": data.get("top_stations", [])
        }