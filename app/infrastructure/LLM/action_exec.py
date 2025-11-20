import os
import fitz
import shutil
import json
import httpx
from typing import Optional, List, Union, Dict
from fastapi import UploadFile, Depends
import logging
from sqlmodel import select

from app.infrastructure.database.db import get_db
from app.infrastructure.decorators.register import Register
from app.domain.models.llm_agent import ContextCollection
from app.domain.models.errors import ErrorResponse
from app.domain.protocols.services.concept import ConceptService as ConceptServiceProtocol
from app.domain.services.concept import ConceptService
from app.domain.models.prompt import Prompt

from langchain_community.chat_models.openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

register = Register()

class ActionExecutor:

    def __init__(self):
        self.prompts = {}
        self.db = get_db()

    def fetch_prompts(self):
        """
        Fetches the prompts from the database and stores them in a dictionary.
        """
        prompts_list = self.db.exec(select(Prompt)).all()
        self.prompts = {prompt.id: {"editable_part": prompt.editable_part, "fixed_part": prompt.fixed_part} for prompt in prompts_list}
        logging.debug(f"Fetched prompts: {self.prompts}")

    def get_prompt_by_id(self, prompt_id: str) -> dict:
        """
        Retrieves a prompt by its ID.
        Inputs:
            prompt_id (str): The ID of the prompt to retrieve.
        Output:
            dict: The prompt dictionary containing editable_part and fixed_part.
        """
        return self.prompts.get(prompt_id, "")

    async def executePrompt(self, context_prompt, action_prompt, model_name):
        """
        Executes the prompt using the specified model.

        Inputs:
            context_prompt (str): The context prompt.
            action_prompt (str): The action prompt.
            model_name (str): The name of the model to be used.

        Output:
            str: The result from the model.
        """
        base_prompt = self.get_prompt_by_id("base-prompt")
        base_prompt = base_prompt["editable_part"] + base_prompt["fixed_part"] + " json"

        if 'gpt' in model_name:
            chain_gpt = ChatOpenAI(model=model_name, openai_api_key=os.getenv("OPENAI_API_KEY"), model_kwargs={"response_format": {"type": "json_object"}})
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "assistant", "content": context_prompt},
                {"role": "user", "content": action_prompt}
            ]
            result = await chain_gpt.ainvoke(messages)
            return result.content

        elif 'gemini' in model_name:    
            chain_gemini = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))
            messages=[
                HumanMessage(content=f"{action_prompt}+ Please perform the action based on the base prompt: {base_prompt}+ context_prompt{context_prompt}")
            ]
            result = await chain_gemini.ainvoke(messages)
            res = result.content
            start_index = res.find('{')
            end_index = res.rfind('}')
            res = res[start_index:end_index+1]
            return res.strip()

        elif 'llama' in model_name:
            url = "https://traip13.dsmlp.ucsd.edu/v1/chat/completions"
            api_key = os.getenv('TRITON_API_KEY')
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": context_prompt + "\n" + action_prompt}
                ],
                "model": "llama-3",
                "max_tokens": 768,
                "stream": False,
                "n": 1,
                "temperature": 0.2,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        else:
            raise ValueError("Unsupported AI provider")
        
    @register.add(action="summarize")
    async def summarize_contents(self, context:Union[ContextCollection, ErrorResponse], params = Dict):
        """
        Generates a summary of the teaching materials provided in the context.
        Inputs:
            context (ContextCollection): Contains the base prompt and file contents.
            params (dict, optional): Additional parameters (not currently used).
        Output:
            str: JSON-formatted summary of the teaching materials.
        """
        if isinstance(context, ErrorResponse):
            print(f"Error: {context}")
            return
        model_name = params.get('model_name')
        summarize_prompt = self.get_prompt_by_id("summarize")
        context_prompt = f"The following is context related to the course being taught. These are the materials being taught: {context.file_contents}"      
        action_prompt = ( params.get('prompt') or '')+ summarize_prompt["fixed_part"]
        print("The action prompt is: ", action_prompt)
        result = await self.executePrompt(context_prompt, action_prompt, model_name)
        built_prompt = f"{context_prompt}\n{action_prompt}"
        print(built_prompt)
        return built_prompt, result

    @register.add(action="domain-concepts")
    async def domain_concepts(self, context:Union[ContextCollection, ErrorResponse], params = Dict):
        """
        Identifies and lists domain concepts from the provided teaching materials and existing database concepts.
        Inputs:
            context (ContextCollection): Includes the base prompt, file contents, and context concepts.
            params (dict, optional): Additional parameters (not currently used).
        Output:
            str: JSON-formatted list of identified domain concepts from the teaching materials.
        """
        if isinstance(context, ErrorResponse):
            print(f"Error: {context}")
            return
        model_name = params.get('model_name')
        createconcepts_prompt = self.get_prompt_by_id("create-concepts")
        context_prompt = f"The following is context related to the course being taught. These are the materials being taught: {context.file_contents}, These are the concepts in the database already: {context.context_concepts}" 
        action_prompt = createconcepts_prompt["editable_part"] + createconcepts_prompt["fixed_part"]
        result = await self.executePrompt(context_prompt, action_prompt, model_name)
        built_prompt = f"{context_prompt}\n{action_prompt}"
        print(built_prompt)
        return built_prompt, result
    
    @register.add(action="module-concepts-alone")
    async def generate_module_concepts(self, context: Union[ContextCollection, ErrorResponse], params: Dict) -> Union[str, ErrorResponse]:
        """
        Extracts module concepts from the teaching materials.
        Inputs:
            context (ContextCollection): Includes the base prompt, file contents, and context concepts.
            params (dict): Parameters including 'model_name'.
        Output:
            str: JSON string of the module concepts for verification.
        """
        if isinstance(context, ErrorResponse):
            print(f"Error: {context}")
            return context
        
        model_name = params.get('model_name')
        moduleconcepts = self.get_prompt_by_id("create-concepts")
        context_prompt = f"The following is context related to the course being taught. These are the materials being taught: {context.file_contents}, These are the concepts in the database already: {context.context_concepts}" 
        action_prompt = params.get('prompt') + moduleconcepts["fixed_part"]
        
        module_concepts = await self.executePrompt(context_prompt, action_prompt, model_name)
        
        try:
            module_concepts_dict = json.loads(module_concepts)
        except Exception as e:
            print(e)
            return ErrorResponse(code=404, type="ValidationError", message="The module concepts were not returned in the proper format.")
        
        built_prompt = f"{context_prompt}\n{action_prompt}"
        print(built_prompt)
        return built_prompt, module_concepts

    @register.add(action="module-concepts")
    async def module_concepts(self, context:Union[ContextCollection, ErrorResponse], params = Dict):
        """
        Extracts module concepts from the teaching materials, compares them with existing database concepts, and handles potential format errors.
        Inputs:
            context (ContextCollection): Includes the base prompt, file contents, and context concepts.
            params (dict, optional): Additional parameters (not currently used).
        Output:
            tuple: Contains prerequisites for the identified module concepts and the module concepts themselves, both typically in JSON format. Also handles and returns errors if the concepts are not in the proper format.
        """
        if isinstance(context, ErrorResponse):
            print(f"Error: {context}")
            return
        model_name = params.get('model_name')
        moduleconcepts = self.get_prompt_by_id("create-concepts")
        context_prompt = f"The following is context related to the course being taught. These are the materials being taught: {context.file_contents}, These are the concepts in the database already: {context.context_concepts}" 
        action_prompt = moduleconcepts["editable_part"] + moduleconcepts["fixed_part"]   
        module_concepts = await self.executePrompt(context_prompt, action_prompt, model_name)
        try:
            module_concepts_dict = json.loads(module_concepts)
        except Exception as e:
            print(e)
            return ErrorResponse(code=404, type="ValidationError", message="The module concepts were not returned in the proper format.")
        if context.context_concepts is None:
            context.context_concepts = []
        context.context_concepts.append(module_concepts_dict)
        if context.focus_concepts is None:
            context.focus_concepts = []
        context.focus_concepts.append(module_concepts_dict) 
        context_prompt = context_prompt + f"The following are the concepts that we are focusing on: {context.focus_concepts}"
        createprereqs_prompt = self.get_prompt_by_id("create-prereqs")
        action_prompt = createprereqs_prompt["editable_part"] + createprereqs_prompt["fixed_part"]
        prereq_concepts = await self.executePrompt(context_prompt, action_prompt, model_name)
        concepts = {
            'prereq_concepts': prereq_concepts,
            'module_concepts': module_concepts
        }
        built_prompt = f"{context_prompt}\n{action_prompt}"
        print(built_prompt)
        return built_prompt, concepts

    @register.add(action="questions")
    async def quiz_questions(self, context:Union[ContextCollection, ErrorResponse], params: dict):
        """
        Generates quiz questions based on the focus concepts provided in the context.
        Inputs:
            context (ContextCollection): Includes the base prompt and focus concepts.
            params (dict, optional): Additional parameters (not currently used).
        Output:
            str: List of quiz questions for each focus concept, usually in a text format.
        """
        if isinstance(context, ErrorResponse):
            print(f"Error: {context}")
            return
        model_name = params.get('model_name')
        quiz_type = params.get('quiz_type')
        prereq_question_prompt = self.get_prompt_by_id("prereq-questions")
        preview_question_prompt = self.get_prompt_by_id("preview-questions")
        review_question_prompt = self.get_prompt_by_id("review-questions")
        print(model_name)
        context_prompt = f"The following is context related to the action you will be asked to take.These are the concepts that we are focusing on: {context.focus_concepts}"
        if quiz_type == "prereq":
            action_prompt = f"Please generate {params.get('num_questions')} questions based on the focus concepts provided." + params.get('prompt') + prereq_question_prompt["fixed_part"]
        elif quiz_type == "preview":
            action_prompt = f"Please generate {params.get('num_questions')} questions based on the focus concepts provided." + params.get('prompt') + preview_question_prompt["fixed_part"]
        elif quiz_type == "review":
            action_prompt = f"Please generate {params.get('num_questions')} questions based on the focus concepts provided." + params.get('prompt') + review_question_prompt["fixed_part"]    
        else:
            print("Invalid quiz type")
        result = await self.executePrompt(context_prompt, action_prompt, model_name)
        built_prompt = f"{context_prompt}\n{action_prompt}"
        print(built_prompt)
        return built_prompt, result

    async def execute(self, context: Union[ContextCollection, ErrorResponse], action: str, params: Optional[Dict]=None):
        """
        Dispatches the request to the appropriate function based on the action parameter.
        Inputs:
            action (str): Action name to identify the function to be executed.
            params (dict, optional): Parameters for the action function.
        Output:
            any: Result of the function execution, varies based on the action.
        """
        self.fetch_prompts()
        return await register.registered_fn[action](self=self, context=context, params=params)
