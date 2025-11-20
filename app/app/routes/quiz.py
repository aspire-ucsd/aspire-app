from typing import Optional, List, Literal, Union, Dict
import json

# TODO: Discuss with team about the TZ for time operations.
import datetime

from loguru import logger
from mimetypes import guess_type
from sqlmodel import Session

from fastapi import APIRouter, Depends, File, Response, Request, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from fastapi_lti1p3 import enforce_auth
from fastapi_lti1p3.session_cache import SessionCache

from app.infrastructure.database.db import get_db

from app.domain.models.errors import ErrorResponse
from ..errors.db_error import DBError
from ..errors.validation_error import ValidationError

from app.domain.models.quiz import Quiz, QuizResult
from app.domain.protocols.routes.quiz import QuizParametersProtocol, QuizResultsProtocol
from app.domain.services.quiz import QuizService


router = APIRouter()


@router.put(
        path="/aspire_quiz/create",
        name="aspire_quiz:create_a_quiz",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def create_a_quiz(
        request: Request,
        quiz_params: QuizParametersProtocol,
        quiz_service = Depends(QuizService)
) -> None:
    try:
        session_data = await enforce_auth(request=request, accepted_roles={
            'TeacherEnrollment', 'DesignerEnrollment'
        })
    except ValidationError:
        return ErrorResponse(
            code=401,
            type="UnauthorizedAccess",
            message="Only the Instructional Team has access to this."
        )
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    await quiz_service.create_quiz(
        quiz=Quiz(
            course_id=session_info.get('course_id'),
            module_id=quiz_params.module_id,
            sme_input=quiz_params.sme_input,
            sme_importance=quiz_params.sme_importance,
            n_questions=quiz_params.n_questions,
            quiz_type=quiz_params.quiz_type,
            due_date=quiz_params.due_date
        )
    )


@router.get(
        path="/aspire_quiz/get_all_quizzes_for_course",
        name="aspire_quiz:get_all_quizzes_for_course",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def get_all_quizzes_for_course(
        request: Request,
        quiz_service = Depends(QuizService)
) -> None:
    session_data = await enforce_auth(request=request, accepted_roles={
        'TeacherEnrollment', 'DesignerEnrollment', 'StudentEnrollment'
    })
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    return await quiz_service.get_all_quizzes_for_course(course_id=session_info.get('course_id'))


@router.get(
        path="/aspire_quiz/get_all_open_quizzes_for_course",
        name="aspire_quiz:get_all_open_quizzes_for_course",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def get_all_open_quizzes_for_course(
        request: Request,
        quiz_service = Depends(QuizService)
) -> None:
    session_data = await enforce_auth(request=request, accepted_roles={
        'TeacherEnrollment', 'DesignerEnrollment', 'StudentEnrollment'
    })
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    return await quiz_service.get_all_open_quizzes(course_id=session_info.get('course_id'))


@router.get(
        path="/aspire_quiz/get_all_open_quizzes_for_student",
        name="aspire_quiz:get_all_open_quizzes_for_student",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def get_all_open_quizzes_for_student(
        request: Request,
        quiz_service = Depends(QuizService)
) -> None:
    session_data = await enforce_auth(request=request, accepted_roles={
        'TeacherEnrollment', 'DesignerEnrollment', 'StudentEnrollment'
    })
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    return await quiz_service.get_all_open_quizzes(
        course_id=session_info.get('course_id'),
        student_id=session_info.get('user_id')
    )


@router.put(
        path="/aspire_quiz/create_submission",
        name="aspire_quiz:create_submission",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def create_submission(
        request: Request,
        quiz_results: QuizResultsProtocol,
        quiz_service = Depends(QuizService)
) -> None:
    session_data = await enforce_auth(request=request, accepted_roles={'StudentEnrollment'})
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    return await quiz_service.add_quiz_result(
        quiz_result=QuizResult(
            quiz_id=quiz_results.quiz_id,
            student_id=session_info.get('user_id'),
            correct=quiz_results.correct,
            total=quiz_results.total,
            total_time_taken_secs=quiz_results.total_time_taken_secs
        )
    )


@router.post(
        path="/aspire_quiz/check_if_attempted",
        name="aspire_quiz:check_if_attempted",
        responses={
            404: {"model": ErrorResponse},
            400: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
            }
        )
async def check_if_attempted(
        request: Request,
        quiz_id: int,
        quiz_service = Depends(QuizService)
) -> None:
    session_data = await enforce_auth(request=request, accepted_roles={
        'TeacherEnrollment', 'DesignerEnrollment', 'StudentEnrollment'
    })
    session_info = session_data.id_token.get('https://purl.imsglobal.org/spec/lti/claim/custom')

    results = await quiz_service.get_results_for_quiz_of_student(
        quiz_id=quiz_id,
        student_id=session_info.get('user_id')
    )
    if results:
        return True
    return False