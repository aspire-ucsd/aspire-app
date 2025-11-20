from typing import Union, Protocol

from app.domain.models.platform_config import PlatformConfigCreate, PlatformConfigRead


class PlatformConfigRepository(Protocol):
    ''' 
    Provides data access to platform configuration entries. Used with dynamic registration system to allow multiple registered platforms to launch the application.
    '''
    

    async def add(self, platform_config: PlatformConfigCreate) -> PlatformConfigRead:
        """
        Used to register a new platform to the application, adds a new entry to the PlatformConfig Table
        """
        ...
        
    async def get(self, client_id: Union[int, str]) -> PlatformConfigRead:
        """
        Used when retrieving platform specific config data, returns a single entry from the PlatformConfig Table where the client_id column exactly matches the supplied client_id
        """
        ...