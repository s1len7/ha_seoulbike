"""Seoul Bike API."""

import aiohttp


class SeoulBikeApi:
    def __init__(self, api_key: str):
        self._key = api_key

    async def validate_api_key(self) -> bool:
        url = f"http://openapi.seoul.go.kr:8088/{self._key}/json/bikeList/1/5/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        return False

                    data = await resp.json()

                    return "rentBikeStatus" in data

        except Exception:
            return False

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
                        "racks": int(s.get("rackTotCnt", 0)),
                        "availability_ratio": int(s.get("shared", 0)),
                    }
                    for s in rows
                    if isinstance(s, dict)
                )

                if len(rows) < size:
                    break

                start += size

        return stations