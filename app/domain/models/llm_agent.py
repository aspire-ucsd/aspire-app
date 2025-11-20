from pydantic import BaseModel
from typing import Union, List, Optional, Literal, Any, Callable
from ...infrastructure.LLM.prompts import generateRolePrompt

class ContextCollection(BaseModel):
    file_contents: Optional[List[Union[bytes, str]]] = None
    context_concepts: Optional[List[str]] = None
    focus_concepts: Optional[List[str]] = None
    base_prompt: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.base_prompt = generateRolePrompt()

    # @validator(pre=True)
    # @classmethod
    # def one_req(cls, v):
    #     if not any(v.values()):
    #         raise ValueError("At least one field must have a value")
    #     return v

action_options = Literal["summarize", "domain-concepts", "module-concepts", "questions"]


class Validator(BaseModel):
    order: int
    error_response: Optional[str] = None
    status: str = "FAIL"
    function: Callable

    def __str__(self):
        return f"Validator #{self.order}: {self.function.__name__} | Error: {self.error_response}"

class ContingencyFunctions(BaseModel):
    validators: List[Validator]
    formatter: Callable