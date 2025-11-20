import logging

from typing import Union
from fastapi import Depends
from sqlmodel import Session, select

from app.infrastructure.database.db import get_db

from app.app.errors.db_error import DBError

from app.domain.protocols.repositories.platform_config import PlatformConfigRepository as PlatformConfigRepoProtocol

from app.domain.models.platform_config import PlatformConfig, PlatformConfigCreate, PlatformConfigRead

logger = logging.getLogger(__name__)

class PlatformConfigRepository(PlatformConfigRepoProtocol):
    db: Session
    
    def __init__(self):
        self.db = get_db()

    async def add(self, platform_config: PlatformConfigCreate) -> PlatformConfigRead:
        try:
            platform_config_table = PlatformConfig.from_orm(platform_config)
            self.db.add(platform_config_table)
            self.db.commit()
            self.db.refresh(platform_config_table)
            return PlatformConfigRead(**dict(platform_config_table))
        
        except Exception as e:
            logger.exception(msg="Failed to add Platform Config object.")
            raise DBError(
                origin="PlatformConfigRepository.add",
                type="QueryExecError",
                status_code=500,
                message="Failed to add Platform Config object."
            ) from e
        
    async def get(self, client_id: str) -> PlatformConfigRead:
        try:
            statement = select(PlatformConfig).where(PlatformConfig.CLIENT_ID == client_id)
            results = self.db.exec(statement=statement)
            return PlatformConfigRead(**dict(results.one()))
        
        except Exception as e:
            logger.exception(msg="Failed to retrieve Platform Config object.")
            raise DBError(
                origin="PlatformConfigRepository.get",
                type="QueryExecError",
                status_code=500,
                message="Failed to retrieve Platform Config object."
            ) from e