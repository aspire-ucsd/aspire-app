""" This function contains multiple parsing utility functions used throughout the app."""
from typing import List

import pandas as pd

from app.domain.models.concept import ConceptBulkRead
from app.domain.models.question import Question, AnswerRead, QuestionAnswerSelection


async def extract_concept_names_from_concept_bulk_read(concepts_object: ConceptBulkRead) -> List:
    """ This function extracts the names of the concepts provided in the Concept object.

    Args:
        concepts_object: ConceptBulkRead object containing prerequisite concepts.

    Returns:
        List of concept names
    """
    return [concept.name for concept in concepts_object.concepts]


async def convert_question_list_to_dataframe(questions: List[Question]) -> pd.DataFrame:
    """ This function formats the List of Question Objects obtained into a pandas dataframe.

    Args:
        questions: List of Question objects

    Returns:
        A pandas dataframe of questions.
    """
    return pd.DataFrame.from_records(data=[question.dict() for question in questions])


async def map_answers_to_questions(
        questions: List[Question],
        answers: List[AnswerRead]
) -> List[QuestionAnswerSelection]:
    """ This function takes in a list of question objects and a list of answer objects and maps
    them together. If an answer does not have a respective question then an error is raised.

    Args:
        questions: List of Question objects
        answers: List of Answer objects

    Returns:
        A list of mapped QuestionAnswerSelection Objects.
    """
    # TODO: Improve the performance of this code. Currently O(nxm)
    question_to_object_mapping ={}
    for answer in answers:
        for question in questions:
            if question.id == answer.question_id:
                if question_to_object_mapping.get(question.id) is None:
                    question_to_object_mapping[question.id] = QuestionAnswerSelection(
                        question=question,
                        answers=[]
                    )
                question_to_object_mapping[question.id].answers = question_to_object_mapping[
                    question.id].answers + [answer]

    return list(question_to_object_mapping.values())
