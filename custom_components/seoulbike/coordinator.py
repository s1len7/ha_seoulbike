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

        state = self.hass.states.get("zone.home")

        if not state:
            return None

        return {
            "lat": state.attributes.get("latitude"),
            "lon": state.attributes.get("longitude"),
        }

    async def _async_update_data(self):

        stations = await self.api_client.get_all_stations()

        home = self._get_home()

        if not home:
            return {
                "stations": [],
                "top_stations": [],
                "nearest": None
            }

        enriched = []

        for s in stations:

            dist = distance(
                home["lat"],
                home["lon"],
                s["lat"],
                s["lon"]
            )

            s["distance_km"] = dist
            enriched.append(s)

        enriched.sort(key=lambda x: x["distance_km"])

        return {
            "stations": enriched,
            "top_stations": enriched[:self.top_n],
            "nearest": enriched[0] if enriched else None
        }