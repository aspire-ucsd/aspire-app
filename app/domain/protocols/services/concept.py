from typing import List, Protocol, Literal, Union, Set, Optional, Dict

from app.domain.models.concept import (
    ConceptRead, 
    ConceptCreate, 
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
    ConceptReadPreformatted
)


class ConceptService(Protocol):
    async def create_concept(self, concept: ConceptCreate) -> ConceptRead:
        """
        Inserts a single Concept to the DB.
        """
        ...

    async def bulk_create_concepts(self, concepts: List[ConceptCreate]) -> ConceptCreateBulkRead:
        """
        Attempts to insert a list of concepts to the DB, 
        returns a ConceptCreateBulkRead object containing a list of successful inserts and a list of failed inserts along with the cause of failure
        """
        ...

    async def get_concept(self, concept_name: str, read_mode: Literal["normal", "verbose"] = "normal") -> Union[ConceptRead, ConceptReadVerbose]:
        """
        Returns a single concept filtered by name, 
        use read_mode='normal' for checking if a concept exists in the db,
        use read_mode='verbose' to return the details of a concept.

        :param concept_name: the name of the concept as a string
        :param read_mode: ('normal', 'verbose') in 'normal' mode just returns the concept name (useful to check if the concept exists in the db), in 'verbose' mode returns all the details of the concept
        """
        ...
        
    async def get_many_concepts(self, filters: ConceptFilter, read_mode: Literal["normal", "verbose"] = "normal") -> Union[List[ConceptRead], List[ConceptReadVerbose]]:
        """
        Returns all concepts matching a set of filters.
        :param filters: ConceptFilter(course_id: Optional[int], subject: Optional[str], difficulty: Optional[int]) - specifies which params to filter concepts by.
        :param read_mode: ('normal', 'verbose') in 'normal' mode returns only the concept name for each matching concept, in 'verbose' mode returns all the details of each matching concept
        """
        ...

    async def get_all_concepts_from_collections(self, collection_ids:Set[int], course_id=Optional[int]) -> Dict[str, ConceptReadPreformatted]:
        """
        Returns all the concepts belonging to supplied collections, formatted as required for domain visualization and editing
        """
        ...

    async def init_module_concepts(
            self, 
            module_id: int, 
            llm_concepts: List[ConceptCreate],
            llm_junctions: List[ConceptToConceptCreate],
            module_concepts: List[str]
    ) -> ConceptCreateBulkRead:
        ...

    async def delete_one_concept(self, concept_name) -> None:
        """ This function deletes a single concept of given name.

        Args:
            concept_name: Name of concept to be deleted

        Returns:
            None
        """
        ...

    async def update_one_concept(
            self,
            concept_name: str,
            updated_concept: ConceptCreate
    ) -> ConceptRead:
        """ This function updates a single concept of given name.

        Args:
            concept_name: Name of the concept (Also PK of the table)
            updated_concept: Object containing the updated concept information.

        Returns:
            Updated Concept Value.
        """
        ...


class ConceptToModuleService(Protocol):
    async def create_module_junction(self, junction: ConceptToCollectionCreate) -> ConceptToCollectionRead:
        """Creates a single Concept to Collection/Module junction"""
        ...

    async def bulk_create_module_junctions(self, junctions: List[ConceptToCollectionCreate]) -> list[ConceptToCollectionRead]:
        """
        Creates many ConceptToModule junctions
        """
        ...

    async def get_all_concepts_in_module(self, module_id: int) -> ConceptBulkRead:
        """
        Returns all concepts inside a module
        """
        ...

    async def get_all_prereqs_of_module(self, module_id: int)-> ConceptBulkRead:
        """
        Returns all concepts that are direct prerequisites of concepts within a module but are not contained inside the module 
        AKA concepts that are prerequisite to start a module
        """
        ...

    async def delete_module_junctions(self, junctions: List[ConceptToCollectionDelete]):
        """
        Removes a concept from a module
        """
        ...

class ConceptToConceptService(Protocol):
    async def create_concept_junction(self, junction: ConceptToConceptCreate) -> (
            ConceptToConceptRead):
        """ This function create a single Concept to Concept Junction

        Args:
            junction: Concept to Concept Junction

        Returns:
            Created Junction
        """
        ...

    async def bulk_create_concept_junctions(self, junctions: List[ConceptToConceptCreate]) -> List[ConceptToConceptRead]:
        """
        Creates many ConceptToConcept junctions
        """
        ...

    async def get_concept_junctions(self, concepts: List[ConceptRead], junction_direction: Literal["up", "down", "both"]="down") -> List[ConceptToConceptRead]:
        """
        Returns the concept-to-concept relationships of specified concepts based on a specified junction_direction

        :param concepts: A ConceptBulkRead object containing a list of ConceptReads, used to filter which concepts to return the relationships of.
    
        :param junction_direction: ('up', 'down', 'both') The orientation of the relationship. 'up' returns all concepts dependent on the supplied concept, 'down' returns the prerequisites of the supplied concept, 'both' returns both.
    
        """
        ...

    async def delete_junctions(self, junctions: List[ConceptToConceptDelete]):
        """
        Deletes a ConceptToConcept junction.
        """
        ...

    async def update_one_junction(
            self,
            junction: ConceptToConceptCreate,
            updated_junction: ConceptToConceptCreate
    ) -> ConceptToConceptRead:
        """ This function updates a given concept to concept junction.

        Notes:
            Designed this way because all rows serve as the PK of the table.

        Args:
            updated_junction: This is the update to be made
            junction: Concept to Concept Junction

        Returns:
            Updated Concept to Concept Junction
        """
        ...