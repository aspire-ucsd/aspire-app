from typing import List, Protocol, Literal, Union
from datetime import datetime

from sqlmodel import Session, select, col
from fastapi import Depends

from app.domain.models.quiz import Quiz, QuizResult
from app.domain.protocols.repositories.quiz import (
    QuizRepository as QuizRepoProtocol,
    QuizResultsRepository as QuizResultsRepoProtocol
)
from app.infrastructure.database.db import get_db


class QuizRepository(QuizRepoProtocol):
    db: Session

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, quiz: Quiz) -> Quiz:
        quiz = Quiz.from_orm(quiz)
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return Quiz.from_orm(quiz)

    async def get_one(self, quiz_id: int) -> Quiz:
        return self.db.exec(
            select(Quiz).where(Quiz.id == quiz_id)
        ).first()

    async def get_all_for_course(self, course_id: int) -> List[Quiz]:
        return self.db.exec(
            select(Quiz).where(Quiz.course_id == course_id)
        ).all()

    async def get_all_open_quizzes(self, course_id: int) -> List[Quiz]:
        return self.db.exec(
            select(Quiz).where(Quiz.course_id == course_id).where(
                Quiz.due_date > datetime.now()
            )
        ).all()

    async def get_all_unprocessed_past_due_date(self, due_date: datetime) -> List[Quiz]:
        # TODO: Make this compliant with the new schema
        return self.db.exec(
            select(Quiz).where(Quiz.due_date < due_date)#.where(Quiz.processed == False)
        ).all()

    async def delete(self, course_id: int, quiz_id: int) -> None:
        ...


class QuizResultRepository(QuizResultsRepoProtocol):
    db: Session

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, quiz_result: QuizResult) -> QuizResult:
        quiz_result = QuizResult.from_orm(quiz_result)
        self.db.add(quiz_result)
        self.db.commit()
        self.db.refresh(quiz_result)
        return QuizResult.from_orm(quiz_result)

    async def get_one(self, quiz_id: int, student_id: int) -> QuizResult:
        return self.db.exec(
            select(QuizResult).where(QuizResult.quiz_id == quiz_id).where(
                QuizResult.student_id == student_id
            )
        ).all()

    async def get_results_for_quiz(self, quiz_id: int) -> List[QuizResult]:
        return self.db.exec(
            select(QuizResult).where(QuizResult.quiz_id == quiz_id)
        ).all()

    async def get_all_results_for_student(self, student_id: int) -> List[QuizResult]:
        return self.db.exec(
            select(QuizResult).where(QuizResult.student_id == student_id)
        ).all()

    async def get_quizzes_attempted_by_student(self, student_id: int) -> List[int]:
        results = self.db.exec(
            select(QuizResult).where(QuizResult.student_id == student_id)
        ).all()

        return [quiz_result.quiz_id for quiz_result in results]
