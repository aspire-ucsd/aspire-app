from fastapi import APIRouter
from fastapi.applications import FastAPI

from fastapi_lti1p3 import routes
from app.app.routes import (root, qas, question, prompt, student, quiz)

from app.app.routes.course import concept_collection, course, llm_services
from app.app.routes.domain import change_requests, concept as domainConcepts, domain, templates, concept_to_concept
from app.app.routes.admin import course as courseAdmin


from app.config.environment import get_settings
from app.domain.models.errors import APIMErrorResponse, ErrorResponse

def register_routers(app: FastAPI) -> FastAPI:
    settings = get_settings()
    app.router.prefix=settings.BASE_PATH
    app.router.responses |= {
        400: {"model": ErrorResponse}, 
        404: {"model": ErrorResponse}, 
        401: {"model": APIMErrorResponse}, 
        422: {"model": APIMErrorResponse}, 
        500: {"model": ErrorResponse}
        }

    app.include_router(root.router)
    app.include_router(routes.router, tags=["LTI-Adapter"])
    # app.include_router(qas.router, tags=["QAS"], prefix="/qas")
    # app.include_router(quiz.router, tags=["Quiz"], prefix="/aspire_quiz")

    # app.include_router(question.router, tags=["Question"], prefix="/question")
    # app.include_router(prompt.router, tags=["Prompt"], prefix="/prompt")
    # app.include_router(student.router, tags=["Student"], prefix="/student")

    app.include_router(course.router, tags=["Course"], prefix="/course")  
    app.include_router(llm_services.router, tags=["Course-LLM-Services"], prefix="/course/llm")  
    app.include_router(concept_collection.router, tags=["Collection", "Concept-to-Collection"], prefix="/course/collection")

    app.include_router(domain.router, tags=["Domain"], prefix="/domain")
    app.include_router(domainConcepts.router, tags=["Domain-Concepts"], prefix="/domain/concept")
    app.include_router(concept_to_concept.router, tags=["Domain-ConceptToConcept"], prefix="/domain/concept/junction")
    # app.include_router(templates.router, tags=["Domain-Templates"], prefix="/domain/templates")
    app.include_router(change_requests.router, tags=["Change-Requests"], prefix="/domain/changes")

    # app.include_router(courseAdmin.router, tags=["Admin-Courses"], prefix="/admin/course")



    return app