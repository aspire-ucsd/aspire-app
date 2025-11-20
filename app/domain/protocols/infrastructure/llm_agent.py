from typing import Optional, Protocol, List, Dict, Union
from app.domain.models.llm_agent import ContextCollection, action_options, ContingencyFunctions
from fastapi import UploadFile, Depends


class LLMAgent(Protocol):
    """
    Contains the single point of access for LLM calls made by the API: LLMAgent.execute() as well as the ContingencySystem for validating and formatting LLM responses.

    All init parameters are marked as optional, but varying combinations are required dependent on the action being executed. See .Docs/LLM_AGENT.md for documentation of these action specific requirements. 
    """
    def process_files(self, content_files) -> Union[List[str], None]:
        ...

    async def runContingencies(
        self, 
        response: str ,
        prompt: str, 
        action: action_options, 
        contingency_functions: ContingencyFunctions,
        params: Dict, 
        add_cycles: int
    ):
        """
        A Contingency System for validating and reformating the output of the LLM using a dictionary of callback functions called "Contingency Functions". 

        The system Operates in two stages: 
        - First it iterates over 'validator' functions to verify some aspect of the llm response and returns a PASS/FAIL status and a response which is passed to subsequent contingency functions.
        - Finally it runs a 'formatter' function which uses the result of the validation loop to either return the LLM response in its final data structure or an ErrorResponse.

        Contingency Functions are grouped into two types: 
            - Validators - Callback functions ran within the Validation Loop in ascending order to validate and preprocess the LLM response. 
            - Formatter -  Callback fucking executed after the Validation Loop, returns the final response.

        
        :param response: The string response of the LLM
        :param prompt: The prompt used to generate the LLM Response
        :param action: The action which the LLM Agent performed
        :param contingency_functions: A ContingencyFunctions object containing the 'validator' and 'formatter' functions being executed.
        :param params: A dictionary of optional parameters used to pass any extra data to functions
        :param add_cycles: An integer which increases the number of validation loops the contingency system will run. Always runs at least two loops, any integer passed adds extra loops.

        
        ---
        Validation Loop
        ---

        The system first iterates over all 'Validation' functions, these functions are iterated over at least twice. 
        All functions start out marked as "FAIL" and the loop always executes every failed 'Validator' function in ascending order,
        if a function passes its marked as a "PASS" and will not be reran in future loops. 
        The response output of every 'validator' function is reassigned to the response variable passed into subsequent functions, propagating any mutations made to the response. 

        
        ---
        Validator Functions:
        ---

        'Validator' functions check and/or modify some aspect of the LLM Response. 
        These functions must always accept the arguments: (self, response, prompt, action, params) 
        and must always return a status in the form of 'PASS'/'FAIL' and a response that will be passed to subsequent contingency functions
        

        Validator Function E.g.::

            async def check_is_json(self, response, prompt, action, params):
                try:
                    dict_response = json.loads(response)
                    return "PASS", dict_response
                except Exception as e:
                    return "FAIL", response
                 
        ---
        Formatter Function:
        ---

        After the 'validator' loop has completed, the 'formatter' function is executed and accepts the Validation Loop response 
        and a dictionary describing which validator functions passed and failed. 
        This function must either return the final response in the required format or an error response.

        Formatting Function E.g.::

            async def format_as_concept_create(response, validator_status):
                try:
                    final_response = [ConceptCreate(**val) for val in response]
                    return final_response
                except Exception as e:
                    return ErrorResponse(
                        code=500, 
                        type=f"LLM Validation Error(s)", 
                        message="Unable to process response from LLM. FAILED VALIDATOR(s):{validator_status.keys()}"
                        )
        """  
        ...

    async def add_param(
        self, 
        course_id: Optional[int]=None,
        module_id: Optional[int]=None,
        content_files: Optional[List[UploadFile]]=None,  
    ) -> None:
        ...
        
    async def execute(
        self,
        action: action_options,
        contingency_functions:ContingencyFunctions,
        params: Optional[dict]=None,
        add_cycles:int=0,
    ):
        """
        Executes the specified action and returns the final formatted response originating from the LLM. 
        Three stages of operation:
            - Executes ContextConstructor.construct() to gather the required contextual information as a standard context object using the initialized parameters and specified action.
            - Executes ActionExecutor.execute() to construct the final prompt and send it to an LLM.
            - Executes self.runContingencies() to validate, format and ultimately return the LLM response in the desired format.
        """
        ...