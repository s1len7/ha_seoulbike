"""Seoul Bike integration."""

from __future__ import annotations

import logging

from .const import DOMAIN, CONF_SEOUL_API_KEY
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    seoul_api_key = entry.data[CONF_SEOUL_API_KEY]

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    api = SeoulBikeApi(seoul_api_key)

    coordinator = SeoulBikeCoordinator(
        hass=hass,
        api=api,
        latitude=latitude,
        longitude=longitude,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    _LOGGER.info(f"Seoul Bike initialized with API key and coordinator")

    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)

    _LOGGER.info(f"Seoul Bike unloaded")

    return True