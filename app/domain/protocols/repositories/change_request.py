from typing import List, Protocol
from app.domain.models.change_requests import ChangeRequestRead, ChangeRequestCreateClient, ChangeRequestUpdate
from app.domain.models.session import SessionExtended

class ChangeRequestRepository(Protocol):
    async def add(self, item: ChangeRequestCreateClient) -> ChangeRequestRead:
        """
        Adds one entry to the change_request table 
        """
        pass
    
    async def bulk_add(self, items: List[ChangeRequestCreateClient]) -> List[ChangeRequestRead]:
        """
        Adds many entrys to the change_request table 
        """
        pass
    
    async def update(self, update: ChangeRequestUpdate)-> ChangeRequestRead:
        """
        Updates the values of a change_request entry, comments are always appended to instead of overwritten.
        """
        pass

    async def get_related(self, client_session: SessionExtended) -> List[ChangeRequestRead]:
        """
        Returns all change_request entries a client has been designated as an appropriate reviewer for.
        """
        pass