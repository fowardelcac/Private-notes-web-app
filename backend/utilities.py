from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from jwt import encode
from fastapi.templating import Jinja2Templates
from cryptography.fernet import Fernet


load_dotenv()

TEMPLATES = Jinja2Templates(directory="backend/static/templates")
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 1

CIPHER = Fernet(key=os.getenv("SECRET_FERNET"))


def fernet_crypt(data: str):
    return CIPHER.encrypt(data.encode("utf-8"))


def fernet_decrypt(data: bytes):
    bytes_text = CIPHER.decrypt(data)
    return bytes_text.decode("utf-8")


def verify_hash(password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(password, hashed_password)

def create_jwt(data: dict):
    to_encode = data.copy()
    to_encode["sub"] = data["sub"]
    return encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
