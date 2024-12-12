from sqlmodel import SQLModel, Field
from typing import Optional


class UserDb(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=True)
    username: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)


class DataDb(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    user_id: Optional[int] = Field(default=None, foreign_key="userdb.id")
