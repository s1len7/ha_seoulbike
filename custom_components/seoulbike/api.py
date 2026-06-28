"""Seoul Bike API."""
# 서울시 공공자전거 따릉이 실시간 대여정보
# https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do
#
# TODO:
# - except Exception 대신 aiohttp.ClientError, asyncio.TimeoutError 등을 구분하여 처리하기

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SeoulBikeApi:
    def __init__(self, api_key: str):
        self._key = api_key

    async def validate_api_key(self) -> bool:
        url = f"http://openapi.seoul.go.kr:8088/{self._key}/json/bikeList/1/5/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        _LOGGER.error(f"API key validation failed: HTTP {resp.status}")
                        return False

                    data = await resp.json()

                    result = data.get("RESULT", {})
                    code = result.get("CODE")
                    message = result.get("MESSAGE")

                    if code != "INFO-000":
                        _LOGGER.error(f"API key validation failed: {code} ({message})")
                        return False

                    if "rentBikeStatus" not in data:
                        _LOGGER.error("API response missing 'rentBikeStatus'")
                        return False

                    return True

        except Exception as err:
            _LOGGER.error(f"API key validation failed: {err}")
            return False

    async def get_all_stations(self) -> list[dict]:
        stations = []
        start = 1
        size = 1000

        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    end = start + size - 1

                    url = f"http://openapi.seoul.go.kr:8088/{self._key}/json/bikeList/{start}/{end}/"

                    async with session.get(url, timeout=30) as resp:
                        if resp.status != 200:
                            _LOGGER.error(f"Failed to fetch stations {start}-{end}: HTTP {resp.status}")
                            return []

                        data = await resp.json()

                    result = data.get("RESULT", {})
                    code = result.get("CODE")
                    message = result.get("MESSAGE")

                    if code != "INFO-000":
                        _LOGGER.error(f"Failed to fetch stations {start}-{end}: {code} ({message})")
                        return []

                    bike_data = data.get("rentBikeStatus")
                    if not bike_data:
                        _LOGGER.error("API response missing 'rentBikeStatus'")
                        return []

                    rows = bike_data.get("row", [])
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

                    if len(rows) < size:
                        break

                    start += size

        except Exception as err:
            _LOGGER.error(f"Failed to fetch station list: {err}")

        return stations