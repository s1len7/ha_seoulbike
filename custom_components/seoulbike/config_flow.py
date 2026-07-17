import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_RADIUS_KM,
    CONF_TOP_N,
    DEFAULT_RADIUS_KM,
    DEFAULT_TOP_N,
    TOP_N_MIN,
    TOP_N_MAX,
)


class SeoulBikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            top_n = int(user_input.get(CONF_TOP_N, DEFAULT_TOP_N))
            if top_n < TOP_N_MIN:
                top_n = TOP_N_MIN
            if top_n > TOP_N_MAX:
                top_n = TOP_N_MAX
            user_input[CONF_TOP_N] = top_n
            return self.async_create_entry(title="SeoulBike", data=user_input)
        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM): vol.Coerce(
                    float
                ),
                vol.Optional(CONF_TOP_N, default=DEFAULT_TOP_N): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """옵션 플로우 핸들러를 반환합니다."""
        return SeoulBikeOptionsFlowHandler(config_entry)


class SeoulBikeOptionsFlowHandler(config_entries.OptionsFlow):
    """설정 메뉴에서 [설정] 버튼을 눌렀을 때의 UI를 처리합니다."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """내부 변수에 안전하게 config_entry를 할당합니다."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            top_n = int(user_input.get(CONF_TOP_N, DEFAULT_TOP_N))
            if top_n < TOP_N_MIN:
                top_n = TOP_N_MIN
            if top_n > TOP_N_MAX:
                top_n = TOP_N_MAX
            user_input[CONF_TOP_N] = top_n
            return self.async_create_entry(title="", data=user_input)
        current_radius = self._config_entry.options.get(
            CONF_RADIUS_KM,
            self._config_entry.data.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM),
        )
        current_top_n = self._config_entry.options.get(
            CONF_TOP_N, self._config_entry.data.get(CONF_TOP_N, DEFAULT_TOP_N)
        )
        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_RADIUS_KM, default=vol.Coerce(float)(current_radius)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_TOP_N, default=vol.Coerce(int)(current_top_n)
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)
