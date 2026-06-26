from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DEFAULT_RADIUS_KM, DEFAULT_TOP_N, CONF_API_KEY
from .api import SeoulBikeApi
from .coordinator import SeoulBikeCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    # 1️⃣ API key
    api_key = entry.data[CONF_API_KEY]

    # 2️⃣ 설정값
    radius_km = float(entry.data.get("radius_km", DEFAULT_RADIUS_KM))
    top_n = int(entry.data.get("top_n", DEFAULT_TOP_N))

    # 3️⃣ API + Coordinator 생성
    api = SeoulBikeApi(api_key)

    coordinator = SeoulBikeCoordinator(
        hass=hass,
        api_client=api,
        radius_km=radius_km,
        top_n=top_n,
    )

    # 4️⃣ 최초 데이터 로딩
    await coordinator.async_config_entry_first_refresh()

    # 5️⃣ hass.data 저장
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    # 6️⃣ sensor + device_tracker 등록
    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor", "device_tracker"]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    # sensor + device_tracker unload
    await hass.config_entries.async_unload_platforms(
        entry,
        ["sensor", "device_tracker"]
    )

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True