from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"

    class Config:
        env_file = ".env"


settings = Settings()