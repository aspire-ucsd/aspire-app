import logging

from typing import List, Union, Literal

from psycopg2.errors import  ForeignKeyViolation
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Session, text, bindparam, select, join, alias, or_, cast

from app.infrastructure.database.db import get_db

from app.app.errors.db_error import DBError
from app.domain.models.errors import DBError as DBErrorObj

from app.domain.models.concept_collection import ConceptCollection

from app.domain.models.concept import (
    Concept,
    ConceptRead, 
    ConceptCreate, 
    ConceptCreateBulkRead,
    ConceptToCollection,
    ConceptToCollectionRead,
    ConceptToCollectionCreate,
    ConceptToConceptCreate,
    ConceptToConceptRead, 
    ConceptToConcept,
    ConceptFilter,
    ConceptBulkRead,
    ConceptReadVerbose,
    ConceptToCollectionDelete,
    ConceptToConceptDelete,
    )

from app.domain.protocols.repositories.concept import (
    ConceptRepository as ConceptRepositoryProtocol, 
    ConceptToModuleRepository as CToMRepoProtocol,
    ConceptToConceptRepository as CToCRepoProtocol
    )

logger = logging.getLogger(__name__)

class ConceptRepository(ConceptRepositoryProtocol):
    db: Session

    def __init__(self):
        self.db = get_db()

    async def add(self, concept: ConceptCreate) -> ConceptRead:
        """
        Creates a new Concept
        """
        try:
            stmt = Concept.model_validate(concept)
            self.db.add(stmt)
            self.db.commit()
            self.db.refresh(stmt)

            result = ConceptRead.model_validate(stmt)

            self.db.close()

            return result
        
        except IntegrityError as e:
            logger.exception(msg="Failed to add Concept object direct result")
            raise DBError(
                origin="ConceptRepository.add", 
                type="ForeignKeyViolation" if isinstance(e.orig, ForeignKeyViolation) else "UniqueViolation",
                status_code=400,
                message=str(e.orig)
                ) from e


    async def bulk_add(self, concepts: List[ConceptCreate]) -> ConceptCreateBulkRead:
        """
        Creates a new Concept entry in the DB for each item in the list of concepts.
        Ignores and logs any unique value violations.
        """
        with self.db.begin():
            query_template = """
                INSERT INTO concept(name, subject, difficulty) 
                VALUES(:name, :subject, :difficulty) 
                RETURNING name
                """

            compiled_query = text(query_template)

            failed_inserts = []
            successful_inserts = []

            for obj in concepts:
                query_params = dict(obj)
                nested = self.db.begin_nested()

                try:   
                    results = self.db.exec(statement=compiled_query, params=query_params)
                    successful_inserts.extend([ConceptRead(**val) for val in results.mappings().fetchall()])
                    nested.commit()

                except IntegrityError as e:
                    failed_inserts.append(
                        DBErrorObj(
                            cause="UniqueViolation", 
                            object_id=obj.name
                            )
                        )
                    nested.rollback()
                except StatementError as e:
                    logger.warn(msg=f"Concept Formatting Error, missing required value(s): {obj}")
                    failed_inserts.append(
                        DBErrorObj(
                            cause="StatementError", 
                            object_id=str(obj)
                            )
                        )
                    nested.rollback()

            if failed_inserts:
                logger.warn(msg=f"Failed to add the following Concept object(s):\n{failed_inserts}")
            return ConceptCreateBulkRead(success=successful_inserts, failed=failed_inserts)


    async def get_one(self, concept_name: str, read_mode: Literal["normal", "verbose"] = "normal") -> Union[ConceptRead, ConceptReadVerbose]:
        try:
            query_stmt = text("SELECT * FROM concept WHERE name = :name")
            results = self.db.exec(statement=query_stmt, params={"name": concept_name})

            if read_mode == "normal":
                return ConceptRead(**results.mappings().fetchone())
            
            else:
                return ConceptReadVerbose(**results.mappings().fetchone())
            
        except Exception as e:
            logger.exception(msg="Failed to return concept object.")
            raise DBError(
                origin="ConceptToConceptRepository.get_one",
                type="QueryExecError",
                status_code=500,
                message="Failed to return concept object."
            ) from e  


    async def get_many(self, filters: ConceptFilter, read_mode: Literal["normal", "verbose"] = "normal") -> Union[List[ConceptRead], List[ConceptReadVerbose]]:
        statement = select(Concept).distinct()
        concept_to_collection_alias_a = alias(ConceptToCollection)
        concept_to_collection_alias_b = alias(ConceptToCollection)

        for key, filter_clause in filters.dict(exclude_none=True).items():

            if key == "module_id":

                statement = statement.join(
                    concept_to_collection_alias_a, 
                    (concept_to_collection_alias_a.c.collection_id == filter_clause) 
                    & 
                    (concept_to_collection_alias_a.c.concept_name == Concept.name)
                    )

            elif key == "course_id":

                statement = statement.join(
                    concept_to_collection_alias_b, 
                    Concept.name == concept_to_collection_alias_b.c.concept_name
                        ).join(
                            ConceptCollection, 
                            (ConceptCollection.id == concept_to_collection_alias_b.c.collection_id) 
                            & 
                            (ConceptCollection.course_id == filter_clause)
                            )
                
            elif key == "subjects":
                filter_clause = filter_clause.split('|')
                statement = statement.where(Concept.subject.in_(filter_clause))

            else:
                column = getattr(Concept, key)
                statement = statement.where(column==filter_clause)

        try:
            results = self.db.exec(statement=statement)
            if read_mode == "normal":
                return [ConceptRead.from_orm(v) for v in results.fetchall()]
            
            else:
                return [ConceptReadVerbose.from_orm(v) for v in results.fetchall()]
        
        except Exception as e:
            logger.exception(msg=f"Failed to retrieve concept(s) with filters: {filters.dict()}.")
            raise DBError(
                origin="ConceptRepository.get_many", 
                type="QueryExecError", 
                status_code=500, 
                message="Failed to select concepts"
                ) from e


    async def exists(self, concept_names: List[str]) -> dict:
        try:
            query_stmt = text("""
                WITH input_names AS (
                    SELECT unnest(array[:concept_names])::text AS name
                ),
                existing_concepts AS (
                    SELECT name
                    FROM concept
                    WHERE LOWER(name) = ANY(array[:concept_names])
                )
                SELECT
                    array_agg(existing_concepts.name) FILTER (WHERE existing_concepts.name IS NOT NULL) AS matched_concepts,
                    array_agg(input_names.name) FILTER (WHERE existing_concepts.name IS NULL) AS unmatched_concepts
                FROM (
                    SELECT LOWER(name) AS name
                    FROM input_names
                ) AS input_names
                LEFT JOIN (
                    SELECT LOWER(name) AS name
                    FROM existing_concepts
                ) AS existing_concepts
                ON input_names.name = existing_concepts.name;
            """)
            result = self.db.exec(statement=query_stmt, params={"concept_names": concept_names})
            return result.mappings().one()
        
        except Exception as e:
            logger.exception(msg="Failed to check concepts.")
            raise DBError(
                origin="ConceptRepository.exists",
                type="QueryExecError",
                status_code=500,
                message="Failed to check concepts."
            ) from e


    async def update_one(
        self,
        concept_name,
        updated_concept_object: ConceptCreate
    ) -> ConceptRead:
        """ This function updates a single concept of given name.

        Args:
            concept_name: Name of the concept (Also PK of the table)
            updated_concept_object: Object containing the updated concept information.

        Returns:
            Updated Concept Value.
        """
        try:
            concept = self.db.exec(
                statement=select(Concept).where(Concept.name == concept_name)
            )
            concept = concept.one_or_none()
        except Exception as e:
            logger.exception(
                msg=f"Concept matching name '{concept_name}' not found")
            raise DBError(
                origin="ConceptRepository.update_one",
                type="QueryError",
                status_code=404,
                message=f"Concept matching name '{concept_name}' not found"
            ) from e

        try:
            concept.sqlmodel_update(updated_concept_object.model_dump(exclude_unset=True))

            self.db.add(concept)
            self.db.commit()

        except Exception as e:
            logger.exception(msg="Failed to update Concept object.")
            raise DBError(
                origin="ConceptRepository.update_one",
                type="ReturnError",
                status_code=500,
                message="Failed to update Concept object."
            ) from e
        try:
            self.db.refresh(concept)
            self.db.close()
            return ConceptRead.model_validate(concept)

        except Exception as e:
            logger.exception(msg="Failed to update Concept object.")
            raise DBError(
                origin="ConceptRepository.update_one",
                type="ReturnError",
                status_code=500,
                message="Failed to update Concept object."
            ) from e

    async def delete_one(self, concept_name: str) -> None:
        """ This function deletes a given a concept name.

        Args:
            concept_name: Name of the concept (this is also the PK in the table)

        Raises:
            DBError: If concept with given name  is not found.

        Returns:
            None
        """
        try:
            concept = self.db.exec(
                statement=select(Concept).where(Concept.name == concept_name)
            )
            concept = concept.one_or_none()
        except Exception as e:
            logger.exception(
                msg=f"Concept matching name '{concept_name}' not found")
            raise DBError(
                origin="ConceptRepository.delete_one",
                type="QueryError",
                status_code=404,
                message=f"Concept matching name '{concept_name}' not found"
            ) from e
        try:
            self.db.delete(concept)
            self.db.commit()
            self.db.close()

        except Exception as e:
            logger.exception(msg=f"Failed to delete Concept object of name '{concept_name}'")
            raise DBError(
                origin="ConceptRepository.delete_one",
                type="QueryError",
                status_code=500,
                message=f"Failed to delete Concept object of name '{concept_name}'"
            ) from e
        

