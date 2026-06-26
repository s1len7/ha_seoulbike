from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_RADIUS_KM
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    api_key = entry.data.get("seoul_api_key")

    radius_km = entry.data.get("radius_km", DEFAULT_RADIUS_KM)

    try:
        radius_km = float(radius_km)
    except (TypeError, ValueError):
        radius_km = DEFAULT_RADIUS_KM

    api = SeoulBikeApi(api_key)

    coordinator = SeoulBikeCoordinator(
        hass=hass,
        api_client=api,
        radius_km=radius_km,
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