"""Seoul Bike API."""
# 서울시 공공자전거 따릉이 실시간 대여정보
# https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do

import logging

from .seoul_api import SeoulApi

_LOGGER = logging.getLogger(__name__)


class SeoulBikeApi(SeoulApi):
    """Seoul Bike API client."""

    SERVICE = "bikeList"

    async def validate_api_key(self) -> bool:
        """Validate Seoul OpenAPI key."""

        data = await self._request(
            service=self.SERVICE,
            start=1,
            end=5,
            timeout=10,
        )

        if data is None:
            return False

        bike_data = data.get("rentBikeStatus")
        if not bike_data:
            _LOGGER.error("API response missing 'rentBikeStatus'")
            return False

        result = bike_data.get("RESULT", {})
        code = result.get("CODE")
        message = result.get("MESSAGE")

        if code != "INFO-000":
            _LOGGER.error(f"API key validation failed: {code} ({message})")
            return False

        return True

    async def get_all_stations(self) -> list[dict]:
        """Get all bike stations."""

        stations: list[dict] = []

        pages = await self.request_all(self.SERVICE)
        if not pages:
            return []

        for data in pages:
            bike_data = data.get("rentBikeStatus")
            if not bike_data:
                _LOGGER.error("API response missing 'rentBikeStatus'")
                return []

            result = bike_data.get("RESULT", {})
            code = result.get("CODE")
            message = result.get("MESSAGE")

            if code != "INFO-000":
                _LOGGER.error(f"API error: {code} ({message})")
                return []

            rows = bike_data.get("row")
            if not isinstance(rows, list):
                _LOGGER.error("API response 'rentBikeStatus.row' is not a list")
                return []

            stations.extend(
                {
                    "station_id": s.get("stationId"),
                    "station_name": s.get("stationName"),
                    "lat": float(s.get("stationLatitude", 0)),
                    "lon": float(s.get("stationLongitude", 0)),
                    "bikes": int(s.get("parkingBikeTotCnt", 0)),
                    "racks": int(s.get("rackTotCnt", 0)),
                    "availability_ratio": int(s.get("shared", 0)),
                }
                for s in rows
                if isinstance(s, dict)
            )

        return stations