from typing import List, Optional, Protocol
from fastapi import UploadFile

from app.domain.models.forms import ModuleForm
from app.domain.models.concept_collection import CollectionRead, CollectionUpdate, CollectionCreateExtended
from app.domain.models.concept import ConceptRead


class CollectionService(Protocol):
    async def create_collection(self, collection: CollectionCreateExtended, concepts: Optional[List[ConceptRead]]) -> CollectionRead:
        ...

    async def get_collection(self, collection_id: int) -> CollectionRead:
        ...

    async def get_course_collections(self, course_id:int) -> List[CollectionRead]:
        ...

    async def get_all_collections(self) -> List[CollectionRead]:
        ...

    async def update_collection(self, collection_id: int, collection_update: CollectionUpdate) -> CollectionRead:
        ...

    async def delete_collection_from_course(self, collection_id: int, course_id: int) -> None:
        ...