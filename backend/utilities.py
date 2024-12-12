from passlib.context import CryptContext
import jwt
from cryptography.fernet import Fernet
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()
TEMPLATES = Jinja2Templates(directory="backend/static/templates")


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # Obligatoria
    ALGORITHM: str = Field(default="HS256")  # Default HS256
    SECRET_FERNET: str = Field(..., env="SECRET_FERNET")

    class Config:
        env_file = ".env"


settings = Settings()


class JWTUtility:
    @staticmethod
    def create_jwt(data: dict) -> str:
        return jwt.encode(
            payload=data, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

    @staticmethod
    def decode_jwt(access_token: str) -> dict:
        try:
            return jwt.decode(
                jwt=access_token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
            )
        except jwt.PyJWKError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )


class FernetUtility:
    cypher: Fernet = Fernet(key=settings.SECRET_FERNET)

    @staticmethod
    def fernet_crypt(data: str) -> bytes:
        return FernetUtility.cypher.encrypt(data.encode("utf-8"))

    @staticmethod
    def fernet_decrypt(data: bytes) -> str:
        bytes_text: bytes = FernetUtility.cypher.decrypt(data)
        return bytes_text.decode("utf-8")


class PWD:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_hash(password: str, hashed_password: str) -> bool:
        return PWD.PWD_CONTEXT.verify(password, hashed_password)
    @staticmethod
    def hash(secret: str) -> str:
        return PWD.PWD_CONTEXT.hash(secret)
