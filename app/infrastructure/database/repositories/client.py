from typing import List
import logging

from app.domain.models.concept import ConceptBulkRead, ConceptToCollection

from app.domain.models.client import (
    ClientCreate,
    ClientRead,
    Client,
    StudentKnowledgeCreate, 
    StudentKnowledgeRead, 
    StudentKnowledge, 
    ClientToCourseCreate,
    ClientToCourseRead,
    ClientToCourse
    )

from app.domain.models.concept_collection import ConceptCollection


from app.domain.models.course import Course
from app.domain.models.change_requests import ChangeRequestCreateClient

from app.infrastructure.database.db import get_db
from sqlmodel import Session, select, col, and_, cast, distinct
from psycopg2.errors import UniqueViolation as psycopg2UniqueViolation

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import JSONB

from app.app.errors.db_error import DBError

logger = logging.getLogger(__name__)

class ClientRepository():
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def add(self, client: ClientCreate) -> ClientRead:
        try:
            client_obj = Client.from_orm(client)
            self.db.add(client_obj)
            self.db.commit()
            self.db.refresh(client_obj)

            return ClientRead.from_orm(client_obj)
        
        except Exception as e:
            logger.exception(msg="Failed to add Client to DB.")
            raise DBError(
                origin="ClientRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Student."
            ) from e

    async def get(self, platform_id: str) -> ClientRead:
        try:
            return self.db.exec(
                select(Client).where(col(Client.platform_id) == platform_id)
            ).first()
        
        except Exception as e:
            logger.exception(msg="Failed to retrieve client")
            raise DBError(
                origin="ClientRepository.get",
                type="QueryExecError",
                status_code=500,
                message="Failed to retrieve client"
            ) from e
        
    async def get_reviewers(self, item: ChangeRequestCreateClient, client_id: int) -> List[int]:
        match item.entity_type:
            case "concept":
                user_filter = item.entity_data.get("subject", '')

                statement = select(Client.id)\
                    .join(ClientToCourse, and_(Client.id == ClientToCourse.client_id, ClientToCourse.is_sme == True))\
                    .join(Course, and_(ClientToCourse.course_id == Course.id, Course.subjects.contains(cast(user_filter, JSONB))))
                
                results = self.db.exec(statement=statement).all()

                self.db.close()

                if client_id not in results:
                    results.append(client_id)
                return results

            case "concept_to_concept":
                #Get all client_ids from client to course where the client is both an sme and the course utilizes both concepts
                target_concepts = [item.entity_data.get("prereq_name", ""), item.entity_data.get("concept_name", "")]

                course_concepts_subquery = (
                    select(ConceptCollection.course_id, ConceptToCollection.concept_name)
                    .join(ConceptToCollection, ConceptCollection.id == ConceptToCollection.collection_id)
                    .where(ConceptToCollection.concept_name.in_(target_concepts))
                    .subquery()
                )
                valid_courses_subquery = (
                    select(course_concepts_subquery.c.course_id)
                    .group_by(course_concepts_subquery.c.course_id)
                    .having(func.count(func.distinct(course_concepts_subquery.c.concept_name)) == 2)
                    .subquery()
                )
                statement = (
                    select(distinct(ClientToCourse.client_id))
                    .join(valid_courses_subquery, valid_courses_subquery.c.course_id == ClientToCourse.course_id)
                    .where(ClientToCourse.is_sme == True)
                )

                results = self.db.exec(statement=statement).all()
                self.db.close()

                if client_id not in results:
                    results.append(client_id)

                return results

            case "question":
                #TODO: Get all client_ids from client to course where the client is both an sme and the course utilizes the concept attached to the question
                return [client_id]

            case "answer":
                #TODO: Get all client_ids from client to course where the client is both an sme and the course utilizes the concept attached to the question
                return [client_id]

class ClientToCourseRepository():
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def add(self, junction: ClientToCourseCreate) -> ClientToCourseRead:
        try:
            junction_obj = ClientToCourse.from_orm(junction)
            self.db.add(junction_obj)
            self.db.commit()
            self.db.refresh(junction_obj)

            return ClientToCourseRead.from_orm(junction_obj)
        
        except IntegrityError as e:
            logger.warn(msg="Junction between course as client already exists")
            raise DBError(
                origin="ClientToCourseRepository.add",
                type="UniqueViolation",
                status_code=500,
                message="Junction between course as client already exists"
            ) from e 

        except Exception as e:
            logger.exception(msg=f"Failed to add Client to course.\nCause:\n{e}")
            raise DBError(
                origin="ClientToCourseRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Student to course."
            ) from e    


