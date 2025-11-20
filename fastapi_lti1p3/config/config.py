from ..utils import generate_rsa_key_pair
from ..models.settings import ToolConfigSettings, PlatformConfigSettings
from typing import Union, Callable, Optional, Union
from ..errors.validation_errors import ConfigValidationError
from ..errors import ConfigValidationError

class AdapterConfig:
    _config = None

    def __new__(cls, *args, **kwargs):
        if not cls._config:
            cls._config = super(AdapterConfig, cls).__new__(cls, *args, **kwargs)
        return cls._config
    
    def __init__(self) -> None:
        if not hasattr(self, "initialized"):
            self.initialized = True
            self._tool_settings = None
            self._platform_settings = None

    def assign_key_pair(self):
        private_pem, public_pem = generate_rsa_key_pair()
        self._tool_settings.LTI_PRIVATE_KEY = private_pem
        self._tool_settings.LTI_PUBLIC_KEY = public_pem

    def set_settings(
            self, 
            tool_settings: ToolConfigSettings, 
            platform_settings: Union[PlatformConfigSettings, Callable[[int], PlatformConfigSettings]]
        ):
        self._tool_settings = tool_settings
        self._platform_settings = platform_settings

    async def get_platform_settings(self, client_id: Optional[str]) -> PlatformConfigSettings:
        if callable(self._platform_settings):
            result = await self._platform_settings(client_id)
            if isinstance(result, PlatformConfigSettings):
                return result
            else:
                raise ConfigValidationError(message=f"Invalid Config: Platform settings initialized as a callback function must return type: PlatformConfigSettings. Returned type: {type(result)} instead.")
        else:
            result = self._platform_settings
            if isinstance(result, PlatformConfigSettings):
                return result
            else:
                raise ConfigValidationError(message=f"Invalid Config: Platform settings initialized as static object must be of type: PlatformConfigSettings. Returned type: {type(result)} instead.")
    
    def get_tool_settings(self) -> ToolConfigSettings:
        result = self._tool_settings
        if isinstance(result, ToolConfigSettings):
            return result
        else:
            raise ConfigValidationError(
                message=f"Invalid Config: Tool settings must be of type: ToolConfigSettings. Returned type: {type(result)} instead."
            )