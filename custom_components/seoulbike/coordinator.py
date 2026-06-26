import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.location import distance

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SeoulBikeCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api_client, radius_km=1.0, top_n=3):

        self.hass = hass
        self.api_client = api_client

        self.radius_km = float(radius_km)
        self.top_n = int(top_n)

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    def _get_home(self):

        # 🔥 HA 공식 기준 위치 사용 (zone.home 제거)
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        if lat is None or lon is None:
            return None

        return {
            "lat": float(lat),
            "lon": float(lon),
        }

    async def _async_update_data(self):

        stations = await self.api_client.get_all_stations()

        home = self._get_home()

        if not home or not stations:
            return {
                "stations": [],
                "top_stations": [],
                "nearest": None
            }

        enriched = []

        for s in stations:

            try:
                lat = float(s.get("lat"))
                lon = float(s.get("lon"))

                dist = distance(
                    home["lat"],
                    home["lon"],
                    lat,
                    lon
                )

                s["lat"] = lat
                s["lon"] = lon
                s["distance_km"] = float(dist)

                enriched.append(s)

            except (TypeError, ValueError):
                # 좌표 깨진 데이터 방어
                continue

        enriched.sort(key=lambda x: x.get("distance_km", float("inf")))

        return {
            "stations": enriched,
            "top_stations": enriched[: self.top_n],
            "nearest": enriched[0] if enriched else None
        }