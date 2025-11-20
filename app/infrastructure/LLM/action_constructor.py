import os
import fitz
import shutil 

from typing import Optional, List, Union, Dict
from fastapi import UploadFile, Depends

from app.infrastructure.decorators.register import Register
from app.domain.models.llm_agent import ContextCollection
from app.domain.models.errors import ErrorResponse
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol
from app.domain.services.concept import ConceptService


register = Register()


class ActionConstructor:
    def __init__(
            self, 
            course_id: Optional[int], 
            module_id: Optional[int], 
            content_files: Optional[List[UploadFile]],
            concept_repo: ConceptServiceProtocol = Depends(ConceptService)
            ):
        self.course_id = course_id
        self.module_id = module_id
        self.content_list = self.process_files(content_files=content_files)
        self.concept_repo = concept_repo

    def process_files(self, content_files) -> Union[List[str], None]:
        """
        Process PDF files in content_files, extracting text and storing it in processed_text.
        Each call to this method resets and repopulates processed_text with new content.
        """
        # Initialize or reset processed_text each time the method is called
        content = []

        if not content_files:
            print("No files to process.")
            return None

        for file in content_files:
            if file.filename.endswith('.pdf'):
                # Save the temporary file to disk to open it with fitz
                temp_file_path = f"temp_{file.filename}"
                with open(temp_file_path, 'wb') as out_file:
                    shutil.copyfileobj(file.file, out_file)
                
                # Open the PDF and extract text
                doc = fitz.open(temp_file_path)
                text = ''
                for page in doc:
                    text += page.get_text("text")
                content.append(text)
                
                # Close the document and remove the temporary file
                doc.close()
                os.remove(temp_file_path)
        return content
    

    @register.add(action="summarize")
    async def summarize_contents(self) -> Union[ContextCollection, ErrorResponse]:
        if not self.content_list:
            message = f"METHOD: .summarize_contents() missing required argument(s): content_files"
            return ErrorResponse(code=404, type="ValidationError", message=message)


    @register.add(action="domain-concepts")
    async def domain_concepts(self, params=None) -> Union[ContextCollection, ErrorResponse]:
        if not self.content_list or self.course_id:
            message = f"METHOD: .domain_concepts() missing required argument(s): {'course_id' if not self.content_list else ''} {'content_files' if not self.content_list else ''}"
            return ErrorResponse(code=404, type="ValidationError", message=message)

        concepts = await self.concept_repo.get_domain_init_concepts(course_id=self.course_id)
        print(concepts)

    @register.add(action="module-concepts")
    async def module_concepts(self, params=None) -> Union[ContextCollection, ErrorResponse]:
        if not self.content_list or self.course_id:
            message = f"METHOD: .module_concepts() missing required argument(s): {'course_id' if not self.content_list else ''} {'content_files' if not self.content_list else ''}"
            return ErrorResponse(code=404, type="ValidationError", message=message)


    @register.add(action="questions")
    async def quiz_questions(self, params: dict) -> Union[ContextCollection, ErrorResponse]:
        if not self.module_id or params.get("quiz_type"):
            message = f"METHOD: .quiz_questions() missing required argument(s): {'module_id' if not self.module_id else ''} {'params (quiz_type)' if not params.get('quiz_type') else ''}"
            return ErrorResponse(code=404, type="ValidationError", message=message)


    async def construct(self, action: str, params: Optional[Dict]=None) -> Union[ContextCollection, ErrorResponse]:
        print("fired")
        return await register.registered_fn[action](self=self, params=params)