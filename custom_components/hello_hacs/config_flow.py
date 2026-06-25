from homeassistant import config_entries

class HelloHacsConfigFlow(
    config_entries.ConfigFlow,
    domain="hello_hacs"
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="Hello HACS",
            data={}
        )