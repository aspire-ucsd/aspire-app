import logging

from typing import Optional, List, Literal, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only
from fastapi import Depends
from sqlmodel import Session, text, select

from app.infrastructure.database.db import get_db

from app.app.errors.db_error import DBError

from app.domain.protocols.repositories.concept_collection import CollectionRepository as CollectionRepoProtocol
from app.domain.models.concept_collection import CollectionRead, CollectionUpdate, ConceptCollection, CollectionCreateExtended

logger = logging.getLogger(__name__)

class CollectionRepository(CollectionRepoProtocol):
    ''' 
    Provides data access to collection models.
    '''
    
    db: Session
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, collection: CollectionCreateExtended) -> CollectionRead:
        try:
            new_collection = ConceptCollection.model_validate(collection)
            self.db.add(new_collection)
            self.db.commit()

        except Exception as e:
            logger.exception(msg=f"Failed to add Collection object.")
            raise DBError(
                origin="CollectionRepository.add",
                type="ReturnError",
                status_code=500,
                message="Failed to add collection"
            ) from e
        
        try:
            self.db.refresh(new_collection)
            self.db.close()
            return CollectionRead.model_validate(new_collection)
        
        except Exception as e:
            logger.exception(msg=f"Failed to return new Collection object.")
            raise DBError(
                origin="CollectionRepository.add",
                type="ReturnError",
                status_code=500,
                message="Failed to return new collection"
            ) from e
        
    
    async def get_one(self, collection_id: int) -> CollectionRead:
        try:
            stmt = select(ConceptCollection).where(ConceptCollection.id == collection_id)
            result = self.db.exec(statement=stmt)
            return CollectionRead.model_validate(result.one().sqlmodel_update)
        
        except Exception as e:
            logger.exception(msg=f"Failed to return collection object at ID: {collection_id}.")
            raise DBError(
                origin="CollectionRepository.get_one",
                type="ReturnError",
                status_code=500,
                message=f"Failed return collection object at ID: {collection_id}."
            ) from e
        
    async def get_all(self, filter_name: Literal["course", "all"], filter_id: Optional[int]=None, id_only:bool=False) -> Union[List[CollectionRead], List[int]]:
        try:
            if id_only:
                stmt = select(ConceptCollection).options(load_only("id"))
            else:
                stmt = select(ConceptCollection)
            
            if filter_name == "course":
                stmt = stmt.where(text(f"course_id = {filter_id}"))

            result = self.db.exec(statement=stmt)
            
            if id_only:
                result = [collection.id for collection in result.all()]

            else:
                result = [CollectionRead.model_validate(collection) for collection in result.all()]

            self.db.close()
            return result
        
        except Exception as e:
            logger.exception(msg="Failed to return collection object(s).")
            raise DBError(
                origin="CollectionRepository.get_one",
                type="ReturnError",
                status_code=500,
                message="Failed to return collection object(s)."
            ) from e
        
    async def update(self, collection_id: int, collection_update: CollectionUpdate) -> CollectionRead:
        try:
            collection = self.db.get(ConceptCollection, collection_id)
            collection.sqlmodel_update(collection_update.model_dump(exclude_unset=True))

            self.db.add(collection)
            self.db.commit()

        except Exception as e:
            logger.exception(msg="Failed to update Collection object.")
            raise DBError(
                origin="CollectionRepository.update",
                type="ReturnError",
                status_code=500,
                message="Failed to update Collection object."
            ) from e
        try:
            self.db.refresh(collection)
            self.db.close()
            return CollectionRead.model_validate(collection)
        
        except Exception as e:
            logger.exception(msg="Failed to update Collection object.")
            raise DBError(
                origin="CollectionRepository.update",
                type="ReturnError",
                status_code=500,
                message="Failed to update Collection object."
            ) from e
    
    async def delete_from_course(self, collection_id: int, course_id: int) -> None:
        try:
            collection = self.db.exec(statement=select(ConceptCollection).where(ConceptCollection.course_id == course_id).where(ConceptCollection.id == collection_id))
            collection = collection.one_or_none()

        except Exception as e:
            logger.exception(msg=f"Collection matching collection_id: {collection_id} AND course_id: {course_id} not found")
            raise DBError(
                origin="CollectionRepository.delete_from_course",
                type="QueryError",
                status_code=404,
                message=f"Collection matching collection_id: {collection_id} AND course_id: {course_id} not found"
            ) from e
        
        try:
            self.db.delete(collection)
            self.db.commit()
            self.db.close()

        except Exception as e:
            logger.exception(msg=f"Failed to delete Collection object matching collection_id: {collection_id} AND course_id: {course_id}")
            raise DBError(
                origin="CollectionRepository.delete_from_course",
                type="QueryError",
                status_code=500,
                message=f"Failed to delete Collection object matching collection_id: {collection_id} AND course_id: {course_id}"
            ) from e