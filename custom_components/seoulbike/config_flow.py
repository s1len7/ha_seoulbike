import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_API_KEY, CONF_RADIUS_KM, DEFAULT_RADIUS_KM


class SeoulBikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            return self.async_create_entry(
                title="SeoulBike",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM): float,
        })

        return self.async_show_form(step_id="user", data_schema=schema)