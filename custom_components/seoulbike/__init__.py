"""Seoul Bike integration."""

from __future__ import annotations

import logging

from .const import (
    DOMAIN,
    CONF_SEOUL_API_KEY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    seoul_api_key = entry.data.get(CONF_SEOUL_API_KEY)

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    _LOGGER.info("Seoul Bike initialized")
    _LOGGER.info(f"Seoul API Key: {seoul_api_key}")
    _LOGGER.info(f"Home latitude: {latitude}")
    _LOGGER.info(f"Home longitude: {longitude}")

    return True


async def async_unload_entry(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info("Seoul Bike unloaded")

    return True