"""Seoul Bike integration."""

import logging

from .const import (
    CONF_VWORLD_API_KEY,
    CONF_SEOUL_API_KEY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    vworld_api_key = entry.data.get(CONF_VWORLD_API_KEY)
    seoul_api_key = entry.data.get(CONF_SEOUL_API_KEY)

    _LOGGER.info("Seoul Bike initialized")
    _LOGGER.debug("VWORLD key configured: %s", bool(vworld_api_key))
    _LOGGER.debug("Seoul API key configured: %s", bool(seoul_api_key))

    return True


async def async_unload_entry(hass, entry):
    _LOGGER.info("Seoul Bike unloaded")
    return True