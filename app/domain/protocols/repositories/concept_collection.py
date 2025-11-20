from typing import Protocol, Literal, Optional, List

from app.domain.models.concept_collection import CollectionRead, CollectionUpdate, CollectionCreateExtended


class CollectionRepository(Protocol):
    async def add(self, collection: CollectionCreateExtended) -> CollectionRead:
        ...

    async def get_one(self, collection_id: int) -> CollectionRead:
        ...
    
    async def get_all(self, filter_name: Literal["course", "domain", "all"], filter_id: Optional[int]) -> List[CollectionRead]:
        ...
    
    async def update(self, collection_id: int, collection_update: CollectionUpdate) -> CollectionRead:
        ...

    async def delete_from_course(self, collection_id: int, course_id: int) -> None:
        ...