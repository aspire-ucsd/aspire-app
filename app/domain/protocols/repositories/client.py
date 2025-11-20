from typing import Protocol, List
from app.domain.models.client import (
    ClientCreate,
    ClientRead,
    StudentKnowledgeCreate, 
    StudentKnowledgeRead, 
    ClientToCourseCreate,
    ClientToCourseRead,
    )


class ClientRepository(Protocol):
    async def add(self, client: ClientCreate) -> ClientRead:
        """
        Adds a new student to the student table
        """
        pass

    async def get(self, platform_id: str) -> ClientRead:
        ...


class ClientToCourseRepository(Protocol):
    async def add(self, junction: ClientToCourseCreate) -> ClientToCourseRead:
        """
        Adds a new junction between a student and a course
        """
        pass


class StudentKnowledgeRepository(Protocol):
    async def get(self, student_id:int, concept_name:str) -> StudentKnowledgeRead:
        """
        Returns a single StudentKnowledge entry matching the student_id and concept_name
        """
        pass

    async def bulk_get(self, student_id: int, concept_list: List) -> List[StudentKnowledgeRead]:
        ...
    
    async def add(self, score: StudentKnowledgeCreate) -> StudentKnowledgeRead:
        """
        Adds a new entry to the StudentKnowledge table
        """
        pass
    
    async def update(self, score: StudentKnowledgeCreate) -> StudentKnowledgeRead:
        """
        Updates the concept_score of an existing StudentKnowledge entry matching the student_id and concept_name provided in the StudentKnowledgeCreate object
        """
        pass