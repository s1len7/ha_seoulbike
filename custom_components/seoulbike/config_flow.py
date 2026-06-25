"""Config flow for Seoul Bike."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .api import SeoulBikeApi
from .const import (
    DOMAIN,
    CONF_SEOUL_API_KEY,
    MAX_DISTANCE_KM,
)


class SeoulBikeConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:

            api = SeoulBikeApi(
                user_input[CONF_SEOUL_API_KEY]
            )

            if not await api.validate_api_key():
                errors["base"] = "invalid_api_key"

            else:
                latitude = self.hass.config.latitude
                longitude = self.hass.config.longitude

                nearest_distance = (
                    await api.nearest_station_distance(
                        latitude,
                        longitude,
                    )
                )

                if (
                    nearest_distance is None
                    or nearest_distance > MAX_DISTANCE_KM
                ):
                    errors["base"] = "unsupported_region"

                else:
                    return self.async_create_entry(
                        title="Seoul Bike",
                        data=user_input,
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_SEOUL_API_KEY): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )