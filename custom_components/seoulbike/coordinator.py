from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.location import distance

from .const import TOP_N


class SeoulBikeCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api, radius_km):

        self.hass = hass
        self.api = api
        self.radius_km = radius_km

        super().__init__(
            hass,
            logger=None,
            name="seoulbike",
            update_interval=timedelta(seconds=60),
        )

    def _home(self):

        s = self.hass.states.get("zone.home")

        if not s:
            return None

        return s.attributes.get("latitude"), s.attributes.get("longitude")

    async def _async_update_data(self):

        stations = await self.api.get_stations()

        home = self._home()

        if not home:
            return {"stations": [], "top5": []}

        hx, hy = home

        result = []

        for s in stations:

            d = distance(hx, hy, s["lat"], s["lon"])

            s["distance_km"] = d

            if d <= self.radius_km:
                result.append(s)

        result.sort(key=lambda x: x["distance_km"])

        return {
            "stations": result,
            "top5": result[:TOP_N]
        }