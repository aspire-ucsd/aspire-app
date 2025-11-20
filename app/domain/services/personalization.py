""" This file contains the logic to personalize the quiz questions. """
from typing import Union, List, Dict

from loguru import logger
import numpy as np
import pandas as pd
from fastapi import Depends

from app.domain.protocols.services.concept import (
    ConceptService as ConceptServiceProtocol,
    ConceptToModuleService as CToMProtocol
)
from app.domain.services.concept import ConceptService
from app.domain.services.question import QuestionService

from app.domain.models.concept import ConceptBulkRead

from app.domain.protocols.services.question import QuestionService as QuestionServiceProtocol
from app.domain.models.question import Question

from app.domain.protocols.services.personalization import KnowledgeStateParameters


class QuestionPersonalizationService:
    """This class contains the code used to Personalized Questions Selection."""
    def __init__(
            self,
            knowledge_state: KnowledgeStateParameters,
            questions: List[Question]
    ):
        self.knowledge_state = knowledge_state
        self.questions = questions

    async def _prepare_concept_to_questions_mapping(self) -> Dict:
        """ This is a function that prepares the concept to question mapping.

        Returns:
            Mapping of concept to relevant questions
        """
        concept_to_questions_mapping = {}
        for question in self.questions:
            # question_name field in our database is equivalent to concept name.
            concept_to_questions_mapping[question.question_name] = concept_to_questions_mapping.get(
                question.question_name, []
            ) + [question]
        logger.debug(concept_to_questions_mapping)
        return concept_to_questions_mapping

    async def _get_formatted_concept_weights(self, concept_to_questions_mapping: Dict) -> Dict:
        """ This function formats the concept weights and presents them in a usable format.

        Returns:
            Mapping of concept to importance.
        """
        # We create a concept to importance mapping.
        # We additionally remove the concepts that we don't have any entries for in the DB.
        concept_weights = {}
        logger.debug(f"Combined Knowledge State: {self.knowledge_state.combined_knowledge_state}")
        for concept, weight in self.knowledge_state.combined_knowledge_state.items():
            if len(concept_to_questions_mapping.get(concept, [])) == 0:
                logger.debug(f'Concept removed: {concept} || Has no questions in DB.')
            else:
                concept_weights[concept] = weight

        return concept_weights

    @staticmethod
    async def _select_a_question_for_concept(
            questions: List
    ) -> [Dict, Question]:
        """ This is a private function that selects a single question given a concept.

        Notes:
            Customize the contents of this function to change the question selection mechanism.

        Args:
            questions: A set of questions to choose from.

        Returns:
            1. questions where the selected question is removed.
            2. Selected question.
        """
        # Currently, we randomly select a single question from the list.
        chosen_idx = np.random.choice(a=range(len(questions)), size=1)[0]

        selected_question = questions.pop(chosen_idx)

        return [questions, selected_question]

    async def get_personalized_questions(self, n_questions: int) -> List[Question]:
        """ This function conducts the selection of questions from the given list based on
        determined concept weights.

        Args:
            n_questions: No of questions to be selected from the given list.

        Returns:
            A list of personalized questions.
        """
        if n_questions > len(self.questions):
            raise ValueError("No of questions requested for quiz is more than the questions "
                             "present in the database.")

        concept_to_questions_mapping = await self._prepare_concept_to_questions_mapping()

        concept_weights = await self._get_formatted_concept_weights(concept_to_questions_mapping)

        # Select the questions
        selected_questions = []
        for _ in range(n_questions):
            selected_concept = np.random.choice(
                a=list(concept_weights.keys()),
                size=1,
                # This is done because the function only takes probability values.
                p=[raw_val / sum(concept_weights.values()) for raw_val in concept_weights.values()]
            )[0]
            new_question_list, selected_question = await self._select_a_question_for_concept(
                questions=concept_to_questions_mapping.get(selected_concept)
            )

            selected_questions.append(selected_question)
            if len(new_question_list) == 0:
                logger.debug(f"Question for {selected_concept} added. No questions remain.")
                concept_weights.pop(selected_concept)
            else:
                logger.debug(f"Question for {selected_concept} added.")
                concept_to_questions_mapping[selected_concept] = new_question_list

        return selected_questions

    async def get_one_question(self) -> Question:
        """ This function selects a single function from the given list.

        Returns:
            1 personalized question is returned.
        """
        concept_to_questions_mapping = await self._prepare_concept_to_questions_mapping()

        concept_weights = await self._get_formatted_concept_weights(concept_to_questions_mapping)

        selected_concept = np.random.choice(
            a=list(concept_weights.keys()),
            size=1,
            # This is done because the function only takes probability values.
            p=[raw_val / sum(concept_weights.values()) for raw_val in concept_weights.values()]
        )[0]
        new_question_list, selected_question = await self._select_a_question_for_concept(
            questions=concept_to_questions_mapping.get(selected_concept)
        )

        # TODO: Adjust session information.

        if len(new_question_list) == 0:
            logger.debug(f"Question for {selected_concept} added. No questions remain.")
        else:
            logger.debug(f"Question for {selected_concept} added.")

        return selected_question
