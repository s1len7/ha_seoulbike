import voluptuous as vol
from homeassistant import config_entries

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

            return self.async_create_entry(
                title="SeoulBike",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM): vol.Coerce(float),
            vol.Optional(CONF_TOP_N, default=DEFAULT_TOP_N): vol.Coerce(int),
        })

        return self.async_show_form(step_id="user", data_schema=schema)