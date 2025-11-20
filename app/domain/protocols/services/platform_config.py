from typing import Protocol

from app.domain.models.platform_config import PlatformConfigCreate, PlatformConfigRead



class PlatformConfigService(Protocol):
    async def add_config(self, platform_config: PlatformConfigCreate) -> PlatformConfigRead:
        ...
    
    async def get_config(self, client_id: str) -> PlatformConfigRead:
        ...