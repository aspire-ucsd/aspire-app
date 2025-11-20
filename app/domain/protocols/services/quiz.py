from typing import List, Protocol, Literal, Union
from datetime import datetime

from app.domain.models.quiz import Quiz, QuizResult


class QuizService(Protocol):
    async def create_quiz(self, quiz: Quiz) -> Quiz:
        ...

    async def add_quiz_result(self, quiz_result: QuizResult) -> QuizResult:
        ...

    async def get_results_for_quiz(self, quiz_id: int) -> QuizResult:
        ...

    async def get_results_for_quiz_of_student(self, quiz_id: int, student_id: int) -> QuizResult:
        ...

    async def get_all_quizzes(self, course_id: int, student_id: Union[None, int]) -> List[Quiz]:
        ...

    async def get_all_open_quizzes(self, course_id: int, student_id: Union[None, int] = None) -> (
            List)[
        Quiz]:
        ...

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz:
        ...
