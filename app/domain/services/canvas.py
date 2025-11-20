""" This file stores the service that allows us conduct read from and write to Canvas. This
service interacts with API endpoints exposed by Canvas. """
from typing import List, Union, Dict

from loguru import logger
from canvasapi import Canvas
from canvasapi.quiz import Quiz

from app.domain.models.question import QuestionAnswerSelection

_CANVAS_API_URL = "https://canvas.ucsd.edu/"


def translate_quiz_type(quiz_type: str) -> str:
    if quiz_type == "prereq":
        return "Prerequisite"
    elif quiz_type == "review":
        return "Review"
    else:
        return "Preview"


class CanvasCourseService:
    """ This class serves to interact with the Canvas API endpoints to conduct data extraction
    tasks or creation tasks.

    Notes:
        This implementation is built specifically for UC San Diego.
    """
    def __init__(self, access_token: str, course_id: int):
        self.canvas_client = Canvas(base_url=_CANVAS_API_URL, access_token=access_token)
        self.course = self.canvas_client.get_course(course_id)

    async def get_student_ids_in_course(self) -> List[int]:
        """ This function returns the IDs of the users enrolled in the "student" capacity in the
        given course.

        Returns:
            A list of IDs.
        """
        student_ids = []

        # The API call returns a paginated result set which needs to be processed.
        for student_record in self.course.get_users(enrollment_type=['student']):
            student_ids.append(student_record.id)

        return student_ids

    async def create_personalized_practice_quiz(
            self,
            student_id: int,
            module_id: int,
            type_of_quiz: str
    ) -> Quiz:
        """ This function generates a quiz in Canvas that is assigned to the given student id.
        A name is assigned to the quiz based on an automation logic in this function.

        - quiz_type='practice_quiz' leads to assignment_id being set to None.
        - quiz_type='assignment' implicitly assigns an assignment_id to the quiz.
        - We need the assignment_id to create an override. The override is a critical component
        as it is the component that assigns a quiz to a student.
        - We need to convert the quiz from type 'assignment' to type 'practice_quiz' in order to
        not flood the grade book in Canvas.

        Notes:
            - Quiz name logic: <MODULE_ID>. <TYPE_OF_QUIZ> Quiz #<STUDENT ID>

        Args:
            student_id: ID of the student
            module_id: Module ID for which the quiz is made.
            type_of_quiz: type of quiz. DO NOT CONFUSE WITH 'quiz_type' ARGUMENT IN CANVAS.

        Returns:
            quiz id
        """
        # read the Notes section in the docstrings to understand these steps.
        # TODO: Prof. has asked for the student_id in the quiz title to be anonymized.
        quiz = self.course.create_quiz(
            quiz={
                'title': f'Module #{module_id} {translate_quiz_type(type_of_quiz)} Quiz',
                'quiz_type': 'assignment',
                'only_visible_to_overrides': True,
                'published': False
            }
        )

        # Overriding the quiz so only the assigned student can view the quiz
        quiz_assignment = self.course.get_assignment(quiz.assignment_id)
        student_override = {
            'student_ids': [student_id],
            'title': f"{quiz.id}'s override"
        }
        quiz_assignment.create_override(assignment_override=student_override)

        quiz.edit(quiz={'quiz_type': 'practice_quiz'})

        return quiz

    async def add_question_to_quiz(
            self,
            quiz: Union[int, Quiz],
            question: QuestionAnswerSelection
    ) -> None:
        """ This function allows for a question to be added to the quiz.
        A forced typechecking of the dictionary items is conducted to make sure that proper
        formatting is maintained

        Args:
            quiz: Quiz ID or Object.
            question: A QuestionAnswerSelection object that contains Question + its answers.

        Returns:
            None
        """
        # If quiz id is given we get the quiz object
        if isinstance(quiz, int):
            quiz = self.course.get_quiz(quiz)

        answer = [answer.__dict__ for answer in question.answers]

        quiz.create_question(
            question={
                'question_name': question.question.question_name,
                'question_text': question.question.question_text,
                'question_type': question.question.question_type,
                'points_possible': question.question.points_possible,
                'correct_comments': question.question.correct_comments,
                'incorrect_comments': question.question.incorrect_comments,
                'text_after_answers': question.question.neutral_comments,
                'answers': answer
            }
        )

    async def get_formatted_submissions_for_quiz(self, quiz: Union[int, Quiz]) -> Dict:
        """ This function returns the latest submission for a given quiz. The function extracts
        the topic of the question and assigns correct/incorrect submission to it.

        TODO: Check with team and break function into 2 parts. Formatter and Query.

        Args:
            quiz: Quiz ID or Object.

        Returns:
            Dictionary where key is the concept name and value is a list of 0 or 1's. []
            The 0 & 1's indicate whether a question is answered correctly/incorrectly.
        """
        # If quiz id is given we get the quiz object
        if isinstance(quiz, int):
            quiz = self.course.get_quiz(quiz)

        # This step is needed because Canvas natively renames the Question for Student view. X(
        question_id_to_name_mapping = {}
        for question in quiz.get_questions():
            question_id_to_name_mapping[question.assessment_question_id] = question.question_name
        logger.debug(question_id_to_name_mapping)

        quiz_results = {}

        # Now, we formatted the latest submission.
        submission = list(quiz.get_submissions())[-1]
        for question in submission.get_submission_questions():
            concept = question_id_to_name_mapping.get(question.assessment_question_id)
            quiz_results[concept] = quiz_results.get(concept, []) + [int(question.correct)]

        return quiz_results


class CanvasResultsProcessor:
    ...
