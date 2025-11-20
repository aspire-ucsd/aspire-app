from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.config.environment import get_settings
from app.infrastructure.database.seeds import run as seed_db

_SETTINGS = get_settings()

# TODO implement your own database connection(s)

def get_engine():
    return create_engine(_SETTINGS.DATABASE1_URL, echo=False)

def init_db():
    SQLModel.metadata.bind = get_engine()

def get_db() -> Generator:
    with Session(get_engine()) as db:
        return db
        
def create_db_and_tables():
    SQLModel.metadata.create_all(bind=get_engine())
    seed_db(get_db())