from typing import List, Union, Literal, Set, Optional, Dict
from fastapi import Depends

from app.domain.models.concept import (
    ConceptCreate, 
    ConceptRead, 
    ConceptCreateBulkRead,
    ConceptToCollectionRead,
    ConceptToCollectionCreate,
    ConceptToConceptCreate,
    ConceptToConceptRead,
    ConceptBulkRead,
    ConceptFilter,
    ConceptReadVerbose,
    ConceptToCollectionDelete,
    ConceptToConceptDelete,
    ConceptReadPreformatted
    )
from app.domain.protocols.repositories.concept import (
    ConceptRepository as ConceptRepoProtocol,
    ConceptToConceptRepository as CToCRepoProtocol, 
    ConceptToModuleRepository as CToMRepoProtocol
    )
from app.domain.protocols.services.concept import (
    ConceptService as ConceptServiceProtocol, 
    ConceptToModuleService as CToCcServiceProtocol,
    ConceptToConceptService as CToCServiceProtocol
    )
from app.infrastructure.database.repositories.concept import (
    ConceptRepository, 
    ConceptToModuleRepository,
    ConceptToConceptRepository
    )


class ConceptService(ConceptServiceProtocol, CToCcServiceProtocol, CToCServiceProtocol):
    def __init__(
        self, 
        concept_repo: ConceptRepoProtocol = Depends(ConceptRepository),
        c_to_m_repo: CToMRepoProtocol = Depends(ConceptToModuleRepository),
        c_to_c_repo: CToCRepoProtocol = Depends(ConceptToConceptRepository),
    ):
        
        self.concept_repo = concept_repo
        self.c_to_m_repo = c_to_m_repo
        self.c_to_c_repo = c_to_c_repo
    

    async def create_concept(self, concept: ConceptCreate) -> ConceptRead:
        return await self.concept_repo.add(concept)
    

    async def bulk_create_concepts(self, concepts: List[ConceptCreate]) -> ConceptCreateBulkRead:
        concepts_result = await self.concept_repo.bulk_add(concepts=concepts)
        return concepts_result


    async def get_concept(self, concept_name: str, read_mode: Literal["normal", "verbose"] = "normal") -> Union[ConceptRead, ConceptReadVerbose]:
        return await self.concept_repo.get_one(concept_name=concept_name, read_mode=read_mode)


    async def get_many_concepts(self, filters: ConceptFilter, read_mode: Literal["normal", "verbose"] = "normal") -> Union[List[ConceptRead], List[ConceptReadVerbose]]:
        return await self.concept_repo.get_many(filters=filters, read_mode=read_mode)


    async def check_if_concepts_exist(self, concept_names: List[str]) -> dict:
        return await self.concept_repo.exists(concept_names=concept_names)
    

    async def get_all_concepts_from_collections(self, collection_ids:Set[int], course_id=Optional[int]) -> Dict[str, ConceptReadPreformatted]:
        concepts = {}
        for collection_id in collection_ids:
            concept_filter = ConceptFilter(course_id=course_id, module_id=collection_id)
            results_list = await self.concept_repo.get_many(filters=concept_filter, read_mode="verbose")
            for concept_item in results_list:
                if concepts.get(concept_item.name) is not None:
                    concepts[concept_item.name].module.append(collection_id) 
                    
                else:
                    concepts[concept_item.name] = ConceptReadPreformatted(**concept_item.model_dump(), module=[collection_id], id=concept_item.name)
        
        return concepts 


    async def init_module_concepts(
            self, 
            module_id: int, 
            llm_concepts: List[ConceptCreate],
            llm_junctions: List[ConceptToConceptCreate],
            module_concepts: List[str]
    ) -> ConceptCreateBulkRead:
        
        concept_results = await self.bulk_create_concepts(concepts=llm_concepts)

        if concept_results.success and concept_results.failed:
            concept_results.success.extend([ConceptRead(name=val.object_id) for val in concept_results.failed if val.cause == "UniqueViolation"])
            all_concepts = concept_results.success
            
        elif concept_results.failed:
            all_concepts = [ConceptRead(name=val.object_id) for val in concept_results.failed if val.cause == "UniqueViolation"]

        else:
            all_concepts = concept_results.success

        module_junctions = [ConceptToCollectionCreate(concept_name=val.name, collection_id=module_id) for val in all_concepts if val.name in module_concepts]

        await self.bulk_create_module_junctions(junctions=module_junctions)

        await self.bulk_create_concept_junctions(junctions=llm_junctions)

        return concept_results

    async def delete_one_concept(self, concept_name: str) -> None:
        await self.concept_repo.delete_one(concept_name=concept_name)

    async def update_one_concept(self, concept_name: str, updated_concept: ConceptCreate) -> ConceptRead:
        return await self.concept_repo.update_one(
            concept_name=concept_name,
            updated_concept_object=updated_concept
        )

    # ConceptToModule Service
    async def create_module_junction(self, junction: ConceptToCollectionCreate) -> ConceptToCollectionRead:
        return await self.c_to_m_repo.add(junction=junction)

    async def bulk_create_module_junctions(self, junctions: List[ConceptToCollectionCreate]) -> list[ConceptToCollectionRead]:
        return await self.c_to_m_repo.bulk_add(junctions=junctions)
    

    async def get_all_concepts_in_module(self, module_id: int) -> ConceptBulkRead:
        return await self.c_to_m_repo.get_all(module_id=module_id)


    async def get_all_prereqs_of_module(self, module_id: int)-> ConceptBulkRead:
        module_concepts = await self.c_to_m_repo.get_all(module_id=module_id)
        module_concept_junctions = await self.c_to_c_repo.get_some(concepts=module_concepts)

        module_concept_list = [val.name for val in module_concepts.concepts]
        prereq_list = list(set([val.prereq_name for val in module_concept_junctions]))

        return ConceptBulkRead(concepts=[ConceptRead(name=val) for val in prereq_list if val not in module_concept_list])


    async def delete_module_junctions(self, junctions: List[ConceptToCollectionDelete]):
        await self.c_to_m_repo.delete(junctions=junctions)


    # ConceptToConcept Service
    async def create_concept_junction(self, junction: ConceptToConceptCreate) -> ConceptToConceptRead:
        return await self.c_to_c_repo.add(junction=junction)

    async def bulk_create_concept_junctions(self, junctions: List[ConceptToConceptCreate]) -> List[ConceptToConceptRead]:
        return await self.c_to_c_repo.bulk_add(junctions=junctions)
    
    async def get_concept_junctions(self, concepts: List[ConceptRead], junction_direction: Literal["up", "down", "both"]="down") -> List[ConceptToConceptRead]:
        return await self.c_to_c_repo.get_some(concepts=concepts, junction_direction=junction_direction)

    async def delete_junctions(self, junctions: List[ConceptToConceptDelete]):
        await self.c_to_c_repo.delete(junctions=junctions)

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
        return await self.c_to_c_repo.update_one(
            junction=junction, updated_junction=updated_junction
        )
