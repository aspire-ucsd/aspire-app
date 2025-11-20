from typing import List
from fastapi import Depends

from app.infrastructure.database.repositories.trigger_event import TriggerEventRepository
from app.domain.protocols.repositories.trigger_event import TriggerEventRepository as TriggerEventRepoProtocol
from app.domain.protocols.services.trigger_event import TriggerEventService as TriggerEventServiceProtocol
from app.domain.models.trigger_event import TriggerEventCreate, TriggerEventRead

class TriggerEventService(TriggerEventServiceProtocol):
    def __init__(
        self, 
        trigger_event_repo: TriggerEventRepoProtocol = Depends(TriggerEventRepository)
    ):
        self.trigger_event_repo = trigger_event_repo

    async def add_event(self, event: TriggerEventCreate) -> TriggerEventRead:
        return await self.trigger_event_repo.add(event=event)
    
    async def bulk_add_events(self, events: List[TriggerEventCreate]) -> List[TriggerEventRead]:
        return await self.trigger_event_repo.bulk_add(events=events)
