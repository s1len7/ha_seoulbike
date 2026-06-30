"""Seoul OpenAPI client."""

#
# TODO:
# - except Exception 대신 aiohttp.ClientError, asyncio.TimeoutError 등을 구분하여 처리하기
#

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SeoulApi:
    """Base client for Seoul OpenAPI."""

    BASE_URL = "http://openapi.seoul.go.kr:8088"

    def __init__(self, api_key: str):
        self._key = api_key

    async def _request(
        self,
        service: str,
        start: int,
        end: int,
        timeout: int = 30,
    ) -> dict | None:
        """Request a single page from Seoul OpenAPI."""

        url = f"{self.BASE_URL}/{self._key}/json/{service}/{start}/{end}/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status != 200:
                        _LOGGER.error(f"Failed to request {service} {start}-{end}: HTTP {resp.status}")
                        return None

                    return await resp.json()

        except Exception as err:
            _LOGGER.error(f"Failed to request {service} {start}-{end}: {err}")
            return None

    async def request_all(
        self,
        service: str,
        page_size: int = 1000,
    ) -> list[dict]:
        """Request all pages from a Seoul OpenAPI service."""

        pages: list[dict] = []

        start = 1

        while True:
            end = start + page_size - 1

            data = await self._request(
                service=service,
                start=start,
                end=end,
            )

            if data is None:
                return []

            pages.append(data)

            service_data = next(iter(data.values()), None)
            if not isinstance(service_data, dict):
                return pages

            rows = service_data.get("row")
            if not isinstance(rows, list):
                return pages

            if len(rows) < page_size:
                break

            start += page_size

        return pages