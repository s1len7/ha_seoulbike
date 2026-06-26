from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DEFAULT_RADIUS_KM, DEFAULT_TOP_N
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator
from .zone_manager import SeoulBikeZoneManager


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    api_key = entry.data["seoul_api_key"]

    radius_km = float(entry.data.get("radius_km", DEFAULT_RADIUS_KM))
    top_n = int(entry.data.get("top_n", DEFAULT_TOP_N))

    api = SeoulBikeApi(api_key)

    coordinator = SeoulBikeCoordinator(
        hass=hass,
        api_client=api,
        radius_km=radius_km,
        top_n=top_n,
    )

    # 1️⃣ 데이터 먼저 준비
    await coordinator.async_config_entry_first_refresh()

    # 2️⃣ hass.data 먼저 세팅 (중요)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "zone_manager": None,
    }

    # 3️⃣ sensor 먼저 생성
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # 4️⃣ zone manager는 sensor 의존 없이 coordinator만 사용
    zone_manager = SeoulBikeZoneManager(
        hass=hass,
        coordinator=coordinator,
    )
    await zone_manager.async_init()

    hass.data[DOMAIN][entry.entry_id]["zone_manager"] = zone_manager

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True