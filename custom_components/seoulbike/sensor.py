import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        SeoulBikeNearest(coordinator),
        SeoulBikeTopN(coordinator),
    ])


class SeoulBikeNearest(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_name = "SeoulBike Nearest"
        self._attr_unique_id = "seoulbike_nearest"
        self._attr_icon = "mdi:bicycle"

    @property
    def state(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return None

        return nearest.get("name")

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        nearest = data.get("nearest")

        if not nearest:
            return {}

        return {
            "distance_km": float(nearest.get("distance_km", 0.0)),
            "bikes": int(nearest.get("bikes", 0)),
            "racks": int(nearest.get("racks", 0)),
            "station_id": nearest.get("id"),
        }


class SeoulBikeTopN(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_name = "SeoulBike Top N"
        self._attr_unique_id = "seoulbike_top_n"
        self._attr_icon = "mdi:bicycle"

    @property
    def state(self):

        data = self.coordinator.data or {}

        top = data.get("top_stations", [])

        return len(top)

    @property
    def extra_state_attributes(self):

        data = self.coordinator.data or {}
        top = data.get("top_stations", [])

        cleaned = []

        for s in top:

            try:
                cleaned.append({
                    "name": s.get("name"),
                    "distance_km": float(s.get("distance_km", 0.0)),
                    "bikes": int(s.get("bikes", 0)),
                    "racks": int(s.get("racks", 0)),
                    "id": s.get("id"),
                })
            except (TypeError, ValueError):
                continue

        return {
            "stations": cleaned
        }