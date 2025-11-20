from typing import List
from fastapi import Depends


from app.domain.protocols.repositories.domain import DomainRepository as DomainRepoProtocol
from app.infrastructure.database.repositories.domain import DomainRepository

from app.domain.protocols.services.domain import DomainService as DomainServiceProtocol



class DomainService(DomainServiceProtocol):
    def __init__(
        self,
        domain_repo: DomainRepoProtocol = Depends(DomainRepository)
    ):
        self.domain_repo = domain_repo

    async def get_all_subjects(self) -> List[str]:
        return await self.domain_repo.get_subjects()


