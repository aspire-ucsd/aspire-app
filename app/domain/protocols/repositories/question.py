from typing import List, Protocol, Literal, Union
from app.domain.models.question import (QuestionCreate, QuestionRead, AnswerCreate, AnswerRead,
                                        Question)

class QuestionRepository(Protocol):
    async def add(self, question: QuestionCreate) -> QuestionRead:
        ...

    async def get_one_by_id(self, id: int) -> Question:
        ...

    async def bulk_get_by_id(self, id_list: List) -> List[Question]:
        ...

    async def get_all_by_concept(self, concept_list: List) -> List[QuestionRead]:
        ...

class AnswerRepository(Protocol):
    async def add(self, answer: AnswerCreate) -> AnswerRead:
        ...

    async def get_answer_for_question_id(self, id: int) -> List[AnswerRead]:
        ...

    async def get_answers_by_question_ids(
            self, question_ids: List) -> List[AnswerRead]:
        ...
