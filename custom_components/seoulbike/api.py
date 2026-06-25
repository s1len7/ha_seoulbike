"""API helpers for Seoul Bike."""

from __future__ import annotations

import aiohttp

from haversine import haversine


class SeoulBikeApi:
    def __init__(self, seoul_api_key: str):
        self._seoul_api_key = seoul_api_key

    async def validate_api_key(self) -> bool:
        url = f"http://openapi.seoul.go.kr:8088/{self._seoul_api_key}/json/bikeList/1/5/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return False

                    data = await response.json()

                    return "rentBikeStatus" in data

        except Exception:
            return False

    async def get_all_stations(self) -> list[dict]:
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

                bike_status = data.get("rentBikeStatus")

                if not bike_status:
                    break

                stations.extend(
                    {
                        "station_id": station["stationId"],
                        "station_name": station["stationName"],
                        "latitude": float(station["stationLatitude"]),
                        "longitude": float(station["stationLongitude"]),
                    }
                    for station in bike_status
                )

                if len(bike_status) < page_size:
                    break

                start_index += page_size

        return stations

    async def nearest_station_distance(
        self,
        latitude: float,
        longitude: float,
    ) -> float | None:

        stations = await self.get_all_stations()

        if not stations:
            return None

        nearest_distance = min(
            haversine(
                (latitude, longitude),
                (
                    station["latitude"],
                    station["longitude"],
                ),
            )
            for station in stations
        )

        return nearest_distance