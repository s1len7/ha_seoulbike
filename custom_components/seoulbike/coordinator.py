"""Coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from haversine import haversine

_LOGGER = logging.getLogger(__name__)


class SeoulBikeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, lat, lon):
        super().__init__(
            hass,
            _LOGGER,
            name="seoulbike",
            update_interval=timedelta(minutes=1),
        )

        self.api = api
        self.lat = lat
        self.lon = lon

    async def _async_update_data(self):
        try:
            stations = await self.api.get_all_stations()

            if not stations:
                return {}

            _LOGGER.warning(f"COORD DATA SAMPLE: {stations[:1]}")  # 👈 여기

            nearest = min(
                stations,
                key=lambda s: haversine(
                    (self.lat, self.lon),
                    (s["lat"], s["lon"]),
                ),
            )

            return {
                "stations": stations,
                "nearest": nearest,
            }

        except Exception as e:
            _LOGGER.error(f"SeoulBike update failed: {e}")
            return {}