import logging

from typing import List, Literal, Union

from sqlmodel import Session, text, select
from sqlalchemy.exc import NoResultFound

from app.infrastructure.database.db import get_db

from app.app.errors.db_error import DBError
from app.domain.models.course import Course, CourseRead, CourseCreate, CourseFilter, CourseUpdate, CourseReadVerbose
from app.domain.protocols.repositories.course import CourseRepository as CourseRepositoryProtocol

logger = logging.getLogger(__name__)

class CourseRepository(CourseRepositoryProtocol):
    ''' 
    Provides data access to Course models.
    
    '''
    
    db: Session
    
    def __init__(self):
        self.db = get_db()


    async def add(self, course: CourseCreate) -> CourseRead:
        try:
            db_course = Course.model_validate(course)
            self.db.add(db_course)
            self.db.commit()
            self.db.refresh(db_course)
            return CourseRead.model_validate(db_course)
        
        except Exception as e:
            logger.exception(msg="Failed to add Course")
            raise DBError(
                origin="CourseRepository.add", 
                type=e.__class__.__name__, 
                status_code=400, 
                message=str(e.orig)
                ) from e
        

    async def get_one(self, course_id: int, read_mode: Literal["normal", "verbose"] = "normal") -> Union[CourseRead, CourseReadVerbose, None]:
        query_stmt = select(Course).where(Course.id==course_id)
        result = self.db.exec(statement=query_stmt)
        try:
            result = result.one()
            self.db.close()
            if read_mode == "verbose":
                return CourseReadVerbose.model_validate(result)
            else:
                return CourseRead.model_validate(result)
            
        except NoResultFound as e:
            raise DBError(origin="CourseRepository.get_one", type="NoResultFound", status_code=404, message=f"Course with ID: {course_id} not found.") from e\
            
        except Exception as e:
            raise DBError(origin="CourseRepository.get_one", type=e.__class__.__name__, status_code=500, message=f"Failed using ID: {course_id}.") from e
       

    async def get_many(self, filters: CourseFilter) -> List[CourseRead]:
        #TODO: Add more precise error handling
        try:
            if not filters.quarter and filters.quarter_filter:
                filters.quarter_filter = "equal"

            filters = filters.model_dump(exclude_none=True)
            query_stmt = select(Course)

            for key, value in filters.items():
                if key == "quarter_filter":
                    continue

                if key in ["name", "instructor"]:
                    query_stmt.where(f"c.{key} = {value}")

                if key in ["subject", "difficulty"]:
                    query_stmt.where(f"c.{key} = {value}")

                if key == "quarter":
                    date_options = {"equal": "=", "newer": ">", "older": "<", "newer-inclusive": ">=", "older-inclusive": "<="}
                    query_stmt.where(f"c.{key} {date_options[filters['quarter_filter']]} {value}")

            result = self.db.exec(statement=query_stmt)
            return [CourseReadVerbose.model_validate(course) for course in result.all()]
        
        except Exception as e:
            logger.exception(msg="Failed to return Course(s)")
            raise DBError(
                origin="CourseRepository.get_many", 
                type=e.__class__.__name__, 
                status_code=400, 
                message=str(e.orig)
                ) from e
        

    async def update(self, course_id: int, course_update: CourseUpdate) -> CourseReadVerbose:
        try:
            set_stmt = []

            params = course_update.model_dump(exclude_none=True)
            for param in params.keys():
                set_stmt.append(f"{param} = :{param}")

            query_stmt = text(" ".join(["UPDATE course SET", " ,".join(set_stmt), "WHERE course_id = :course_id RETURNING *"]))
            params["course_id"] = course_id

            results = self.db.exec(statement=query_stmt, params=params)
            self.db.commit()

            return CourseReadVerbose(**results.mappings().fetchone())
        
        except Exception as e:
            logger.exception(msg=f"Failed to return Module object.")
            raise DBError(
                origin="ModuleRepository.get_one",
                type="ReturnError",
                status_code=500,
                message="Failed return module"
            ) from e
    

    async def delete(self, course_id: int):
        try:
            query_stmt = text("DELETE FROM course WHERE course_id = :course_id")

            results = self.db.exec(statement=query_stmt, params={"course_id": course_id})
            self.db.commit()
            self.db.close()

            # return CourseReadVerbose(**results.mappings().fetchone())
        
        except Exception as e:
            logger.exception(msg=f"Failed to return Module object.")
            raise DBError(
                origin="ModuleRepository.get_one",
                type="ReturnError",
                status_code=500,
                message="Failed return module"
            ) from e