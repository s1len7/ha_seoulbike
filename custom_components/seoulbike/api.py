"""API helpers for Seoul Bike."""

from __future__ import annotations

import aiohttp
from haversine import haversine


class SeoulBikeApi:
    def __init__(self, seoul_api_key: str):
        self._seoul_api_key = seoul_api_key

    async def validate_api_key(self) -> bool:
        """API 키 유효성 체크"""
        url = f"http://openapi.seoul.go.kr:8088/{self._seoul_api_key}/json/bikeList/1/5/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return False

                    data = await response.json()

                    bike_data = data.get("rentBikeStatus")
                    if not bike_data:
                        return False

                    # 정상 응답 구조 체크
                    return "row" in bike_data

        except Exception:
            return False

    async def get_all_stations(self) -> list[dict]:
        """전체 따릉이 대여소 목록 가져오기"""
        stations = []

        start_index = 1
        page_size = 1000

        async with aiohttp.ClientSession() as session:

            while True:
                end_index = start_index + page_size - 1

                url = f"http://openapi.seoul.go.kr:8088/{self._seoul_api_key}/json/bikeList/{start_index}/{end_index}/"

                async with session.get(url, timeout=30) as response:
                    response.raise_for_status()
                    data = await response.json()

                bike_data = data.get("rentBikeStatus")

                if not bike_data:
                    break

                # 핵심: 실제 데이터는 row 안에 있음
                rows = bike_data.get("row", [])

                if not isinstance(rows, list):
                    break

                stations.extend(
                    {
                        "station_id": station.get("stationId"),
                        "station_name": station.get("stationName"),
                        "latitude": float(station.get("stationLatitude", 0)),
                        "longitude": float(station.get("stationLongitude", 0)),
                    }
                    for station in rows
                    if isinstance(station, dict)
                )

                # 마지막 페이지 체크
                if len(rows) < page_size:
                    break

                start_index += page_size

        return stations

    async def nearest_station_distance(
        self,
        latitude: float,
        longitude: float,
    ) -> float | None:
        """가장 가까운 따릉이 거리 계산 (km)"""

        stations = await self.get_all_stations()

        if not stations:
            return None

        return min(
            haversine(
                (latitude, longitude),
                (station["latitude"], station["longitude"]),
            )
            for station in stations
        )