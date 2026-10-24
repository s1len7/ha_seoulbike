"""Seoul OpenAPI client."""

import asyncio
import json
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)

# 인증키 오류 코드
AUTH_ERROR_CODE = "INFO-100"


class SeoulApiError(Exception):
    """Raised when Seoul OpenAPI request fails."""


class SeoulApiAuthError(SeoulApiError):
    """Raised when Seoul OpenAPI key is invalid."""


class SeoulApi:
    """Base client for Seoul OpenAPI."""

    BASE_URL = "http://openapi.seoul.go.kr:8088"

    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self._key = api_key
        self._session = session

    async def _request(
        self,
        service: str,
        start: int,
        end: int,
        timeout: int = 30,
    ) -> dict:
        """Request a single page from Seoul OpenAPI."""

        url = f"{self.BASE_URL}/{self._key}/json/{service}/{start}/{end}/"

        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status != 200:
                    raise SeoulApiError(
                        f"Failed to request {service} {start}-{end}: HTTP {resp.status}"
                    )

                text = await resp.text()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise SeoulApiError(
                f"Failed to request {service} {start}-{end}: {err!r}"
            ) from err

        try:
            data = json.loads(text)
        except ValueError as err:
            # 인증키 오류는 json을 요청해도 XML로 응답함
            if AUTH_ERROR_CODE in text:
                raise SeoulApiAuthError("Invalid API key") from err
            raise SeoulApiError(
                f"Failed to parse {service} {start}-{end} response"
            ) from err

        if data.get("RESULT", {}).get("CODE") == AUTH_ERROR_CODE:
            raise SeoulApiAuthError("Invalid API key")

        return data

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
