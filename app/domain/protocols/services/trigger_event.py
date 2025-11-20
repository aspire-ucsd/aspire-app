from typing import List, Protocol
from app.domain.models.trigger_event import TriggerEventCreate, TriggerEventRead

class TriggerEventService(Protocol):
    async def add_event(self, event: TriggerEventCreate) -> TriggerEventRead:
        """
        Adds one entry to the TriggerEvent table 
        """
        pass
    
    async def bulk_add_events(self, events: List[TriggerEventCreate]) -> List[TriggerEventRead]:
        """
        Adds many entrys to the TriggerEvent table 
        """
        pass