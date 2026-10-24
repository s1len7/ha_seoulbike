"""따릉이 설정 화면.

설정 항목은 API 키만 갖고, 대여소·지역은 하위 항목으로 추가한다.
"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_RADIUS_KM,
    CONF_STATION_ID,
    CONF_TOP_N,
    CONF_ZONE_ID,
    DEFAULT_RADIUS_KM,
    DEFAULT_TOP_N,
    RADIUS_KM_MAX,
    RADIUS_KM_MIN,
    SUBENTRY_TYPE_STATION,
    SUBENTRY_TYPE_ZONE,
    TOP_N_MIN,
    TOP_N_MAX,
    ZONE_HOME,
)
from .src.seoul_api import SeoulApiError
from .src.seoul_bike_api import SeoulBikeApi

API_KEY_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


async def _async_validate_api_key(hass, api_key):
    """API 키를 실제로 호출해 확인하고, 화면에 보여줄 errors를 반환."""

    api = SeoulBikeApi(api_key, async_get_clientsession(hass))

    try:
        valid = await api.validate_api_key()
    except SeoulApiError:
        return {"base": "cannot_connect"}

    if not valid:
        return {CONF_API_KEY: "invalid_api_key"}

    return {}


class SeoulBikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors = {}

        if user_input is not None:
            errors = await _async_validate_api_key(self.hass, user_input[CONF_API_KEY])
            if not errors:
                return self.async_create_entry(title="SeoulBike", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(API_KEY_SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        """실행 중 API 키 오류(ConfigEntryAuthFailed)가 나면 HA가 호출."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._async_step_update_api_key(
            "reauth_confirm", self._get_reauth_entry(), user_input
        )

    async def async_step_reconfigure(self, user_input=None):
        """통합 화면 ⋮ 메뉴의 [재구성]에서 API 키만 바꾼다."""
        return await self._async_step_update_api_key(
            "reconfigure", self._get_reconfigure_entry(), user_input
        )

    async def _async_step_update_api_key(self, step_id, entry, user_input):

        errors = {}

        if user_input is not None:
            errors = await _async_validate_api_key(self.hass, user_input[CONF_API_KEY])
            if not errors:
                # 로드된 상태면 update listener가 다시 로드하고,
                # 첫 로드에서 키 오류로 실패한 상태면 listener가 없으므로 직접 다시 로드
                if entry.update_listeners:
                    return self.async_update_and_abort(entry, data_updates=user_input)
                return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id=step_id,
            data_schema=API_KEY_SCHEMA,
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry):
        return {
            SUBENTRY_TYPE_STATION: StationSubentryFlowHandler,
            SUBENTRY_TYPE_ZONE: ZoneSubentryFlowHandler,
        }


class StationSubentryFlowHandler(config_entries.ConfigSubentryFlow):
    """대여소 하위 항목 추가.

    대여소 ID는 하위 항목 고유 ID라서 바꿀 수 없으므로 재구성 화면을 두지 않는다.
    (중복 추가는 HA가 고유 ID로 막음)
    """

    async def async_step_user(self, user_input=None):

        runtime = self.hass.data.get(DOMAIN, {}).get(self._get_entry().entry_id)

        if runtime is None:
            return self.async_abort(reason="entry_not_loaded")

        coordinator = runtime["coordinator"]

        if user_input is not None:
            station = coordinator.get_station(user_input[CONF_STATION_ID])
            if station is None:
                return self.async_abort(reason="station_not_found")
            return self.async_create_entry(
                title=station.station_name,
                data={CONF_STATION_ID: station.station_id},
                unique_id=station.station_id,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_ID): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=self._station_options(coordinator),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    def _station_options(self, coordinator):
        """전체 대여소를 집에서 가까운 순으로. 라벨: 이름 (거리, 현재 대수)"""

        stations = (coordinator.data or {}).get("stations_by_id", {}).values()
        items = []

        for station in stations:
            dist = coordinator.distance_km(ZONE_HOME, station)
            items.append((dist if dist is not None else float("inf"), station))

        items.sort(key=lambda item: (item[0], item[1].station_name))

        options = []

        for dist, station in items:
            dist_text = f"{dist:.1f}km, " if dist != float("inf") else ""
            options.append(
                selector.SelectOptionDict(
                    value=station.station_id,
                    label=f"{station.station_name} ({dist_text}현재 {station.parking_bike_total_count}대)",
                )
            )

        return options


class ZoneSubentryFlowHandler(config_entries.ConfigSubentryFlow):
    """지역 하위 항목 추가·재구성. 지역 주변 대여소를 가까운 순으로 자동 탐색한다."""

    async def async_step_user(self, user_input=None):
        return await self._async_step_zone("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._async_step_zone("reconfigure", user_input)

    async def _async_step_zone(self, step_id, user_input):

        if user_input is not None:
            zone_id = user_input[CONF_ZONE_ID]
            state = self.hass.states.get(zone_id)
            title = state.name if state else zone_id
            data = {
                CONF_ZONE_ID: zone_id,
                CONF_RADIUS_KM: float(user_input[CONF_RADIUS_KM]),
                CONF_TOP_N: int(user_input[CONF_TOP_N]),
            }

            if step_id == "reconfigure":
                return self.async_update_and_abort(
                    self._get_entry(),
                    self._get_reconfigure_subentry(),
                    title=title,
                    data=data,
                    unique_id=zone_id,
                )
            return self.async_create_entry(title=title, data=data, unique_id=zone_id)

        schema = vol.Schema(
            {
                vol.Required(CONF_ZONE_ID, default=ZONE_HOME): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="zone")
                ),
                vol.Required(
                    CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=RADIUS_KM_MIN,
                        max=RADIUS_KM_MAX,
                        step=0.1,
                        unit_of_measurement="km",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_TOP_N, default=DEFAULT_TOP_N): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=TOP_N_MIN,
                        max=TOP_N_MAX,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
            }
        )

        # 재구성 시에는 현재 값을 기본으로 보여줌
        if step_id == "reconfigure":
            schema = self.add_suggested_values_to_schema(
                schema, dict(self._get_reconfigure_subentry().data)
            )

        return self.async_show_form(step_id=step_id, data_schema=schema)
