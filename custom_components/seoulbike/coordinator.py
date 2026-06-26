from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from haversine import haversine

from .const import DOMAIN, DEFAULT_RADIUS_KM, TOP_N


class SeoulBikeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, radius_km=DEFAULT_RADIUS_KM):
        self.api_client = api_client
        self.radius_km = radius_km

        super().__init__(
            hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        stations = await self.api_client.get_stations()

        user_location = await self.api_client.get_user_location()

        enriched = []

        for s in stations:
            dist = haversine(
                (user_location["lat"], user_location["lon"]),
                (s["lat"], s["lon"])
            )

            s["distance_km"] = dist

            if dist <= self.radius_km:
                enriched.append(s)

        enriched.sort(key=lambda x: x["distance_km"])

        return {
            "stations": enriched,
            "top5": enriched[:TOP_N] if enriched else []
        }