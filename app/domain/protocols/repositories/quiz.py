from typing import List, Protocol, Literal, Union
from datetime import datetime

from app.domain.models.quiz import Quiz, QuizResult


class QuizRepository(Protocol):
    async def add(self, quiz: Quiz) -> Quiz:
        ...

    async def get_one(self, quiz_id: int) -> Quiz:
        ...

    async def get_all_for_course(self, course_id: int) -> List[Quiz]:
        ...

    async def get_all_open_quizzes(self, course_id: int) -> List[Quiz]:
        ...

    async def get_all_unprocessed_past_due_date(self, due_date: datetime) -> List[Quiz]:
        ...

    async def delete(self, course_id: int, quiz_id: int) -> None:
        ...


class QuizResultsRepository(Protocol):
    async def add(self, quiz_result: QuizResult) -> QuizResult:
        ...

    async def get_one(self, quiz_id: int, student_id: int) -> QuizResult:
        ...

    async def get_results_for_quiz(self, quiz_id: int) -> List[QuizResult]:
        ...

    async def get_all_results_for_student(self, student_id: int) -> List[QuizResult]:
        ...

    async def get_quizzes_attempted_by_student(self, student_id: int) -> List[int]:
        ...
