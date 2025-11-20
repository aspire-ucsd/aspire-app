from distutils import errors
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, validator


class ErrorListMessage(BaseModel):
    message: str
    class Config:
        extra = 'allow'
    
class ErrorResponse(BaseModel):
    code: Optional[int] = None
    type: str
    message: Optional[str] = None
    errors: Optional[List[ErrorListMessage]] = None
    
    @validator('errors', pre=True, always=True)
    def require_messge_or_errors(cls, v, values):
        ''' 
        Check to ensure either message or errors is set.
        
        V has the value of errors and values has all the fields validated before errors.
        '''
        if 'message' not in values and not v:
            raise ValueError('Either message or errors is required.')
        return v
    
    @validator('message')
    def pretty_errors(cls, value):
        return value.replace('\n', "")


check_type_options = Literal["VALUE", "COLUMN", "TABLE"]
response_type_options = Literal["DOES NOT EXIST"]

class ValidationError(BaseModel):
    check_type: check_type_options
    response_type: response_type_options
    target: str
    value: Union[str, int]

    def raise_value_error(self):
        print("test")
        raise ValueError(f"{self.check_type}: {self.value} {self.response_type} at target: {self.target}")


class DBError(BaseModel):
    cause: str
    object_id: Union[str, int]

class APIMFault(BaseModel):
    code: int
    message: str
    description: str

class APIMErrorResponse(BaseModel):
    fault: APIMFault
