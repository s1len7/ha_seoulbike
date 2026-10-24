"""Seoul Bike API."""
# 서울시 공공자전거 따릉이 실시간 대여정보
# https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do

import logging

from .seoul_api import SeoulApi, SeoulApiAuthError, SeoulApiError

_LOGGER = logging.getLogger(__name__)


class SeoulBikeApi(SeoulApi):
    """Seoul Bike API client."""

    SERVICE = "bikeList"

    async def validate_api_key(self) -> bool:
        """Validate Seoul OpenAPI key.

        Raises SeoulApiError when the server cannot be reached.
        """

        try:
            data = await self._request(
                service=self.SERVICE,
                start=1,
                end=5,
                timeout=10,
            )
        except SeoulApiAuthError:
            return False

        bike_data = data.get("rentBikeStatus")
        if not bike_data:
            raise SeoulApiError(
                f"API response missing 'rentBikeStatus': {data.get('RESULT')}"
            )

        result = bike_data.get("RESULT", {})
        code = result.get("CODE")
        message = result.get("MESSAGE")

        if code != "INFO-000":
            raise SeoulApiError(f"API error: {code} ({message})")

        return True

    async def get_all_stations(self) -> list[dict]:
        """Get all bike stations.

        Raises SeoulApiError on request failure or invalid response.
        """

        stations: list[dict] = []

        pages = await self.request_all(self.SERVICE)

        for data in pages:
            bike_data = data.get("rentBikeStatus")
            if not bike_data:
                raise SeoulApiError(
                    f"API response missing 'rentBikeStatus': {data.get('RESULT')}"
                )

            result = bike_data.get("RESULT", {})
            code = result.get("CODE")
            message = result.get("MESSAGE")

            if code != "INFO-000":
                raise SeoulApiError(f"API error: {code} ({message})")

            rows = bike_data.get("row")
            if not isinstance(rows, list):
                raise SeoulApiError("API response 'rentBikeStatus.row' is not a list")

            stations.extend(
                {
                    "station_id": s.get("stationId"),
                    "station_name": s.get("stationName"),
                    "lat": float(s.get("stationLatitude", 0)),
                    "lon": float(s.get("stationLongitude", 0)),
                    "parking_bike_total_count": int(s.get("parkingBikeTotCnt", 0)),
                    "rack_total_count": int(s.get("rackTotCnt", 0)),
                    "shared": int(s.get("shared", 0)),
                }
                for s in rows
                if isinstance(s, dict)
            )

        return stations
