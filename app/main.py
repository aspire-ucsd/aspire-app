import uvicorn

from app.config.environment import get_settings
from app.app import init_app
from app.domain.models.trigger_event import TriggerEvent
from app.domain.services.platform_config import get_config_lti_adapter
from app.domain.models.session import SessionExtended

from fastapi_lti1p3 import init_adapter_config, ToolConfigSettings, PlatformConfigSettings

# def _setup_logging(self):
#     self.logger = logging.getLogger(__name__)
#     self.logger.setLevel(logging.DEBUG)
#     if len(self.logger.handlers) == 0: # Prevent successive configuration for same logger instance
#         log_format = logging.Formatter('MAD <' + os.getenv('MAD_ENV','') + '> [%(levelname)s] - %(message)s')
#         handler = logging.handlers.SysLogHandler(address = '/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
#         handler.setFormatter(log_format)
#         self.logger.addHandler(handler)

_SETTINGS = get_settings()

adapter_tool_config = ToolConfigSettings(
    **_SETTINGS.model_dump(), 
    client_name=_SETTINGS.WEB_APP_TITLE, 
    description=_SETTINGS.WEB_APP_DESCRIPTION, 
    SESSION_CLASS=SessionExtended
)

init_adapter_config(tool_settings=adapter_tool_config, platform_settings=get_config_lti_adapter)

app = init_app(_SETTINGS)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


