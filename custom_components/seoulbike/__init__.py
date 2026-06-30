import logging
import debugpy

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.loader import async_get_integration

from .const import DOMAIN, DEFAULT_RADIUS_KM, DEFAULT_TOP_N, CONF_API_KEY
from .coordinator import SeoulBikeCoordinator
from .src.seoul_bike_api import SeoulBikeApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    integration = await async_get_integration(hass, DOMAIN)
    _LOGGER.warning(f"🚲 SeoulBike v{integration.version} integration started (async_setup_entry)")

    # 🐞 DEBUGPY ATTACH (2015)
    try:
        debugpy.listen(("0.0.0.0", 2015))
        # debugpy.wait_for_client()
        _LOGGER.warning("🐞 Debugger listening on port 2015")
    except Exception as e:
        _LOGGER.debug(f"Debugpy already started or failed: {e}")

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

    # 6️⃣ platforms 등록
    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor", "device_tracker", "geo_location"]
    )

    _LOGGER.warning("🚲 SeoulBike setup completed")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    _LOGGER.warning("🚲 SeoulBike unloading")

    await hass.config_entries.async_unload_platforms(
        entry,
        ["sensor", "device_tracker", "geo_location"]
    )

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True