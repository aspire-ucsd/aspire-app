from ..config import AdapterConfig
from ..models.settings import ToolConfigSettings, PlatformConfigSettings
from typing import Union, Callable, Union, Coroutine, Any

def init_adapter_config(
        tool_settings: ToolConfigSettings, 
        platform_settings: Union[PlatformConfigSettings, Callable[[str], Coroutine[Any, Any, PlatformConfigSettings]]]
    ):
    """
    Initializes the library with a persistent set of configuration settings.

    :param tool_settings: \
        Static tool specific settings, must be an instance of the ToolConfigSettings class.

    :param platform_settings: \
        Platform specific settings either as an instance of the PlatformConfigSettings class \
        or an awaitable callback function that accepts a client_id:int and returns an instance of PlatformConfigSettings. \
        Awaitable Callback function required for applications requiring a dynamic registration system.

    <hr/>
    ========================================
    Usage Example:
    ========================================
```python

    import uvicorn

    from example_env_settings import get_settings
    from app.app import init_app

    from fastapi_lti1p3 import init_adapter_config, ToolConfigSettings, PlatformConfigSettings
    
    _SETTINGS = get_settings()

    tool_config = ToolConfigSettings(**_SETTINGS.dict())
    # static platform config example, see below for dynamic example.
    platform_config = PlatformConfigSettings(**_SETTINGS.dict())
    init_adapter_config(tool_settings=tool_config, platform_settings=platform_config)

    app = init_app(_SETTINGS)

    if __name__ == '__main__':
        uvicorn.run(app, host='0.0.0.0', port=8080)

```
    
    <hr/>
    ========================================
    Dynamic Platform Config Settings Example:
    ========================================

```python

    from fastapi_lti1p3 import PlatformConfigSettings ToolConfigSettings, init_adapter_config
    from irrelevant_to_example import tool_config
    from fake_db_engine import db

    #Must be async function that accepts a client_id as a string
    async def get_platform_settings(client_id:str) -> PlatformConfigSettings:
        statement = "SELECT ... WHERE client_id == %(client_id)s"
        result = db.execute(statement)
        #process the result however you want, im sure you can work it out.
        ...
        # Function must return an instance of PlatformConfigSettings
        return PlatformConfigSettings(**result)

    
    init_adapter_config(tool_settings=tool_config, platform_settings=get_platform_settings)

```
    """
    adapter_config = AdapterConfig()
    adapter_config.set_settings(tool_settings=tool_settings, platform_settings=platform_settings)
    adapter_config.assign_key_pair()

