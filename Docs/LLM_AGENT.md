# Table of Contents

- **[Overview](#overview)**
- **[LLMAgent](#llm-agent)** 
    - [.execute()](#llmagentexecute)
    - [Actions, Init Params, & Arg Params](#actions-initialization-params-argument-params)
- **[The Contingency System](#the-contingency-system)**
    - [Operation](#operation)
    - [Contingency Functions](#contingency-functions)
    - [Validation Loop](#validation-loop)
    - [Data Formatting](#data-formatting)
- **[ContextConstructor](#contextconstructor)** 
    - [.construct()](#construct)
    - [Method Registration](#method-registration)
- **[ActionExecutor](#actionexecutor)** 
    - [.execute()](#execute)
    - [Method Registration](#method-registration)
   


## Overview

The LLM Agent and support systems acts as the single point of access for all LLM calls made by the API via the LLMAgent.execute() method. This system handles the gathering of context from the DB, construction and execution of prompts via the LLM, and the validation and formatting of the LLM response. 

The system is broken down into three parts: The LLM Agent, the Context Constructor, and the Action Executor.

The LLM Agent manages the initialization and distribution of required data to, and the execution of, the Context Constructor and Action Executor, as well as containing the Contingency System for validating and reformating LLM responses.


## LLM Agent
To use the LLMAgent within the API requires only that the class be initialized with the parameters required for the specified action and that .execute() is called and awaited with an action, ContingencyFunctions object, and any required parameters passed.

.execute() returns either an LLM Response matching the specified action and formatted as specified by the formatter function passed in with the contingency functions, or an instance of the ErrorResponse model. 

E.g:
```python
from ... import LLMAgent
# Contingency Function pydantic model
from ... import ContingencyFunctions, Validator
# sample contingency functions
from ... import convert_to_dict, check_has_answer, convert_to_model
# sample output model
from ... import ConceptCreate


def summarize_contents(files):
    llm_agent = LLMAgent(content_files=files)
    contingency_functions = ContingencyFunctions(
        validators=[
            Validator(
                order=1, 
                error_response="Unprocessable String", 
                function=convert_to_dict
                ),
                Validator(
                order=2, 
                error_response="Missing Key: answer", 
                function=check_has_answer
                ),
            ],
        # formatter requires a model to be passed as a param
        formatter=convert_to_model
        ),

    summary = await LLMAgent.execute(
        action="questions", 
        contingency_functions=contingency_functions,
        # The 'questions' action also requires a param: "quiz_type"
        params={"model_format": ConceptCreate, "quiz_type": "prereq"}
        ) 

    return summary
```


### LLMAgent.execute()

| arg | type |is required? | application |
| --- | ---- |------------ | ----------- |
| action | String | True | Specifies the context and action added to the prompt and sent to the LLM |
| contingency_functions | ContingencyFunctions obj | True | Validates and formats the LLM response |
| params | Dictionary | True/False | Params are specific to action/contingency functions and only required if the desired action or contingency function(s) require them. Acts as additional metadata |
| add_cycles | Integer | False | Adds to the maximum number of cycles the Validation Loop can run, Always runs no less than 2 cycles |  


### Actions, Initialization Params, Argument Params

The required initialization parameters for the LLMAgent class and argument parameters passed to LLMAgent.execute() are action and contingency function dependant. Not every init or arg parameter is required for every action, the table below shows the minimum amount of data required for each action.

| Action | Init Params | Arg Params |
| ------ | ----------- | ---------- |
| summarize | file_contents | None* |
| domain-concepts | file_contents, course_id | None* |
| module-concepts | file_contents, course_id | None* |
| questions | module_id | {"quiz_type": "prereq" or "preview" or "review"} |

*Table only specifies the required Arg Params for the LLMAgent and subsystems, add any additional params needed by your contingency functions.

## The Contingency System

### Operation

The Contingency System operates in 2 stages: First it executes all supplied contingency functions in a 

### Contingency Functions

### Validation Loop

### Data Formatting

## ContextConstructor 

### .construct()

### Method Registration

## ActionExecutor 

### .execute()

### Method Registration