class StudentKnowledgeRepository():
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def get(self, student_id:int, concept_name:str) -> StudentKnowledgeRead:
        try:
            stmt = select(StudentKnowledge).where(StudentKnowledge.concept_name == concept_name).where(StudentKnowledge.student_id == student_id)
            return self.db.exec(stmt).one_or_none()
        
        except Exception as e:
            logger.exception(msg=f"Failed to retrieve student knowledge with student_id: {student_id} and concept_name: {concept_name}")
            raise DBError(
                origin="StudentKnowledgeRepository.get",
                type="QueryExecError",
                status_code=500,
                message=f"Failed to retrieve student knowledge with student_id: {student_id} and "
                        f"concept_name: {concept_name}, {e}"
            ) from e

    async def bulk_get(self, student_id: int, concept_list: List[str]) -> List[
        StudentKnowledgeRead]:
        try:
            stmt = select(StudentKnowledge).where(
                col(StudentKnowledge.concept_name).in_(concept_list)).where(
                col(StudentKnowledge.student_id) == student_id)
            result = self.db.exec(statement=stmt)
            result = StudentKnowledgeRead.from_orm(result.all())
            self.db.close()
            return result

        except Exception as e:
            logger.exception(
                msg=f"Failed to retrieve student knowledge with student_id: {student_id} and "
                    f"concepts: {concept_list}")
            raise DBError(
                origin="StudentKnowledgeRepository.get",
                type="QueryExecError",
                status_code=500,
                message=f"Failed to retrieve student knowledge with student_id: {student_id} and "
                        f"concepts: {concept_list}, {e}"
            ) from e

    async def add(self, score: StudentKnowledgeCreate) -> StudentKnowledgeRead:
        try:
            knowledge_obj = StudentKnowledge.from_orm(score)
            self.db.add(knowledge_obj)
            self.db.commit()
            self.db.refresh(knowledge_obj)
            result = StudentKnowledgeRead.from_orm(knowledge_obj)
            self.db.close()
            return result
        
        except Exception as e:
            logger.exception(msg="Failed add new student knowledge entry.")
            raise DBError(
                origin="StudentKnowledgeRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed add new student knowledge entry."
            ) from e
    
    async def update(self, score: StudentKnowledgeCreate) -> StudentKnowledgeRead:
        try:
            stmt = select(StudentKnowledge).where(StudentKnowledge.concept_name == score.concept_name).where(StudentKnowledge.student_id == score.student_id)
            result = self.db.exec(statement=stmt)

            knowledge = result.one_or_none()
            knowledge.score = score.score
            knowledge.no_of_inputs = score.no_of_inputs
            knowledge.numerator = score.numerator
            knowledge.denominator = score.denominator


            self.db.add(knowledge)

            # flag_modified(knowledge, 'change_history')
            self.db.commit()

            self.db.refresh(knowledge)
            result = StudentKnowledgeRead.from_orm(knowledge)

            self.db.close()
            return result
    
        except Exception as e:
            logger.exception(msg="Failed update student knowledge entry.")
            raise DBError(
                origin="StudentKnowledgeRepository.update",
                type="QueryExecError",
                status_code=500,
                message="Failed update student knowledge entry."
            ) from e

    async def get_many(self, concepts: ConceptBulkRead, student_id: int) -> List[StudentKnowledgeRead]:
        concept_list = [concept.name for concept in concepts.concepts]
        try:
            stmt = select(StudentKnowledge).where(StudentKnowledge.student_id == student_id).filter(StudentKnowledge.concept_name.in_(concept_list))
            result = self.db.exec(statement=stmt)
            result = result.all()
            return [StudentKnowledgeRead.model_validate(item) for item in result]
        
        except Exception as e:
            logger.exception(msg="Failed retrieve student knowledge entries.")
            raise DBError(
                origin="StudentKnowledgeRepository.get_many",
                type="QueryExecError",
                status_code=500,
                message="Failed retrieve student knowledge entries."
            ) from e