from typing import List, Literal, Protocol, Union

from fastapi import Depends
from sqlmodel import Session, col, select

from app.domain.models.question import (
    Answer,
    AnswerCreate,
    AnswerRead,
    Question,
    QuestionCreate,
    QuestionRead,
)
from app.domain.protocols.repositories.question import (
    AnswerRepository as AnswerRepoProtocol,
)
from app.domain.protocols.repositories.question import (
    QuestionRepository as QuestionRepoProtocol,
)
from app.infrastructure.database.db import get_db


class QuestionRepository(QuestionRepoProtocol):
    db: Session
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, question: QuestionCreate) -> QuestionRead:
        question = Question.from_orm(question)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return QuestionRead.from_orm(question)

    async def get_one_by_id(self, id: int) -> Question:
        """ THis function returns a single question based on matching id.

        Args:
            id: ID of the question

        Returns:
            Question to return.
        """
        return self.db.exec(
            select(Question).where(col(Question.id) == id)
        ).first()

    async def bulk_get_by_id(self, id_list: List) -> List[Question]:
        """ This function returns all question where the ids are in the list.

        Args:
            id_list: List of Question IDs

        Returns:
            List of QuestionRead objects
        """
        return self.db.exec(
            select(Question).where(col(Question.id).in_(id_list))
        ).all()

    async def get_all_by_concept(self, concept_list: List) -> List[QuestionRead]:
        """ This function returns all the questions for the concepts in the concept_list.

        Args:
            concept_list: List of concepts

        Returns:
            List of QuestionRead objects
        """
        return self.db.exec(
            select(Question).where(col(Question.question_name).in_(concept_list))
        ).all()

class AnswerRepository(AnswerRepoProtocol):
    db: Session
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, answer: AnswerCreate) -> AnswerRead:
        answer = Answer.from_orm(answer)
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return AnswerRead.from_orm(answer)

    async def get_answer_for_question_id(self, id: int) -> List[Answer]:
        """ This function returns all the answers for the given question id.

        Args:
            id: Question ID

        Returns:
            Returns a list of answers. (1 question has multiple Answers)
        """
        return self.db.exec(
            select(Answer).where(col(Answer.question_id) == id)
        ).all()


    async def get_answers_by_question_ids(self, question_ids: List) -> List[Answer]:
        """ This function returns all the answers for the given question ids.

        Args:
            question_ids: Question IDs for which we need the answers.

        Returns:
            Returns a list of answers.
        """
        return self.db.exec(
            select(Answer).where(col(Answer.question_id).in_(question_ids))
        )
