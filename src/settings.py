from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # Obligatoria
    ALGORITHM: str = Field(default="HS256")  # Default HS256
    SECRET_FERNET: str = Field(..., env="SECRET_FERNET")

    class Config:
        env_file = ".env"
