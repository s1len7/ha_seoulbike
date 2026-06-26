import logging

from homeassistant.core import HomeAssistant

from .const import DOMAIN, ZONE_ENTITY_ID

_LOGGER = logging.getLogger(__name__)


class SeoulBikeZoneManager:

    def __init__(self, hass: HomeAssistant, coordinator):
        self.hass = hass
        self.coordinator = coordinator
        self._zone_exists = False

    async def async_init(self):
        await self._sync_from_coordinator()

    async def _sync_from_coordinator(self):

        nearest = self.coordinator.data.get("nearest")

        if not nearest:
            _LOGGER.warning("No nearest station in coordinator data")
            return

        lat = nearest.get("lat")
        lon = nearest.get("lon")
        name = nearest.get("name", "SeoulBike Nearest")

        if lat is None or lon is None:
            _LOGGER.warning("Invalid lat/lon from coordinator")
            return

        await self._upsert_zone(name, float(lat), float(lon))

    async def _upsert_zone(self, name: str, lat: float, lon: float):

        if not self._zone_exists:
            await self._create_zone(name, lat, lon)
            self._zone_exists = True
        else:
            await self._update_zone(name, lat, lon)

    async def _create_zone(self, name: str, lat: float, lon: float):

        _LOGGER.info("Creating zone")

        await self.hass.services.async_call(
            "zone",
            "create",
            {
                "name": "SeoulBike Nearest Station",
                "latitude": lat,
                "longitude": lon,
                "radius": 25,
                "icon": "mdi:bicycle",
            },
            blocking=True,
        )

    async def _update_zone(self, name: str, lat: float, lon: float):

        await self.hass.services.async_call(
            "zone",
            "update",
            {
                "entity_id": ZONE_ENTITY_ID,
                "latitude": lat,
                "longitude": lon,
                "radius": 25,
            },
            blocking=True,
        )