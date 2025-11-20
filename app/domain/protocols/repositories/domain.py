from typing import Protocol, List



class DomainRepository(Protocol):
    """
    Repository interface for accessing misc. information about the ASPIRE domain 
    """
    async def get_subjects(self) -> List[str]:
        """
        Retrieves all subjects logged in the domain
        """
        pass