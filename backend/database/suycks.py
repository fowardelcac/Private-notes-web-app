from sqlmodel import SQLModel, create_engine, Session, select
from .models import UserDb, DataDb
from typing import Annotated
from fastapi import Depends
from utilities import fernet_decrypt

ENGINE = create_engine(
    "mysql+pymysql://root:123@localhost/pn",
    echo=False,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(ENGINE)


def get_session():
    with Session(ENGINE) as session:
        yield session


SESSIONDEP = Annotated[Session, Depends(get_session)]


class UserSQL:
    def get_user(user_name: str, session: SESSIONDEP) -> UserDb:
        statement = select(UserDb).where(UserDb.username == user_name)
        query = session.exec(statement)
        return query.first()

    def add_user(user_name: str, hashed_password: str, session: SESSIONDEP):
        new_user = UserDb(user_name, hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)


class DataSQL:

    @staticmethod
    def get_user_id(user_name: str, session: SESSIONDEP) -> UserDb:
        user = UserSQL.get_user(user_name, session)
        return user.id

    @staticmethod
    def get_data(user_name: str, session: SESSIONDEP) -> DataDb:
        statement = select(DataDb).where(DataDb.user_id == id)
        query = session.exec(statement)
        user_result = query.all()
        print(user_result)
        decrypted_results = []

        for result in user_result:
            decrypted_result = {
                "id": result.id,
                "title": result.title,
                "content": fernet_decrypt(result.content),
                "user_id": result.user_id,
            }
            decrypted_results.append(decrypted_result)
        return decrypted_results

    @staticmethod
    def get_content_id(username: str, datadb_id: int, session: SESSIONDEP) -> DataDb:
        user_id_data = DataSQL.get_user_id(username, session)
        statement = select(DataDb).where(
            DataDb.id == datadb_id and DataDb.user_id == user_id_data
        )
        query = session.exec(statement)
        return query.first()

    @staticmethod
    def add_data(title: str, hashed_content: bytes, user_id: int, session: SESSIONDEP):
        new_content = DataDb(title=title, content=hashed_content, user_id=user_id)
        session.add(new_content)
        session.commit()
        session.refresh(new_content)
