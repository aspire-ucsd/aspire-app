from typing import List, Optional, Protocol
from app.domain.models.question import (
    QuestionCreate,
    QuestionRead,
    AnswerPreCreate,
    AnswerRead,
    QuestionAnswerInput
)

class QuestionService(Protocol):
    async def create_question(self, question: QuestionAnswerInput) -> QuestionRead:
        ...

    async def create_questions(self, questions: List[QuestionAnswerInput]) -> List[QuestionRead]:
        ...

    async def get_question(self, question_id: int) -> QuestionRead:
        ...

    async def get_questions_by_id(self, id_list: List) -> List[QuestionRead]:
        ...

    async def get_all_questions_for_concepts(self, concept_list: List) -> List[QuestionRead]:
        ...

    async def get_answers_for_questions(self, question_ids: List) -> List[AnswerRead]:
        ...

    async def get_answers_for_one_question(self, question_id: int) -> AnswerRead:
        ...

    # async def update_question(self, question_id: int, question_update: QuestionUpdate) -> QuestionRead:
    #     ...

    async def delete_question(self, question_id: int) -> None:
        ...