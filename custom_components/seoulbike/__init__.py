"""Seoul Bike."""

from __future__ import annotations

import logging

from .const import DOMAIN, CONF_SEOUL_API_KEY
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    api_key = entry.data[CONF_SEOUL_API_KEY]

    lat = hass.config.latitude
    lon = hass.config.longitude

    api = SeoulBikeApi(api_key)

    coordinator = SeoulBikeCoordinator(
        hass=hass,
        api=api,
        lat=lat,
        lon=lon,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # _LOGGER.info("SeoulBike loaded")
    _LOGGER.warning("🔥 SEOULBIKE INIT EXECUTED 🔥")
    
    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id, None)

    _LOGGER.info("SeoulBike unloaded")

    return True