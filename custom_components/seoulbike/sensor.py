from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, add_entities):

    coord = hass.data[DOMAIN][entry.entry_id]

    add_entities([
        SeoulBikeNearest(coord),
        SeoulBikeTop5(coord),
    ])


class SeoulBikeNearest(SensorEntity):

    def __init__(self, coord):
        self.coord = coord
        self._attr_name = "SeoulBike Nearest"

    @property
    def state(self):

        d = self.coord.data

        if not d or not d["stations"]:
            return None

        return d["stations"][0]["name"]

    @property
    def extra_state_attributes(self):

        d = self.coord.data

        if not d or not d["stations"]:
            return {}

        s = d["stations"][0]

        return {
            "distance_km": s["distance_km"],
            "bikes": s.get("bikes"),
            "docks": s.get("docks"),
        }


class SeoulBikeTop5(SensorEntity):

    def __init__(self, coord):
        self.coord = coord
        self._attr_name = "SeoulBike Top5"

    @property
    def state(self):

        d = self.coord.data

        if not d:
            return 0

        return len(d.get("top5", []))

    @property
    def extra_state_attributes(self):

        d = self.coord.data

        if not d:
            return {}

        return {"stations": d.get("top5", [])}