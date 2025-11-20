from typing import Optional, List, Union

from fastapi import APIRouter, Depends, Response, Request

from ..errors.db_error import DBError

from app.domain.models.errors import ErrorResponse

from app.domain.protocols.services.question import QuestionService as QuestionServiceProtocol
from app.domain.services.question import QuestionService
from app.domain.models.question import QuestionAnswerInput, QuestionRead

router = APIRouter()

@router.post("/create", name="Question:save-question", response_model=Union[List[QuestionRead], ErrorResponse])
async def save_questions(
    request: Request, 
    response: Response,
    questions: List[QuestionAnswerInput],
    question_service: QuestionServiceProtocol = Depends(QuestionService)
    ) -> Union[List[QuestionRead], ErrorResponse]:

    try:
        return await question_service.create_questions(questions=questions)
    
    except DBError as e:
        response.status_code = e.status_code
        return ErrorResponse(
            code=e.status_code,
            type=e.type,
            message=str(e)
        )