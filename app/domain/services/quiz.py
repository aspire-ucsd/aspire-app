from typing import List, Union

from fastapi import Depends

from app.domain.models.quiz import Quiz, QuizResult

from app.infrastructure.database.repositories.quiz import QuizRepository, QuizResultRepository
from app.domain.protocols.repositories.quiz import (
    QuizRepository as QuizRepoProtocol,
    QuizResultsRepository as QuizResultsRepoProtocol
)
from app.domain.protocols.services.quiz import QuizService as QuizServiceProtocol


class QuizService(QuizServiceProtocol):
    def __init__(
            self,
            quiz_repo: QuizRepoProtocol = Depends(QuizRepository),
            quiz_results_repo: QuizResultsRepoProtocol = Depends(QuizResultRepository)
    ):
        self.quiz_repo = quiz_repo
        self.quiz_results_repo = quiz_results_repo

    async def create_quiz(self, quiz: Quiz) -> Quiz:
        """ This function creates an entry in the DB for a quiz.

        Args:
            quiz: Quiz Object

        Returns:
            Created Quiz Object
        """
        return await self.quiz_repo.add(quiz=quiz)

    async def add_quiz_result(self, quiz_result: QuizResult) -> QuizResult:
        """ This function creates an entry in the DB for a quiz result(Quiz Attempt).

        Args:
            quiz_result: Quiz Result object

        Returns:
            Quiz Result Object
        """
        return await self.quiz_results_repo.add(quiz_result=quiz_result)

    async def get_results_for_quiz(self, quiz_id: int) -> List[QuizResult]:
        """ This function returns the results of a given quiz of all students.

        Args:
            quiz_id: Quiz ID

        Returns:
            List of Quiz Result Objects.
        """
        return await self.quiz_results_repo.get_results_for_quiz(quiz_id=quiz_id)

    async def get_results_for_quiz_of_student(self, quiz_id: int, student_id: int) -> QuizResult:
        """ This function returns the results of a given quiz for a given student.

        Args:
            quiz_id: Quiz ID
            student_id: Student ID

        Returns:

        """
        return await self.quiz_results_repo.get_one(quiz_id=quiz_id, student_id=student_id)

    async def get_all_quizzes_for_course(
            self,
            course_id: int
    ) -> List[Quiz]:
        """ This function returns all the quizzes assigned to a course.

        Args:
            course_id: Course id

        Returns:
            List of Quiz Objects
        """
        return await self.quiz_repo.get_all_for_course(course_id=course_id)


    async def get_all_open_quizzes(
            self,
            course_id: int,
            student_id: Union[None, int] = None
    ) -> List[Quiz]:
        """ This function returns all the quizzes that are currently open(i.e. pre-deadline).
        Additionally, if student_id is given then the quizzes that are NOT ATTEMPTED by the
        student are provided.

        Args:
            course_id: Course ID
            student_id: Optional input of Student ID

        Returns:
            List of Quiz Objects
        """
        open_quizzes = await self.quiz_repo.get_all_open_quizzes(course_id=course_id)

        # This list contains the quizzes already attempted by a student.
        exclude_quizzes = []
        if not student_id:
            exclude_quizzes = await self.quiz_results_repo.get_quizzes_attempted_by_student(
                student_id=student_id
            )

        return [quiz for quiz in open_quizzes if quiz.quiz_id not in exclude_quizzes]

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz:
        """ This function extracts a quiz from the DB based on its ID.

        Args:
            quiz_id: Quiz ID

        Returns:
            Quiz object
        """
        return await self.quiz_repo.get_one(quiz_id=quiz_id)
