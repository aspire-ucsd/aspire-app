from typing import List, Protocol, Literal, Union

from app.domain.models.concept import (
    ConceptCreate, 
    ConceptRead, 
    ConceptCreateBulkRead, 
    ConceptToCollectionCreate, 
    ConceptToCollectionRead,
    ConceptToConceptCreate,
    ConceptToConceptRead,
    ConceptFilter,
    ConceptBulkRead,
    ConceptReadVerbose,
    ConceptToCollectionDelete,
    ConceptToConceptDelete,

    )

class ConceptRepository(Protocol):
    async def add(self, concept: ConceptCreate) -> ConceptRead:
        """
        Adds a single concept to the db
        """
        ...

    async def bulk_add(self, concepts: List[ConceptCreate]) -> ConceptCreateBulkRead:
        """
        Adds many concepts to the db
        """
        ...

    async def get_one(self, concept_name: str, read_mode: Literal["normal", "verbose"] = "normal") -> Union[ConceptRead, ConceptReadVerbose]:
        """
        Returns a single concept filtered by name, 
        use read_mode='normal' for checking if a concept exists in the db,
        use read_mode='verbose' to return the details of a concept.

        :param concept_name: the name of the concept as a string
        :param read_mode: ('normal', 'verbose') in 'normal' mode just returns the concept name (useful to check if the concept exists in the db), in 'verbose' mode returns all the details of the concept
        """
        ...

    async def get_many(self, filters: ConceptFilter, read_mode: Literal["normal", "verbose"] = "normal") -> Union[List[ConceptRead], List[ConceptReadVerbose]]:
        """
        Returns all concepts matching a set of filters.
        :param filters: ConceptFilter(course_id: Optional[int], subject: Optional[str], difficulty: Optional[int]) - specifies which params to filter concepts by.
        :param read_mode: ('normal', 'verbose') in 'normal' mode returns only the concept name for each matching concept, in 'verbose' mode returns all the details of each matching concept
        """
        ...

    async def delete_one(self, concept_name: str) -> None:
        """ This function deletes a single concept from the Database

        Args:
            concept_name: Name of the concept to be deleted. (PK of the table)

        Raises:
            DBError: If concept with given name  is not found.

        Returns:
            None
        """
        ...

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
        ...


class ConceptToModuleRepository(Protocol):
    async def add(self, junction: ConceptToCollectionCreate) -> ConceptToCollectionRead:
        """
        Creates one ConceptToModule junction
        """        
        ...

    async def bulk_add(self, junctions: List[ConceptToCollectionCreate]) -> List[ConceptToCollectionRead]:
        """
        Creates many ConceptToModule junctions
        """
        ...

    async def get_all(self, module_id: int) -> ConceptBulkRead:
        """
        Returns all concepts inside a module
        """
        ...

    async def delete(self, junctions: List[ConceptToCollectionDelete]):
        """
        Removes a concept from a module
        """       
        ...

class ConceptToConceptRepository(Protocol):
    async def add(self, junction: ConceptToConceptCreate) -> ConceptToConceptRead:
        """
        Adds a single ConceptToConcept junction
        """
        ...

    async def bulk_add(self, junctions: List[ConceptToConceptCreate]) -> List[ConceptToConceptRead]:
        """
        Adds many ConceptToConcept junctions
        """
        ...

    async def get_some(
            self, 
            concepts: List[ConceptRead], 
            junction_direction: Literal["up", "down", "both"]="down"
    ) -> List[ConceptToConceptRead]:
        """
        Returns the concept-to-concept relationships of specified concepts based on a specified junction_direction

        :param concepts: A ConceptBulkRead object containing a list of ConceptReads, used to filter which concepts to return the relationships of.
    
        :param junction_direction: ('up', 'down', 'both') The orientation of the relationship. 'up' returns all concepts dependent on the supplied concept, 'down' returns the prerequisites of the supplied concept, 'both' returns both.
    
        """
        ...

    async def delete(self, junctions: List[ConceptToConceptDelete]):
        """
        Deletes one or many ConceptToConcept junctions
        """
        ...

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
            updated_junction: Updates to be made.

        Returns:
            Updated ConceptToConcept Object
        """
        ...