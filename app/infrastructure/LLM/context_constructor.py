
from typing import Optional, List, Union, Dict

from app.infrastructure.decorators.register import Register
from app.domain.models.llm_agent import ContextCollection

from app.app.errors.validation_error import ValidationError

from app.domain.protocols.repositories.concept import (
    ConceptRepository as ConceptRepositoryProtocol, 
    ConceptToModuleRepository as CToMRepoProtocol,
    ConceptToConceptRepository as CToCRepoProtocol
    )

from app.domain.models.concept import ConceptFilter

from app.domain.protocols.repositories.course import CourseRepository as CourseRepoProtocol
from app.infrastructure.database.repositories.concept import ConceptRepository, ConceptToModuleRepository, ConceptToConceptRepository

from app.infrastructure.database.repositories.course import CourseRepository



register = Register()


class ContextConstructor:
    def __init__(
            self, 
            course_id: Optional[int] = None, 
            module_id: Optional[int] = None, 
            content_files: Optional[List[Union[bytes, str]]] = None
    ):
        self.course_id = course_id
        self.module_id = module_id
        self.file_contents = content_files
        self.concept_repo: ConceptRepositoryProtocol = ConceptRepository()
        self.c_to_m_repo: CToMRepoProtocol = ConceptToModuleRepository()
        self.c_to_c_repo: CToCRepoProtocol = ConceptToConceptRepository()
        self.course_repo: CourseRepoProtocol = CourseRepository()
    

    @register.add(action="summarize")
    async def summarize_contents(self, params=None) -> ContextCollection:
        if not self.file_contents:
            message = f"METHOD: .summarize_contents() missing required argument(s): content_files"
            raise ValidationError(origin="ContextConstructor", status_code=400, message=message)

        return ContextCollection(file_contents=self.file_contents)


    @register.add(action="module-concepts-alone")
    async def module_concepts(self, params=None) -> ContextCollection:
        if not self.file_contents or not self.course_id:
            message = f"METHOD: .module_concepts() missing required argument(s): {'course_id' if not self.course_id else ''} {'content_files' if not self.file_contents else ''}"
            raise ValidationError(origin="ContextConstructor", status_code=400, message=message)
        #TODO: error handling for when course_id invalid/get_one_course() fails
        course_data = await self.course_repo.get_one(course_id=self.course_id, read_mode="verbose")


        concepts_obj = await self.concept_repo.get_many(filters=ConceptFilter(subject=course_data.subject, difficulty=course_data.difficulty))
        concepts = [val.name for val in concepts_obj.concepts]

        return ContextCollection(file_contents=self.file_contents, context_concepts=concepts)


    @register.add(action="module-concepts")
    async def module_concepts(self, params=None) -> ContextCollection:
        if not self.file_contents or not self.course_id:
            message = f"METHOD: .module_concepts() missing required argument(s): {'course_id' if not self.course_id else ''} {'content_files' if not self.file_contents else ''}"
            raise ValidationError(origin="ContextConstructor", status_code=400, message=message)
        #TODO: error handling for when course_id invalid/get_one_course() fails
        course_data = await self.course_repo.get_one(course_id=self.course_id)

        concepts_obj = await self.concept_repo.get_many(filters=ConceptFilter(subject=course_data.subject, difficulty=course_data.difficulty))
        concepts = [val.name for val in concepts_obj.concepts]

        return ContextCollection(file_contents=self.file_contents, context_concepts=concepts)


    @register.add(action="questions")
    async def quiz_questions(self, params: dict) -> ContextCollection:
        if not self.module_id or not params.get("quiz_type"):
            message = f"METHOD: .quiz_questions() missing required argument(s): {'module_id' if not self.module_id else ''} {'params (quiz_type)' if not params.get('quiz_type') else ''}"
            raise ValidationError(origin="ContextConstructor", status_code=400, message=message)

        if params.get("quiz_type") == "prereq":
            #TODO: error handling for when module_id invalid/get_all_module_prereqs() fails
            module_concepts = await self.c_to_m_repo.get_all(module_id=self.module_id)
            concept_junctions = await self.c_to_c_repo.get_some(concepts=module_concepts)

            module_concept_list = [val.name for val in module_concepts.concepts]
            prereq_list = list(set([val.prereq_name for val in concept_junctions]))

            concepts = [val for val in prereq_list if val not in module_concept_list]

        else:
            #TODO: error handling for when module_id invalid/get_all_concepts_in_module() fails
            concepts_obj = await self.c_to_m_repo.get_all(module_id=self.module_id)
            concepts = [val.name for val in concepts_obj.concepts]

        if not concepts:
            raise ValidationError(origin="ContextConstructor", status_code=400, message="Error: Module has no Prereqs")
        
        return ContextCollection(focus_concepts=concepts)


    async def construct(self, action: str, params: Optional[Dict]={}) -> ContextCollection:
        return await register.registered_fn[action](self=self, params=params)