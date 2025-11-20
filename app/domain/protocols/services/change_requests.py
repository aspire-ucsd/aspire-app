from typing import List, Protocol, Union
from app.domain.models.change_requests import ChangeRequestRead, ChangeRequestCreateClient, ChangeRequestUpdate
from app.domain.models.session import SessionExtended

class ChangeRequestService(Protocol):
    async def add_item(self, item: ChangeRequestCreateClient, client_session: SessionExtended) -> ChangeRequestRead:
        """
        Adds one entry to the change_request table 

        =======
        Process
        =======
        - Performs 'validity' check on the CR with the following instructions:
            - CRs of modification_type == 'delete' or 'update' where the targeted entry does not exist in the db are tossed out.
            - CRs of modification_type == 'create' where the proposed entry already exists either:
                A) Convert to update request if the entity_type is not a junction table and the request data differs from the origional.
                B) Convert to null request if the entity_type is not a junction table and the request data matches the origional.
                C) Are tossed out if the entity_type is a junction table.
            - CRs of modification_type == 'create' on junction tables where the proposed entry does not exist are tossed if one or both of the entries being joined do not exist.
        - Populates entity_data field of 'update' or 'delete' CRs with the stored data of the target entity.
        - Populates the vote_type field based on the entity_type and modification_type.
        - Populates the closes_at field if vote_type not none.
        - Populates the reviewers field with relevant reviewers if vote_type not none.
        - Populates submitted_by field with the internal client_id on the client session.

        """
        ...
    
    async def bulk_add_items(self, items: List[ChangeRequestCreateClient], client_session: SessionExtended) -> List[ChangeRequestRead]:
        """
        Adds many entrys to the change_request table 
        """
        ...
    
    async def update_item(self, update: ChangeRequestUpdate)-> ChangeRequestRead:
        """
        Updates the values of a change_request entry, comments are always appended to instead of overwritten.
        """
        ...

    async def get_relevant_items(self, client_session: SessionExtended) -> List[ChangeRequestRead]:
        """
        Returns all change_request entries a client has been designated as an appropriate reviewer for.
        """
        ...

    async def get_my_drafts(self, client_session: SessionExtended)-> Union[List[ChangeRequestRead], list]:
        """
        Returns all change_request entries a belonging to a client where the status == 'draft'.
        """
        ...