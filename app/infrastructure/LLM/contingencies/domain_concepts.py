import logging 

from app.domain.models.concept import ConceptCreate
from app.app.errors.llm_response_error import LLMResponseError

logger = logging.getLogger(__name__)

async def format_as_concept_create(response, validator_status, params):
    try:
        final_response = [
            ConceptCreate(
                name=val, 
                subject=params.get("subject"), 
                difficulty=params.get("difficulty"), 
                domain_id=params.get("domain_id")
            ) 
            for val in response.get("concepts")
        ]
        return final_response
    except Exception as e:
        logger.exception(msg="Failed to parse LLM response")
        raise LLMResponseError(
            message="Failed to parse LLM response.", 
            action="domain-concepts",
            status_code=500, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL'], 
            llm_response=response
            )
