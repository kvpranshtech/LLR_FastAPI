# Option 1: For Pydantic v2 with pydantic-settings
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # ... other settings

    model_config = ConfigDict(env_file=".env")


settings = Settings()
