"""Config flow for Seoul Bike."""

from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, CONF_SEOUL_API_KEY
from .api import SeoulBikeApi


class SeoulBikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):

        errors = {}

        if user_input is not None:
            api = SeoulBikeApi(user_input[CONF_SEOUL_API_KEY])

            # 🔥 API 키 검증
            valid = await api.validate_api_key()

            if not valid:
                errors["base"] = "invalid_api_key"
            else:
                return self.async_create_entry(
                    title="Seoul Bike",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SEOUL_API_KEY): str,
            }),
            errors=errors,
        )