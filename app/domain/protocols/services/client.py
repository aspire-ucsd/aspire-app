from typing import  Protocol

from app.domain.models.client import (
    ClientCreate,
    ClientRead,
    StudentKnowledgeRead,
    ClientToCourseCreate,
    ClientToCourseRead
)


class ClientService(Protocol):
    async def add_client(self, client: ClientCreate) -> ClientRead:
        """
        Adds a new student to the db
        """
        pass

    async def get_client(self, platform_id: str) -> ClientRead:
        ...
    
    async def add_client_to_course(self, junction: ClientToCourseCreate) -> ClientToCourseRead:
        """
        Adds an existing client to an existing course
        """
        pass

    async def get_student_knowledge_score(self, student_id: int, concept_name: str) -> StudentKnowledgeRead:
        """
        Returns a single StudentKnowledge entry matching the student_id and concept_name
        """
        pass