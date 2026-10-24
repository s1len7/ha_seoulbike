import logging
from types import MappingProxyType

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_RADIUS_KM,
    CONF_TOP_N,
    CONF_ZONE_ID,
    DEFAULT_RADIUS_KM,
    DEFAULT_TOP_N,
    SUBENTRY_TYPE_ZONE,
    ZONE_HOME,
)
from .coordinator import SeoulBikeCoordinator
from .src.seoul_bike_api import SeoulBikeApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "device_tracker", "geo_location"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    # 1️⃣ API + Coordinator 생성 (모든 하위 항목이 함께 씀)
    api = SeoulBikeApi(entry.data[CONF_API_KEY], async_get_clientsession(hass))

    coordinator = SeoulBikeCoordinator(hass, entry, api)

    # 2️⃣ 최초 데이터 로딩
    await coordinator.async_config_entry_first_refresh()

    # 3️⃣ hass.data 저장
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    # 4️⃣ platforms 등록
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 5️⃣ API 키 변경, 하위 항목 추가·변경·삭제 시 다시 로드
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.debug("SeoulBike setup completed")

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):

    if entry.version > 2:
        # 더 새 버전에서 만든 설정은 읽을 수 없음
        return False

    if entry.version == 1:
        # 1 → 2: 반경·대여소 수 설정을 "집" 지역 하위 항목으로 옮김
        settings = {**entry.data, **entry.options}

        hass.config_entries.async_add_subentry(
            entry,
            ConfigSubentry(
                data=MappingProxyType(
                    {
                        CONF_ZONE_ID: ZONE_HOME,
                        CONF_RADIUS_KM: float(
                            settings.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)
                        ),
                        CONF_TOP_N: int(settings.get(CONF_TOP_N, DEFAULT_TOP_N)),
                    }
                ),
                subentry_type=SUBENTRY_TYPE_ZONE,
                title=hass.config.location_name,
                unique_id=ZONE_HOME,
            ),
        )

        # 옛 형식 unique_id의 엔티티는 하위 항목 엔티티로 대체되므로 삭제
        entity_registry = er.async_get(hass)
        for entity in er.async_entries_for_config_entry(
            entity_registry, entry.entry_id
        ):
            entity_registry.async_remove(entity.entity_id)

        hass.config_entries.async_update_entry(
            entry,
            data={CONF_API_KEY: entry.data[CONF_API_KEY]},
            options={},
            unique_id=DOMAIN,
            version=2,
        )

        _LOGGER.debug("SeoulBike config entry migrated to version 2")

    return True
