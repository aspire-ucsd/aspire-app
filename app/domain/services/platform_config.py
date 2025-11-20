from typing import Union
from fastapi import Depends

from fastapi_lti1p3 import PlatformConfigSettings
from fastapi_lti1p3.errors import ClientIdError

from app.domain.models.platform_config import PlatformConfigCreate, PlatformConfigRead
from app.infrastructure.database.repositories.platform_config import PlatformConfigRepository
from app.domain.protocols.repositories.platform_config import PlatformConfigRepository as PlatformConfigRepoProtocol
from app.domain.protocols.services.platform_config import PlatformConfigService as PlatformConfigServiceProtocol


class PlatformConfigService(PlatformConfigServiceProtocol):
    def __init__(
        self, 
        platform_config_repo: PlatformConfigRepoProtocol = Depends(PlatformConfigRepository),

    ):
        self.platform_config_repo = platform_config_repo


    async def add_config(self, platform_config: PlatformConfigCreate) -> PlatformConfigRead:
        return await self.platform_config_repo.add(platform_config=platform_config)
    

    async def get_config(self, client_id: str) -> PlatformConfigRead:
        return await self.platform_config_repo.get(client_id=client_id)
    

async def get_config_lti_adapter(client_id: str) -> PlatformConfigSettings:
    platform_config_repo = PlatformConfigRepository()
    try:
        settings = await platform_config_repo.get(client_id=client_id)
        
    except Exception as e:
        raise ClientIdError(message="Unauthorized Client ID", status_code=403) from e
    
    return PlatformConfigSettings(**dict(settings))
