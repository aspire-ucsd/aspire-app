from typing import Protocol, List



class DomainService(Protocol):
    async def get_all_subjects(self) -> List[str]:
        """
        Retrieves all subjects logged in the domain
        """
        pass
