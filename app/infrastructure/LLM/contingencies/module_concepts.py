import logging

from app.domain.models.concept import ConceptCreate, ConceptToConceptCreate
from app.app.errors.llm_response_error import LLMResponseError

logger = logging.getLogger(__name__)

async def format_for_module_concepts_alone(response, validator_status, params):
    try:
        concepts = response.get('concepts')
        return concepts
    
    except Exception as e:
        logger.exception(msg="Failed to parse LLM response")
        raise LLMResponseError(
            message="Failed to parse LLM response.", 
            action="module-concepts-alone",
            status_code=500, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL'], 
            llm_response=response
            )

async def format_for_module_concepts(response, validator_status, params):
    try:
        concepts = response.get('module_concepts').get("concepts")
        prereqs = response.get('prereq_concepts').get("prerequisites")
        print(f"\n\nprereqs before: {prereqs}\n\n")
        for key, val in prereqs.items():
            val.append(key)
            concepts.extend(val)

        llm_concepts = [
            ConceptCreate(
                name=val, 
                subject=params.get("subject"), 
                difficulty=params.get("difficulty"), 
                domain_id=params.get("domain_id")
            ) 
            for val in set(concepts)
        ]

        llm_junctions = []
        for concept_name, concept_list in prereqs.items():
            llm_junctions.extend([ConceptToConceptCreate(concept_name=concept_name, prereq_name=val) for val in concept_list])
        print(f"\n\nprereqs after: {prereqs}\n\n")
        return [llm_concepts, llm_junctions, concepts]
    
    except Exception as e:
        logger.exception(msg="Failed to parse LLM response")
        raise LLMResponseError(
            message="Failed to parse LLM response.", 
            action="module-concepts",
            status_code=500, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL'], 
            llm_response=response
            )