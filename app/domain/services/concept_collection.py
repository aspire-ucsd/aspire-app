from typing import List, Union, Optional, Dict

from fastapi import Depends, UploadFile

from app.domain.models.forms import ModuleForm

from app.domain.protocols.repositories.concept_collection import CollectionRepository as CollectionRepoProtocol
from app.domain.protocols.services.concept_collection import CollectionService as CollectionServiceProtocol
from app.infrastructure.database.repositories.concept_collection import CollectionRepository
from app.domain.models.concept_collection import CollectionCreate, CollectionRead, CollectionUpdate, CollectionCreateExtended

from app.domain.models.concept import ConceptRead, ConceptToCollectionCreate
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol, ConceptToModuleService as CToMProtocol
from .concept import ConceptService

from app.domain.protocols.services.course import CourseService as CourseServiceProtocol
from app.domain.services.course import CourseService

from app.domain.models.llm_agent import Validator, ContingencyFunctions

from app.infrastructure.LLM.llm_agent import LLMAgent
from app.infrastructure.LLM.contingencies.general import check_is_not_json, check_dict_values_not_json
from app.infrastructure.LLM.contingencies.summarize import format_as_string
from app.infrastructure.LLM.contingencies.module_concepts import format_for_module_concepts, format_for_module_concepts_alone



class CollectionService(CollectionServiceProtocol):
    def __init__(
            self, 
            collection_repo: CollectionRepoProtocol = Depends(CollectionRepository), 
            concept_service: Union[ConceptServiceProtocol, CToMProtocol] = Depends(ConceptService),
            course_service: CourseServiceProtocol = Depends(CourseService)
    ):
        self.collection_repo = collection_repo
        self.concept_service = concept_service
        self.course_service = course_service

    async def generate_module_summary(
            self,
            model_name: str,
            form_data: ModuleForm,
            prompt: str,
            files: List[UploadFile]
    ) -> str:
        llm_agent = LLMAgent(content_files=files)
        
        validators = [Validator(order=1, function=check_is_not_json)]
        c_func = ContingencyFunctions(validators=validators, formatter=format_as_string)
        content_summary = await llm_agent.execute(action="summarize", contingency_functions=c_func, params = {
            "model_name": model_name,
            "prompt": prompt})

        return {
            "summary": content_summary
        }

    async def generate_module_concepts(
            self,
            model_name: str,
            form_data: ModuleForm, 
            prompt: str,
            files: List[UploadFile],
    ) -> List[str]:
        llm_agent = LLMAgent(content_files=files, course_id=form_data.course_id)
        
        # Generate concepts
        concept_validators = [
            Validator(order=1, function=check_is_not_json),
            Validator(order=2, function=check_dict_values_not_json)
        ]
        concept_contingency_functions = ContingencyFunctions(validators=concept_validators, formatter=format_for_module_concepts_alone)
        
        course = await self.course_service.get_one_course(course_id=form_data.course_id)
        
        llm_concept_result = await llm_agent.execute(
            action="module-concepts-alone", 
            contingency_functions=concept_contingency_functions, 
            params={"domain_id": course.domain_id, 
                    "subject": "comp-sci", 
                    "difficulty": 1, 
                    "model_name": model_name,
                    "prompt": prompt}
        )
        
        module_concepts = llm_concept_result

        return {
            "concepts": module_concepts
        }

    async def generate_module_prerequisites(
            self,
            module_id: int,
            model_name: str
    ) -> Dict[str, List[Dict[str, List[str]]]]:
        module = await self.get_collection(module_id)
        course = await self.course_service.get_one_course(course_id='module.course_id')
        
        module_concepts = await self.concept_service.get_module_concepts(module_id)
        
        llm_agent = LLMAgent(course_id=module.course_id)
        
        validators = [
            Validator(order=1, function=check_is_not_json),
            Validator(order=2, function=check_dict_values_not_json)
        ]
        # c_func = ContingencyFunctions(validators=validators, formatter=format_for_module_prerequisites)
        
        llm_result = await llm_agent.execute(
            action="module-prerequisites", 
            # contingency_functions=c_func, 
            params={
                "domain_id": course.domain_id,
                "subject": "comp-sci",
                "difficulty": 1,
                "model_name": model_name,
                "module_concepts": [concept.name for concept in module_concepts]
            }
        )
        
        prerequisites = llm_result[1]  # Assuming this is where prerequisites are in the result

        # Format prerequisites as a list of dictionaries
        formatted_prerequisites = [{"concept": concept, "prerequisites": prereqs} for concept, prereqs in prerequisites.items()]

        return {"prerequisites": formatted_prerequisites}
    

    async def create_collection(self, collection: CollectionCreateExtended) -> CollectionRead:
        result = await self.collection_repo.add(collection=collection)

        return result
    
        
    async def get_collection(self, collection_id: int) -> CollectionRead:
        return await self.collection_repo.get_one(collection_id=collection_id)
    

    async def get_course_collections(self, course_id: int, id_only:int=False) -> List[CollectionRead]:
        return await self.collection_repo.get_all(filter_name="course", filter_id=course_id, id_only=id_only)


    async def get_all_collections(self) -> List[CollectionRead]:
        return await self.collection_repo.get_all(filter_name="all")
    

    async def update_collection(self, collection_id: int, collection_update: CollectionUpdate) -> CollectionRead:
        return await self.collection_repo.update(collection_id=collection_id, collection_update=collection_update)

    async def delete_collection_from_course(self, collection_id: int, course_id: int) -> None:
        return await self.collection_repo.delete_from_course(collection_id=collection_id, course_id=course_id)