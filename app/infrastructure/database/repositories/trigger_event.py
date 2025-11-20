import logging
from typing import List
from sqlmodel import Session, text, delete

from app.infrastructure.database.db import get_db
from app.domain.models.trigger_event import TriggerEventCreate, TriggerEventRead, TriggerEvent, TriggerEventProcess
from app.domain.protocols.repositories.trigger_event import TriggerEventRepository as TriggerEventRepoProtocol

from app.app.errors.db_error import DBError

logger = logging.getLogger(__name__)

class TriggerEventRepository(TriggerEventRepoProtocol):
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def add(self, event: TriggerEventCreate) -> TriggerEventRead:
        try:
            event_obj = TriggerEvent.model_validate(event)
            self.db.add(event_obj)
            self.db.commit()
            self.db.refresh(event_obj)

            return TriggerEventRead.model_validate(event_obj)
        
        except Exception as e:
            logger.exception(msg=f"Failed to add Trigger Event: {event}.")
            raise DBError(
                origin="TriggerEventRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Trigger Event."
            ) from e
            
    async def bulk_add(self, events: List[TriggerEventCreate]) -> List[TriggerEventRead]:
        try:
            event_objs = [TriggerEvent.model_validate(event) for event in events]
            self.db.add_all(event_objs)
            self.db.commit()

            for item in event_objs:
                self.db.refresh(item)

            return [TriggerEventRead.model_validate(event) for event in event_objs]
        
        except Exception as e:
            logger.exception(msg="Failed to add Trigger Events.")
            raise DBError(
                origin="TriggerEventRepository.bulk_add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Trigger Events."
            ) from e
        
    async def queue_check(self) -> bool:
        try:
            stmt = text("SELECT exists (SELECT * FROM trigger_event limit 1)")
            result = self.db.exec(statement=stmt)
            result = result.one()
            self.db.close()
            return result[0]
        
        except Exception as e:
            logger.exception(msg="Failed to check queue")
            raise DBError(
                origin="TriggerEventRepository.queue_check",
                type="QueryExecError",
                status_code=500,
                message="Failed to check queue"
            ) from e
        
    async def get_queue(self, max_batch_size:int) -> List[TriggerEventProcess]:
        try:
            stmt = text(
                """
                SELECT student_id, concept, SUM(weight * value) numerator, SUM(weight) denominator, array_agg ( event_id ) event_ids
                FROM trigger_event
                GROUP BY GROUPING SETS ((student_id, concept))
                LIMIT :max_batch_size
                """
                )
            
            results = self.db.exec(statement=stmt, params={"max_batch_size": max_batch_size})
            results = [TriggerEventProcess(**event) for event in results.mappings().all()]
            self.db.close()
            return results
        
        except Exception as e:
            logger.exception(msg="Failed to return queue")
            raise DBError(
                origin="TriggerEventRepository.get_queue",
                type="QueryExecError",
                status_code=500,
                message="Failed to return queue"
            ) from e
        
    async def bulk_delete(self, event_ids: list[int]):
        try:
            stmt = delete(TriggerEvent).where(TriggerEvent.event_id.in_(event_ids))
            self.db.exec(statement=stmt)
            self.db.commit()
            self.db.close()
            
        except Exception as e:
            logger.exception(msg="Failed to delete event object")
            raise DBError(
                origin="TriggerEventRepository.bulk_delete",
                type="QueryExecError",
                status_code=500,
                message="Failed to delete event object"
            ) from e