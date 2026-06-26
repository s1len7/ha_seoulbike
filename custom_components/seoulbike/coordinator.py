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
    # HOME 좌표 (HA 기준)
    # -----------------------------
    def _get_home(self):

        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return None

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.warning(f"[SeoulBike] Invalid HOME coords: lat={lat}, lon={lon}")
            return None

        return {"lat": lat, "lon": lon}

    # -----------------------------
    # 좌표 검증
    # -----------------------------
    def _validate_station(self, s):

        try:
            lat = float(s.get("lat"))
            lon = float(s.get("lon"))
        except (TypeError, ValueError):
            return None

        # 기본 범위 체크
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.debug(f"[SeoulBike] Out of range station skipped: {s}")
            return None

        # 🔥 lat/lon swap 감지 (한국 기준 휴리스틱)
        # lat이 100 이상이고 lon이 40 근처면 swap 의심
        if lat > 90 and abs(lon) < 90:
            _LOGGER.warning(
                f"[SeoulBike] Lat/Lon swapped detected -> fixing: lat={lat}, lon={lon}"
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
            _LOGGER.error("[SeoulBike] Home coordinates invalid")
            return {"stations": [], "top_stations": [], "nearest": None}

        enriched = []

        for s in stations:

            s = self._validate_station(s)
            if not s:
                continue

            try:
                dist = distance(
                    home["lat"],
                    home["lon"],
                    s["lat"],
                    s["lon"]
                )

                dist = float(dist)

                # 🔥 비정상 거리 탐지 로그
                if dist > 100:
                    _LOGGER.warning(
                        f"[SeoulBike] Large distance detected: {dist} km "
                        f"(home={home}, station={s.get('name')})"
                    )

                s["distance_km"] = dist
                enriched.append(s)

            except Exception as e:
                _LOGGER.debug(f"[SeoulBike] Distance calc error: {e}")
                continue

        enriched.sort(key=lambda x: x.get("distance_km", float("inf")))

        # 🔥 샘플 로그 (첫 실행 때만 확인용)
        if enriched:
            _LOGGER.info(
                f"[SeoulBike] NEAREST SAMPLE: "
                f"{enriched[0].get('name')} = {enriched[0].get('distance_km')} km"
            )

        return {
            "stations": enriched,
            "top_stations": enriched[: self.top_n],
            "nearest": enriched[0] if enriched else None,
        }