"""Hello HACS integration."""
import logging

DOMAIN = "hello_hacs"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    # Home Assistant 시작 시 1회 실행
    _LOGGER.info("Hello World from hello_hacs!")
    return True

async def async_unload_entry(hass, entry):
    return True