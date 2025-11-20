import logging

from app.app.errors.llm_response_error import LLMResponseError

logger = logging.getLogger(__name__)


async def format_as_string(response, validator_status, params):
    try:
        return response.get("summary")
    except Exception as e:
        logger.exception(msg="Failed to parse LLM response")
        raise LLMResponseError(
            message="Failed to parse LLM response.", 
            action="summarize",
            status_code=500, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL'], 
            llm_response=response
            )