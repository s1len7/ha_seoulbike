import logging
from datetime import timedelta

from haversine import Unit, haversine
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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

    def _normalize_coord(self, value):

        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _get_home(self):

        lat = self._normalize_coord(self.hass.config.latitude)
        lon = self._normalize_coord(self.hass.config.longitude)

        if lat is None or lon is None:
            _LOGGER.error("[SeoulBike] Home coordinate is invalid")
            return None

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.error(f"[SeoulBike] Home out of range: lat={lat}, lon={lon}")
            return None

        return {
            "lat": lat,
            "lon": lon,
        }

    def _validate_station(self, station):

        lat = self._normalize_coord(station.get("lat"))
        lon = self._normalize_coord(station.get("lon"))

        if lat is None or lon is None:
            return None

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.warning(
                f"[SeoulBike] Invalid coord skipped: "
                f"name={station.get('name')}, lat={lat}, lon={lon}"
            )
            return None

        station["lat"] = lat
        station["lon"] = lon
        station["station_id"] = station.pop("id", None)

        return station

    async def _async_update_data(self):

        stations = await self.api_client.get_all_stations()
        home = self._get_home()

        if not home:
            return {
                "stations": [],
                "top_stations": [],
                "nearest": None,
            }

        enriched = []

        for station in stations:

            station = self._validate_station(station)

            if not station:
                continue

            try:
                dist = haversine(
                    (home["lat"], home["lon"]),
                    (station["lat"], station["lon"]),
                    unit=Unit.KILOMETERS,
                )

                if dist <= self.radius_km:
                    station["distance_km"] = dist
                    enriched.append(station)

            except Exception as e:
                _LOGGER.debug(f"[SeoulBike] Distance calculation failed: {e}")

        enriched.sort(key=lambda x: x["distance_km"])

        return {
            "stations": enriched,
            "top_stations": enriched[: self.top_n],
            "nearest": enriched[0] if enriched else None,
        }