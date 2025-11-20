from typing import List
import logging

from app.domain.protocols.repositories.domain import DomainRepository as DomainRepoProtocol

from app.domain.models.concept import Concept

from app.infrastructure.database.db import get_db
from sqlmodel import Session, select, distinct


from app.app.errors.db_error import DBError

logger = logging.getLogger(__name__)

class DomainRepository(DomainRepoProtocol):
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def get_subjects(self) -> List[str]:
        try:
            return self.db.exec(
                select(distinct(Concept.subject))
            ).all()
        
        except Exception as e:
            logger.exception(msg="Failed to retrieve subject list")
            raise DBError(
                origin="ClientRepository.get",
                type="QueryExecError",
                status_code=500,
                message="Failed to retrieve subject list"
            ) from e