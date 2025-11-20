from fastapi import HTTPException, Request
from fastapi.applications import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from toolz import pipe

from app.app.errors.http_error import http_error_handler, validation_error_handler
from app.app.errors.user_info_error import get_user_info_exception_handler, UserInfoException
from app.app.routes import register_routers as register_routers
from app.config.environment import Settings
from app.infrastructure.database.db import create_db_and_tables, init_db
from app.infrastructure.event_processor.process_manager import start_process_worker

class TemplateMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        templates = Jinja2Templates(directory="app/app/templates")
        request.state.templates = templates
        # process the request and get the response    
        response = await call_next(request)
        
        return response

    

def create_instance(settings: Settings) -> FastAPI:

    return {"app": FastAPI(
        docs_url=settings.BASE_PATH + '/docs', redoc_url=None, 
        openapi_url=settings.BASE_PATH + '/openapi.json',
        debug=settings.WEB_APP_DEBUG,
        title=settings.WEB_APP_TITLE,
        description=settings.WEB_APP_DESCRIPTION,
        version=settings.WEB_APP_VERSION,
        prefix=settings.BASE_PATH
    ), "settings": settings}

def init_database(app: FastAPI) -> FastAPI:
    # TODO init databases if applicable
    init_db()
    return app

def register_events(app: FastAPI) -> FastAPI:
    # TODO add events if applicable
    # app.on_event("startup")(create_db_and_tables) # This event can be removed if not seeding a database
    app.on_event("startup")(start_process_worker)

    return app


def register_middleware(config: dict) -> FastAPI:
    # TODO register middleware if applicable
    app = config.get("app")
    settings = config.get("settings")
    app.add_middleware(TemplateMiddleware)
    app.add_middleware(CORSMiddleware, 
        allow_origins=["http://localhost:8081", "https://ucsd-dev.instructure.com"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[settings.SESSION_ID_STORAGE_KEY, settings.REFRESH_TOKEN_STORAGE_KEY]
)
    
    return app

def register_exception_handlers(app: FastAPI) -> FastAPI:
    # TODO register exception handlers if applicable
    # Modify HttpExceptions to follow API guidelines
    # app.add_exception_handler(HTTPException, http_error_handler)
    # app.add_exception_handler(StarletteHTTPException, http_error_handler)
    # app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(UserInfoException, get_user_info_exception_handler)
    return app
    

def init_app(settings: Settings) -> FastAPI:
    app: FastAPI = pipe(
        settings,
        create_instance,
        register_middleware,
        init_database,
        register_events,
        register_routers,
        register_exception_handlers,
    )
    app.mount(settings.BASE_PATH + "/static", StaticFiles(directory="app/static"), name="static")
    return app
