""" This file stores the protocols used for the Personalization Service."""
from typing import Union, Dict, List, Optional

from pydantic import BaseModel, Field
from loguru import logger


class KnowledgeStateParameters(BaseModel):
    """
    This  class stores the format followed for the knowledge state parameters.
    """
    concept_list: List = Field(...)
    student_knowledge_state: Dict = Field(...)
    sme_concept_wise_importance: Dict = Field(default={})
    sme_opinion_importance_factor: float = Field(default=0.0, ge=0.0, le=1.0)

    # TODO: Check with team if it is over-engineering to provide it as a field.
    # A default value to assign as understanding of a completely new concept(i.e. there is no DB
    # entry for it). The value should lie between [0, 1].
    # Note:
    #    A value like 0.5 is used as it sits in the middle of the scale and as the student's
    #    understanding rating is not available, I believe we do not have much of an option here.
    #
    #    I can see this default value promoting a strategy of prioritizing testing of new
    #    concepts over personalization to a certain degree. We should keep this in mind.
    default_filler: Optional[float] = Field(default=0.5)

    @property
    def combined_knowledge_state(self) -> Dict:
        """ This field combines the SMEs input on concepts and Student's Knowledge state in a
        weighted manner.

        Notes:
            - There is a possibility of getting 'sme_opinion_importance_factor' as 0.0 or
            'sme_concept_wise_importance' is empty.
                In this case, the SME input should not be processed.
            - There is a possibility that a student might be encountering a concept for the first
            time which would mean there is no DB entry for it.
                In this case, we need a default value to assign to it.

        Returns:
            Dict containing the weighted average mean of the student state and the SME's input.
        """
        output = {}

        # Convert the student's concept-understanding score mapping into concept weights.
        # Currently, a weight is defined as 1 - understanding score because higher understanding
        # score indicates higher level of mastery. An addition of 1e-4 is made to this weight to
        # make sure it is never 0.
        for concept in self.concept_list:
            logger.debug(self.student_knowledge_state.get(
                concept, self.default_filler))
            output[concept] = 1 - self.student_knowledge_state.get(
                concept, self.default_filler
            ) + 1e-4

        if self.sme_opinion_importance_factor == 0.0 or not self.sme_concept_wise_importance:
            logger.debug("SME's opinion is skipped.")
            return output

        # Here, we take the weighted average between the 'sme_concept_wise_importance' and
        # concept weights gained in the previous step(stored in output).
        # This is done using the 'sme_opinion_importance_factor' as the relative weight.
        for concept in self.concept_list:
            output[concept] = (output[concept] * (1 - self.sme_opinion_importance_factor)) + (
                self.sme_concept_wise_importance.get(
                    concept, self.default_filler
                ) * self.sme_opinion_importance_factor
            )

        return output
