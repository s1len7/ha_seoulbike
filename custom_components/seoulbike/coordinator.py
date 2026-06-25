"""Coordinator for Seoul Bike."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from haversine import haversine


_LOGGER = logging.getLogger(__name__)


class SeoulBikeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, latitude, longitude):
        super().__init__(
            hass,
            _LOGGER,
            name="seoulbike",
            update_interval=timedelta(minutes=1),
        )

        self.api = api
        self.latitude = latitude
        self.longitude = longitude

    async def _async_update_data(self):
        try:
            stations = await self.api.get_all_stations()

            if not stations:
                return {}

            nearest = min(
                stations,
                key=lambda s: haversine(
                    (self.latitude, self.longitude),
                    (s["latitude"], s["longitude"]),
                ),
            )

            return {
                "stations": stations,
                "nearest_station": nearest,
            }

        except Exception as err:
            _LOGGER.error(f"SeoulBike update failed: {err}")
            return {}