class ConceptToModuleRepository(CToMRepoProtocol):
    db: Session

    def __init__(self):
        self.db = get_db()


    async def add(self, junction: ConceptToCollectionCreate) -> ConceptToCollectionRead:
        try:
            db_junction = ConceptToCollection.from_orm(junction)
            self.db.add(db_junction)
            self.db.commit()
            self.db.refresh(db_junction)

            return ConceptToCollectionRead(**dict(db_junction))
        
        except Exception as e:
            logger.exception(msg=f"Failed to add ConceptToModule object.")
            raise DBError(
                origin="ConceptToModuleRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add module junction"
            ) from e

    async def bulk_add(self, junctions: List[ConceptToCollectionCreate]) -> List[ConceptToCollectionRead]:
        try:
            db_junctions = [ConceptToCollection(**junction.dict()) for junction in junctions]
            
            self.db.add_all(db_junctions)
            self.db.commit()

        except Exception as e:
            logger.exception(msg=f"Failed to add ConceptToModule object(s).")
            raise DBError(
                origin="ConceptToModuleRepository.bulk_add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add module junctions"
            ) from e
        
        try:
            for object in db_junctions:
                self.db.refresh(object)

            return [ConceptToCollectionRead(**dict(val)) for val in db_junctions]
        
        except Exception as e:
            logger.exception(msg=f"Failed to return ConceptToModule object.")
            raise DBError(
                origin="ConceptToModuleRepository.bulk_add",
                type="ReturnError",
                status_code=500,
                message="Failed to return module junction objects"
            ) from e
        

    async def get_all(self, module_id: int) -> ConceptBulkRead:
        try:
            query_stmt = text("SELECT concept_name FROM concept_to_module WHERE module_id = "
                              ":module_id")
            result = self.db.exec(statement=query_stmt, params={"module_id": module_id})
            result = result.mappings().fetchall()
            if not result:
                raise DBError(
                    origin="ConceptToModuleRepository.get_all",
                    type="ReturnError",
                    status_code=404,
                    message=f"No concepts found at module_id: {module_id}"
                )
            
            return ConceptBulkRead(concepts=[ConceptRead(name=val["concept_name"]) for val in result])
        
        except Exception as e:
            logger.exception(msg=f"Failed to add ConceptToModule object(s) at module_id: {module_id}.")
            raise DBError(
                origin="ConceptToModuleRepository.get_all",
                type="QueryExecError",
                status_code=500,
                message="Failed to return module junction objects"
            ) from e  
        
    async def delete(self, junctions: List[ConceptToCollectionDelete]):
        query_stmt = text("DELETE FROM concept_to_collection WHERE collection_id = :collection_id AND concept_name = :concept_name")

        for item in junctions:
            try: 
                self.db.exec(statement=query_stmt, params=item.dict())
                self.db.commit()

            except Exception as e:
                logger.exception(msg=f"Failed to delete ConceptToModule object(s): {item}.")
                raise DBError(
                    origin="ConceptToModuleRepository.delete",
                    type="QueryExecError",
                    status_code=500,
                    message=f"Failed to delete ConceptToModule object(s): {item}"
                ) from e  


