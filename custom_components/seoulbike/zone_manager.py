import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ZONE_ENTITY_ID = "zone.seoulbike_nearest_station"
SENSOR_ENTITY_ID = "sensor.nearest_station"  # CoordinatorEntity name 기반


async def async_setup_zone_manager(hass: HomeAssistant, entry):
    """Entry point from __init__.py"""

    manager = SeoulBikeZoneManager(hass)

    await manager.async_init()

    hass.data[DOMAIN]["zone_manager"] = manager

    return True


class SeoulBikeZoneManager:
    """Moves a Home Assistant Zone based on nearest station sensor."""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._unsub = None
        self._zone_exists = False

    async def async_init(self):
        """Start listening sensor changes."""

        self._unsub = async_track_state_change_event(
            self.hass,
            SENSOR_ENTITY_ID,
            self._handle_state_change,
        )

        # 초기 1회 동기화
        await self._sync_from_sensor()

    async def async_unload(self):
        if self._unsub:
            self._unsub()

    @callback
    async def _handle_state_change(self, event):
        """Triggered when sensor updates."""

        await self._sync_from_sensor()

    async def _sync_from_sensor(self):
        """Read sensor and update zone."""

        state = self.hass.states.get(SENSOR_ENTITY_ID)

        if not state:
            _LOGGER.warning("Nearest station sensor not found")
            return

        attrs = state.attributes or {}

        lat = attrs.get("lat")
        lon = attrs.get("lon")
        name = attrs.get("name", "SeoulBike Nearest")

        if lat is None or lon is None:
            _LOGGER.warning("Invalid lat/lon from sensor")
            return

        # Zone 생성 or 업데이트
        await self._upsert_zone(name, float(lat), float(lon))

    async def _upsert_zone(self, name: str, lat: float, lon: float):
        """Create zone once, then update."""

        if not self._zone_exists:
            await self._create_zone(name, lat, lon)
            self._zone_exists = True
        else:
            await self._update_zone(name, lat, lon)

    async def _create_zone(self, name: str, lat: float, lon: float):
        """Create moving zone."""

        _LOGGER.info("Creating zone %s", ZONE_ENTITY_ID)

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
        """Update existing zone."""

        _LOGGER.debug("Updating zone %s", ZONE_ENTITY_ID)

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