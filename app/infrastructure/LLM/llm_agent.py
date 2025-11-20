from typing import List, Optional, Dict, Union
from fastapi import UploadFile
import os
from dotenv import load_dotenv
import fitz  # Import PyMuPDF
import shutil 

from app.app.errors.file_process_error import FileProcessError

from app.domain.models.llm_agent import action_options, ContingencyFunctions
from app.domain.protocols.infrastructure.llm_agent import LLMAgent as LLMAgentProtocol
from app.domain.models.errors import ErrorResponse

from .action_exec import ActionExecutor
from .context_constructor import ContextConstructor
load_dotenv()




class LLMAgent(LLMAgentProtocol):
    def __init__(
            self, 
            content_files: Optional[List[UploadFile]] = None,
            course_id: Optional[int] = None, 
            module_id: Optional[int] = None, 
    ):
        # Check if all inputs are None or if content_files is an empty list
        if not course_id and not module_id and not content_files:
            print("Error: At least one input must be non-empty.")
            return

        self.course_id = course_id
        self.module_id = module_id
        self.content_files = self.process_files(content_files)
        self.context_constructor = ContextConstructor(content_files=self.content_files, course_id=self.course_id, module_id=self.module_id)
        self.action_executor = ActionExecutor()


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
            try:
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
            except Exception as e:
                raise FileProcessError(message=str(e), file=file)
        return content


    async def add_param(
            self, 
            course_id: Optional[int]=None,
            module_id: Optional[int] = None,
            content_files: Optional[List[UploadFile]] = None,  
        ) -> None:
        self.course_id = course_id if course_id else self.course_id
        self.module_id = module_id if module_id else self.module_id
        self.content_files = self.process_files(content_files=content_files) if content_files else self.content_files

        self.context_constructor = ContextConstructor(
            content_files=self.content_files, 
            course_id=self.course_id, 
            module_id=self.module_id
            )


    async def runContingencies(
        self, 
        response: str, 
        prompt: str, 
        action: action_options, 
        contingency_functions: ContingencyFunctions,
        params: Dict, 
        add_cycles: int
        ):
        
        validation_response = response

        max_cycles = add_cycles + 2
        cycles = 0

        while cycles != max_cycles:
            # filter for only failed validators and sort by order
            sorted_validators = [validator for validator in contingency_functions.validators if validator.status == "FAIL"]
            sorted_validators.sort(key=lambda x: x.order)
            if not sorted_validators:
                cycles = max_cycles
                break
            else:
                for validator in sorted_validators:
                    status, new_response = await validator.function(
                        self=validator, 
                        response=validation_response,
                        validator_status=contingency_functions.validators, 
                        prompt=prompt, 
                        action=action, 
                        params=params
                        )
                    validator.status = status
                    validation_response = new_response

            cycles += 1

        return await contingency_functions.formatter(
            response=validation_response, 
            validator_status=contingency_functions.validators, 
            params=params
            )
                

    async def execute(
        self,
        action: action_options,
        contingency_functions:ContingencyFunctions,
        params: Optional[dict]=None,
        add_cycles:int=0
        ):
        
        context = await self.context_constructor.construct(action=action, params=params)
        prompt, response = await self.action_executor.execute(action=action, context=context, params=params)
        print("The prompt being sent is:", prompt)
        print("The response being sent is:", response)
        response = await self.runContingencies(
            response=response, 
            prompt=prompt, 
            action=action, 
            contingency_functions=contingency_functions, 
            params=params,
            add_cycles=add_cycles
            )
        
        print(response)
        return response
