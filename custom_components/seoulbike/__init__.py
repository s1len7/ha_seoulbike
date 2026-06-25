"""Seoul Bike integration."""
import logging

DOMAIN = "seoulbike"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    # Home Assistant 시작 시 1회 실행
    _LOGGER.info("Hello World from Seoul Bike!")
    return True

async def async_unload_entry(hass, entry):
    _LOGGER.info("Goodbye World from Seoul Bike!")
    return True