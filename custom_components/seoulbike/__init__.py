from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    api = SeoulBikeApi(entry.data["api_key"])

    coordinator = SeoulBikeCoordinator(
        hass,
        api,
        entry.data.get("radius_km", 1.0),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True