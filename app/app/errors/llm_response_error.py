class LLMResponseError(Exception):
    def __init__(
            self, 
            message: str, 
            action: str, 
            status_code: int, 
            llm_response, 
            failed_validators
    ) -> None:
        
        self.message = message
        self.action = action
        self.llm_response = llm_response
        self.failed_validators = failed_validators
        self.status_code = status_code

    def __str__(self):
        return f"MESSAGE: {self.message}\nACTION: {self.action}\nLLM RESPONSE: {self.llm_response}\nFAILED VALIDATORS: {self.failed_validators}"