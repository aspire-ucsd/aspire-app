from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_PATH: str
    ENV: str
    LOG_LEVEL: str
    WEB_APP_DEBUG: str
    WEB_APP_VERSION: str
    WEB_APP_TITLE: str 
    WEB_APP_DESCRIPTION: str 
    DATABASE1_URL: str
    SSO_REDIS_SESSION_PREFIX: str
    OPENAI_API_KEY: str
    TRITON_API_KEY: str
    SECRET_HASH_KEY: str
    SESSION_ID_STORAGE_KEY: str
    REFRESH_TOKEN_STORAGE_KEY: str
    TIMEZONE: str
    
@lru_cache # Cache settings
def get_settings() -> Settings:
    load_dotenv()
    settings = Settings()
    return settings

def get_secret_key() -> str:
    return get_settings().SECRET_HASH_KEY
