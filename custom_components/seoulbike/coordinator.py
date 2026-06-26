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

    # -----------------------------
    # SAFE CONVERT
    # -----------------------------
    def _normalize_coord(self, value):

        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    # -----------------------------
    # HOME (HA CONFIG 기준)
    # -----------------------------
    def _get_home(self):

        lat = self._normalize_coord(self.hass.config.latitude)
        lon = self._normalize_coord(self.hass.config.longitude)

        if lat is None or lon is None:
            _LOGGER.error("[SeoulBike] Home coordinate is invalid")
            return None

        # sanity check
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.error(f"[SeoulBike] Home out of range: lat={lat}, lon={lon}")
            return None

        return {"lat": lat, "lon": lon}

    # -----------------------------
    # STATION VALIDATION
    # -----------------------------
    def _validate_station(self, s):

        lat = self._normalize_coord(s.get("lat"))
        lon = self._normalize_coord(s.get("lon"))

        if lat is None or lon is None:
            return None

        # WGS84 sanity check
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.warning(
                f"[SeoulBike] Invalid coord skipped: "
                f"name={s.get('name')}, lat={lat}, lon={lon}"
            )
            return None

        # lat/lon swap detection (heuristic)
        if abs(lat) > 90 and abs(lon) <= 90:
            _LOGGER.warning(
                f"[SeoulBike] Lat/Lon swap detected fixed: "
                f"name={s.get('name')}, lat={lat}, lon={lon}"
            )
            lat, lon = lon, lat

        s["lat"] = lat
        s["lon"] = lon

        return s

    # -----------------------------
    # UPDATE
    # -----------------------------
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

        for s in stations:

            s = self._validate_station(s)
            if not s:
                continue

            try:
                dist = distance(
                    float(home["lat"]),
                    float(home["lon"]),
                    float(s["lat"]),
                    float(s["lon"]),
                )

                dist = float(dist)

                # 🚨 폭주 방지 (서울 기준 현실 컷)
                if dist > 200:
                    _LOGGER.error(
                        f"[SeoulBike] CORRUPT DISTANCE DETECTED: {dist} km | "
                        f"home={home} | station={s.get('name')} | "
                        f"lat={s['lat']} lon={s['lon']}"
                    )
                    continue

                if dist < 0:
                    continue

                s["distance_km"] = dist
                enriched.append(s)

            except Exception as e:
                _LOGGER.debug(f"[SeoulBike] distance calc error: {e}")
                continue

        enriched.sort(key=lambda x: x.get("distance_km", float("inf")))

        # nearest sample log
        if enriched:
            _LOGGER.info(
                f"[SeoulBike] NEAREST: {enriched[0].get('name')} "
                f"= {enriched[0].get('distance_km')} km"
            )

        return {
            "stations": enriched,
            "top_stations": enriched[: self.top_n],
            "nearest": enriched[0] if enriched else None,
        }