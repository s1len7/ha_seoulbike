"""Seoul Bike API."""

from __future__ import annotations

import aiohttp
from haversine import haversine


class SeoulBikeApi:
    def __init__(self, seoul_api_key: str):
        self._key = seoul_api_key
        raise Exception(f"{__file__}: SeoulBikeApi loaded")

    async def get_all_stations(self) -> list[dict]:
        stations = []
        start = 1
        size = 1000

        async with aiohttp.ClientSession() as session:

            while True:
                end = start + size - 1

                url = f"http://openapi.seoul.go.kr:8088/{self._key}/json/bikeList/{start}/{end}/"

                async with session.get(url, timeout=30) as resp:
                    data = await resp.json()

                bike_data = data.get("rentBikeStatus")
                if not bike_data:
                    break

                rows = bike_data.get("row", [])
                if not isinstance(rows, list):
                    break

                stations.extend(
                    {
                        "id": s.get("stationId"),
                        "name": s.get("stationName"),
                        "lat": float(s.get("stationLatitude", 0)),
                        "lon": float(s.get("stationLongitude", 0)),
                        "bikes": int(s.get("parkingBikeTotCnt", 0)),
                    }
                    for s in rows
                    if isinstance(s, dict)
                )

                if len(rows) < size:
                    break

                start += size

        return stations