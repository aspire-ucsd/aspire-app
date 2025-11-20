from typing import List, Protocol

from app.domain.models.trigger_event import TriggerEventCreate, TriggerEventRead, TriggerEventProcess



class TriggerEventRepository(Protocol):
    async def add(self, event: TriggerEventCreate) -> TriggerEventRead:
        """
        Adds a single Trigger Event to the queue for later processing
        """
        pass
    
    async def bulk_add(self, events: List[TriggerEventCreate]) -> List[TriggerEventRead]:
        """
        Adds multiple Trigger Event to the queue for later processing
        """
        pass
    
    async def queue_check(self) -> bool:
        """
        Checks if data is in the TriggerEvent table
        Returns True if table has data else returns false
        """
        pass

    async def get_queue(self, max_batch_size:int) -> List[TriggerEventProcess]:
        """
        Pre-processes data from the queue such that rows with matching pairs of concept and student_id values
        are grouped together, and the weights and values of these groups are aggregated and calculated as the numerator and denominator of the weighted average equation.
        Returns the numerator, denominator, student_id, concept, and list of event_ids for each of these groups up to max_batch_size.
        """
        pass
    
    async def bulk_delete(self, event_ids: list[int]) -> None:
        """
        Deletes all trigger events where its event_id is in the list of event_ids
        """
        pass