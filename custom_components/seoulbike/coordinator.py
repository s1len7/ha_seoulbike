from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.location import distance

from .const import DOMAIN, TOP_N


class SeoulBikeCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api_client, radius_km=1.0):

        self.hass = hass
        self.api_client = api_client
        self.radius_km = float(radius_km)

        super().__init__(
            hass,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    def _get_home(self):

        state = self.hass.states.get("zone.home")

        if not state:
            return None

        return {
            "lat": state.attributes.get("latitude"),
            "lon": state.attributes.get("longitude"),
        }

    async def _async_update_data(self):

        stations = await self.api_client.get_stations()

        home = self._get_home()

        if not home:
            return {"stations": [], "top5": []}

        enriched = []

        for s in stations:

            dist = distance(
                home["lat"],
                home["lon"],
                s["lat"],
                s["lon"]
            )

            s["distance_km"] = dist

            if dist <= self.radius_km:
                enriched.append(s)

        enriched.sort(key=lambda x: x["distance_km"])

        return {
            "stations": enriched,
            "top5": enriched[:TOP_N]
        }