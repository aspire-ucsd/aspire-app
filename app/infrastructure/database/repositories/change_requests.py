import logging
from typing import List, Union, Optional
from datetime import datetime, UTC
from sqlmodel import Session, text, delete, select, or_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import NoResultFound
from app.infrastructure.database.db import get_db
from app.app.errors.db_error import DBError

from app.app.errors.validation_error import ValidationError

from app.domain.models.change_requests import ChangeRequestRead, ChangeRequestCreate, ChangeRequestUpdate, ChangeRequest, Comment
from app.domain.models.session import SessionExtended
from app.domain.protocols.repositories.change_request import ChangeRequestRepository as ChangeRequestRepoProtocol

logger = logging.getLogger(__name__)

class ChangeRequestRepository(ChangeRequestRepoProtocol):
    db: Session
    
    def __init__(self):
        self.db = get_db()


    async def add(self, item: ChangeRequestCreate) -> ChangeRequestRead:
        """
        Adds one entry to the change_request table 
        """
        try:
            validation_obj = ChangeRequest.model_validate(item)
            self.db.add(validation_obj)
            self.db.commit()
            self.db.refresh(validation_obj)
            self.db.close()

            return ChangeRequestRead.model_validate(validation_obj)

        except Exception as e:
            logger.exception(msg=f"Failed to add item: {item}.")
            raise DBError(
                origin="ChangeRequestRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Item."
            ) from e
    

    async def bulk_add(self, items: List[ChangeRequestCreate]) -> List[ChangeRequestRead]:
        """
        Adds many entries to the change_request table 
        """
        try:
            validation_objs = [ChangeRequest.model_validate(item) for item in items]
            self.db.add_all(validation_objs)
            self.db.commit()

            for item in validation_objs:
                self.db.refresh(item)

            self.db.close()

            return [ChangeRequestRead.model_validate(item) for item in validation_objs]
        
        except Exception as e:
            logger.exception(msg="Failed to add items.")
            raise DBError(
                origin="ChangeRequestRepository.bulk_add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add items."
            ) from e
    

    async def update(
            self, 
            update: ChangeRequestUpdate, 
            apply_null_closes_at: bool = True,
            )-> ChangeRequestRead:
        """
        Updates the values of a change_request entry, comments are always appended to existing instead of overwritten. 
        This method performs direct updates on the table and should not be directly exposed to any service or endpoint not handling data curation and rule enforcement.
        """
        try:
            item = self.db.get(ChangeRequest, update.id)

            if item.vote_type == "veto" and "rejected" in update.votes:
                update.reviewers = []
                update.closes_at = None
                update.validation_status = "rejected"
                update_comment = Comment(
                    type='update', 
                    content=f"msg|Status automatically changed to 'rejected' due to veto|data_type|votes|data|{item.votes + update.votes}",
                    submitted_at=datetime.now(UTC),
                    )
                update.comments = [update_comment]
                update.votes = []
                update.committed_at = datetime.now(UTC)

            update_dict = update.model_dump(exclude_none=True)

            if apply_null_closes_at:
                update_dict["closes_at"] = update.closes_at
            
            
            item.sqlmodel_update(update_dict)
            item.votes = update.votes
            item.reviewers = update.reviewers

            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)

            return ChangeRequestRead.model_validate(item)
        
        except Exception as e:
            logger.exception(msg="Failed to update item.")
            raise DBError(
                origin="ChangeRequestRepository.update",
                type="QueryExecError",
                status_code=500,
                message="Failed to update item."
            ) from e
    
    async def close_request(            
        self, 
        change_request_id: int,
        client_session: Optional[SessionExtended] = None,
    )-> ChangeRequestRead:
        try:
            item = self.db.get(ChangeRequest, change_request_id)
            # Manual Change Request closure requires the CR be owned by the client and have no vote_type 
            if item.submitted_by != client_session.user_credentials.internal_id or item.vote_type:
                raise ValidationError(
                    origin="ChangeRequestRepository.update",
                    status_code=403,
                    message=f"Forbidden - Insufficent permissions to perform updates of type: CloseChangeRequest on this change request."
                    )
            
            update = ChangeRequestUpdate(
                id=change_request_id,
                comments=[Comment(type="update", content="msg|Change Request manually closed by submitter.")]
                )
            update_dict = update.model_dump(exclude_none=True)
            update_dict["closes_at"] = None
            
            item.sqlmodel_update(update_dict)

            item.votes = None
            item.reviewers = []

            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)

            return ChangeRequestRead.model_validate(item)
        
        except Exception as e:
            logger.exception(msg="Failed to close request.")
            raise DBError(
                origin="ChangeRequestRepository.close_request",
                type="QueryExecError",
                status_code=500,
                message="Failed to close request."
            ) from e


    async def get_related(self, client_id: int) -> Union[List[ChangeRequestRead], list]:
        """
        Returns all change_request entries a client has been designated as an appropriate reviewer for.
        """
        try:
            stmt = select(ChangeRequest)\
                .where(ChangeRequest.reviewers.contains(cast(client_id, JSONB)))\
                    .where(ChangeRequest.closes_at > datetime.now(UTC))\
                        .where(ChangeRequest.validation_status == 'pending')
            
            requests = self.db.exec(stmt).all()
            if len(requests) > 0:
                result = [ChangeRequestRead.model_validate(item) for item in requests]
            else:
                result = []

            self.db.close()
            return result
        
        except Exception as e:
            logger.exception(msg="Failed to update item.")
            raise DBError(
                origin="ChangeRequestRepository.update",
                type="QueryExecError",
                status_code=500,
                message="Failed to update item."
            ) from e
        
    async def get_my_closed(self, client_id: int) -> Union[List[ChangeRequestRead], list]:
        try:
            stmt = select(ChangeRequest)\
                .where(ChangeRequest.submitted_by == client_id)\
                    .where(or_(ChangeRequest.closes_at < datetime.now(UTC), ChangeRequest.closes_at == None))\
                        .where(ChangeRequest.validation_status == 'pending')
            
            requests = self.db.exec(stmt).all()
            if len(requests) > 0:
                result = [ChangeRequestRead.model_validate(item) for item in requests]
            else:
                result = []

            self.db.close()
            return result
        
        except Exception as e:
            logger.exception(msg="Failed to update item.")
            raise DBError(
                origin="ChangeRequestRepository.update",
                type="QueryExecError",
                status_code=500,
                message="Failed to update item."
            ) from e
        
    async def get_my_drafts(self, client_id: int) -> Union[List[ChangeRequestRead], list]:
        try:
            stmt = select(ChangeRequest)\
                .where(ChangeRequest.submitted_by == client_id)\
                    .where(or_(ChangeRequest.closes_at < datetime.now(UTC), ChangeRequest.closes_at == None))\
                        .where(ChangeRequest.validation_status == 'draft')
            
            requests = self.db.exec(stmt).all()
            if len(requests) > 0:
                result = [ChangeRequestRead.model_validate(item) for item in requests]
            else:
                result = []

            self.db.close()
            return result
        
        except Exception as e:
            logger.exception(msg="Failed to update item.")
            raise DBError(
                origin="ChangeRequestRepository.update",
                type="QueryExecError",
                status_code=500,
                message="Failed to update item."
            ) from e
    
    async def get_one(self, change_request_id: int) -> ChangeRequestRead:
        try:
            item = self.db.get(ChangeRequest, change_request_id)
            return ChangeRequestRead.model_validate(item)
        
        except Exception as e:
            logger.exception(msg=f"Failed to retrieve item at id: {change_request_id}.")
            raise DBError(
                origin="ChangeRequestRepository.get_one",
                type="QueryExecError",
                status_code=500,
                message=f"Failed to retrieve item at id: {change_request_id}."
            ) from e
        
    async def delete_draft(        
        self,
        client_session: SessionExtended, 
        change_request_id: int 
    ) -> None:
        try:
            item = select(ChangeRequest)\
                .where(ChangeRequest.submitted_by == client_session.user_credentials.internal_id)\
                    .where(ChangeRequest.id == change_request_id)\
                        .where(ChangeRequest.validation_status == 'draft')
            
            results = self.db.exec(item)
            self.db.delete(results.one())
            self.db.commit()
            self.db.close()

        except NoResultFound as e:
            logger.warn(msg=f"\n\nWARNING: A user attempted an illegal deletion of a Change Request\nclient_session.client.id: {client_session.user_credentials.internal_id}\nchange_request_id: {client_session.user_credentials.internal_id}\n\n")
            raise DBError(
                origin="ChangeRequestRepository.delete_draft",
                type="NoResultFound",
                status_code=404,
                message=f"Valid change request at ID: {change_request_id} not found."
            ) from e
        
        except Exception as e:
            logger.exception(msg=f"Failed to delete item at id: {change_request_id}\n\nCause: {e}.")
            raise DBError(
                origin="ChangeRequestRepository.delete_draft",
                type="QueryExecError",
                status_code=500,
                message=f"Failed to delete item at id: {change_request_id}."
            ) from e