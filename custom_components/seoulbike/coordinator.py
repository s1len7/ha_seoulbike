import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util.location import distance
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .src.seoul_api import SeoulApiAuthError, SeoulApiError
from .src.seoulbike_station import SeoulBikeStation

_LOGGER = logging.getLogger(__name__)


class SeoulBikeCoordinator(DataUpdateCoordinator):
    """전체 대여소를 한 번에 받아 모든 하위 항목이 함께 쓴다."""

    def __init__(self, hass, config_entry, api_client):

        self.api_client = api_client

        super().__init__(
            hass,
            logger=_LOGGER,
            config_entry=config_entry,
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

    def _validate_station(self, station):

        lat = self._normalize_coord(station.get("lat"))
        lon = self._normalize_coord(station.get("lon"))

        if lat is None or lon is None:
            return None

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            _LOGGER.debug(
                f"[SeoulBike] Invalid coord skipped: name={station.get('station_name')}, lat={lat}, lon={lon}"
            )
            return None

        return SeoulBikeStation(
            station_id=station["station_id"],
            station_name=station["station_name"],
            lat=lat,
            lon=lon,
            rack_total_count=int(station["rack_total_count"]),
            parking_bike_total_count=int(station["parking_bike_total_count"]),
            shared=int(station["shared"]),
        )

    async def _async_update_data(self):

        try:
            stations = await self.api_client.get_all_stations()
        except SeoulApiAuthError as err:
            # HA가 "재인증 필요" 알림을 띄움
            raise ConfigEntryAuthFailed(str(err)) from err
        except SeoulApiError as err:
            raise UpdateFailed(str(err)) from err

        stations_by_id = {}

        for station in stations:

            station = self._validate_station(station)

            if station:
                stations_by_id[station.station_id] = station

        _LOGGER.debug(f"stations fetched: {len(stations)}, valid: {len(stations_by_id)}")

        return {"stations_by_id": stations_by_id}

    def get_station(self, station_id):

        data = self.data or {}

        return data.get("stations_by_id", {}).get(station_id)

    def get_zone_location(self, zone_id):
        """지역(zone) 엔티티의 좌표. 지역이 없거나 좌표가 없으면 None."""

        state = self.hass.states.get(zone_id)

        if state is None:
            return None

        lat = self._normalize_coord(state.attributes.get("latitude"))
        lon = self._normalize_coord(state.attributes.get("longitude"))

        if lat is None or lon is None:
            return None

        return lat, lon

    def distance_km(self, zone_id, station):

        location = self.get_zone_location(zone_id)

        if location is None or station is None:
            return None

        return distance(location[0], location[1], station.lat, station.lon) / 1000.0

    def find_nearby(self, zone_id, radius_km, top_n):
        """지역 기준 반경 안의 대여소를 가까운 순으로 top_n개. [(대여소, 거리km)]"""

        location = self.get_zone_location(zone_id)

        if location is None:
            return []

        data = self.data or {}
        nearby = []

        for station in data.get("stations_by_id", {}).values():

            dist = distance(location[0], location[1], station.lat, station.lon) / 1000.0

            if dist <= radius_km:
                nearby.append((station, dist))

        nearby.sort(key=lambda item: item[1])

        return nearby[:top_n]