class ConceptToConceptRepository(CToCRepoProtocol):
    db: Session

    def __init__(self):
        self.db = get_db()


    async def add(self, junction: ConceptToConceptCreate) -> ConceptToConceptRead:
        try:
            db_junction = ConceptToConcept.from_orm(junction)

            self.db.add(db_junction)
            self.db.commit()
            self.db.refresh(db_junction)

            return ConceptToConceptRead(**dict(db_junction))
        
        except Exception as e:
            logger.exception(msg="Failed to add ConceptToConcept object.")
            raise DBError(
                origin="ConceptToConceptRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add concept junction"
            ) from e          


    async def bulk_add(self, junctions: List[ConceptToConceptCreate]) -> List[ConceptToConceptRead]:
        try:
            with self.db.no_autoflush as session:
                db_junctions = [ConceptToConcept.from_orm(junction) for junction in junctions]
                with session.begin(nested=True):
                    for obj in db_junctions:
                        nested = session.begin_nested()
                        try:
                            session.add(obj)
                            nested.commit()
                            session.refresh(obj)
                            
                        except IntegrityError as e:
                            nested.rollback()
                            
                result = [ConceptToConceptRead(**val.dict()) for val in db_junctions]
                session.commit()
                return result
        
        except Exception as e:
            logger.exception(msg="Failed to add ConceptToConcept object(s).")
            raise DBError(
                origin="ConceptToConceptRepository.bulk_add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add concept junctions"
            ) from e  


    async def get_some(self, concepts: List[ConceptRead], junction_direction: Literal["up", "down", "both"]="down") -> List[ConceptToConceptRead]:
        try:
            concept_names = [val.name for val in concepts]
            query_stmt_options = {
                "down": select(ConceptToConcept).where(ConceptToConcept.concept_name.in_(concept_names)),
                "up": select(ConceptToConcept).where(ConceptToConcept.prereq_name.in_(concept_names)),
                "both": select(ConceptToConcept).where(or_(ConceptToConcept.concept_name.in_(concept_names), ConceptToConcept.prereq_name.in_(concept_names)))
            }

            query_stmt = query_stmt_options[junction_direction]
            result = self.db.exec(statement=query_stmt)
            results = [ConceptToConceptRead.model_validate(val) for val in result.fetchall()]

            self.db.close()
            
            return results
        
        except Exception as e:
            logger.exception(msg=f"Failed to get ConceptToConcept object(s) with direction: {junction_direction}.")
            raise DBError(
                origin="ConceptToConceptRepository.get_some",
                type="QueryExecError",
                status_code=500,
                message="Failed to retrieve concept junctions"
            ) from e    


    async def delete(self, junctions: List[ConceptToConceptDelete]):
        query_stmt = text("DELETE FROM concept_to_concept WHERE prereq_name = :prereq_name AND concept_name = :concept_name")

        for item in junctions:
            try: 
                self.db.exec(statement=query_stmt, params=item.dict())
                self.db.commit()

            except Exception as e:
                logger.exception(msg=f"Failed to delete ConceptToConcept object(s): {item}.")
                raise DBError(
                    origin="ConceptToConceptRepository.delete",
                    type="QueryExecError",
                    status_code=500,
                    message=f"Failed to delete ConceptToConcept object(s): {item}."
                ) from e

    async def update_one(
            self,
            junction: ConceptToConceptCreate,
            updated_junction: ConceptToConceptCreate
    ) -> ConceptToConceptRead:
        """ Updates given junction.

        Notes:
            Designed this way because all rows serve as the PK of the table.

        Args:
            junction: Concept To Concept Junction

        Returns:
            Updated ConceptToConcept Object
        """
        try:
            extracted_junction = self.db.exec(
                statement=select(ConceptToConcept).where(
                    ConceptToConcept.concept_name == junction.concept_name
                ).where(
                    ConceptToConcept.prereq_name == junction.prereq_name
                )
            ).one_or_none()
            extracted_junction.sqlmodel_update(updated_junction.model_dump(exclude_unset=True))

            self.db.add(extracted_junction)
            self.db.commit()

        except Exception as e:
            logger.exception(msg="Failed to update ConceptToConcept object.")
            raise DBError(
                origin="ConceptToConceptRepository.update_one",
                type="ReturnError",
                status_code=500,
                message="Failed to update ConceptToConcept object."
            ) from e
        try:
            self.db.refresh(extracted_junction)
            self.db.close()
            return ConceptToConceptRead.model_validate(extracted_junction)

        except Exception as e:
            logger.exception(msg="Failed to update ConceptToConcept object.")
            raise DBError(
                origin="ConceptToConceptRepository.update_one",
                type="ReturnError",
                status_code=500,
                message="Failed to update ConceptToConcept object."
            ) from e
