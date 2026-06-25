from homeassistant import config_entries

class SeoulBikeConfigFlow(
    config_entries.ConfigFlow,
    domain="seoulbike"
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="Hello Seoul Bike",
            data={}
        )