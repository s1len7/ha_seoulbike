import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class SeoulBikeZoneManager:

    def __init__(self, hass: HomeAssistant, coordinator):
        self.hass = hass
        self.coordinator = coordinator

    async def async_init(self):
        await self._sync()

    async def _sync(self):

        nearest = self.coordinator.data.get("nearest")

        if not nearest:
            return

        lat = nearest.get("lat")
        lon = nearest.get("lon")

        if lat is None or lon is None:
            return

        # 👉 device_tracker 상태로 생성
        self.hass.states.async_set(
            "device_tracker.seoulbike_nearest",
            "home",
            {
                "latitude": float(lat),
                "longitude": float(lon),
                "source_type": "gps",
                "friendly_name": "SeoulBike Nearest Station"
            }
        )