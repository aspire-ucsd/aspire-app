from typing import List
from fastapi import Depends

from app.domain.models.client import (
    ClientCreate,
    ClientRead,
    StudentKnowledgeRead,
    ClientToCourseCreate,
    ClientToCourseRead
)
from app.infrastructure.database.repositories.client import (
    ClientRepository,
    StudentKnowledgeRepository,
    ClientToCourseRepository
)
from app.domain.protocols.repositories.client import (
    StudentKnowledgeRepository as StudentKnowledgeRepoProtocol,
    ClientRepository as ClientRepoProtocol,
    ClientToCourseRepository as SToCRepoProtocol
    )
from app.domain.protocols.services.client import ClientService as ClientServiceProtocol

from app.domain.models.concept import ConceptBulkRead


class ClientService(ClientServiceProtocol):
    def __init__(
        self, 
        client_repo: ClientRepoProtocol = Depends(ClientRepository),
        s_k_repo: StudentKnowledgeRepoProtocol = Depends(StudentKnowledgeRepository),
        s_to_c_repo: SToCRepoProtocol = Depends(ClientToCourseRepository)

    ):
        self.client_repo = client_repo
        self.s_k_repo = s_k_repo
        self.s_to_c_repo = s_to_c_repo

    async def add_client(self, client: ClientCreate) -> ClientRead:
        return await self.client_repo.add(client=client)

    async def get_client(self, platform_id: str) -> ClientRead:
        return await self.client_repo.get(platform_id=platform_id)
    
    async def add_client_to_course(self, junction: ClientToCourseCreate) -> ClientToCourseRead:
        return await self.s_to_c_repo.add(
            junction=junction
        )

    async def get_student_knowledge_score(self, student_id: int, concept_name: str) -> StudentKnowledgeRead:
        return await self.s_k_repo.get(student_id=student_id, concept_name=concept_name)
    
    async def get_student_model_from_concepts(self, concepts: ConceptBulkRead, student_id: int) -> List[StudentKnowledgeRead]:
        return await self.s_k_repo.get_many(concepts=concepts, student_id=student_id)
