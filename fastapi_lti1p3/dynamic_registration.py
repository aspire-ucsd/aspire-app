import httpx
from operator import itemgetter

from fastapi import Request, Depends

from fastapi_lti1p3.config import AdapterConfig
from fastapi_lti1p3 import ToolConfigSettings

class DynamicRegistrationService:
    def __init__(self, request: Request) -> None:
        self._request: Request = request
        self._adapter_config = AdapterConfig()
        self._tool_settings: ToolConfigSettings = self._adapter_config.get_tool_settings()

    async def get_registration_config(self) -> dict:
        openid_config_url, registration_token = itemgetter("openid_configuration", "registration_token")(self._request.query_params)

        async with httpx.AsyncClient() as client:
            response = await client.get(openid_config_url)
            response = response.json()
            print(f"\n\nResponse: {response}\n\n")
            return response
        
    

