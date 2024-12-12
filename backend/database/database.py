from sqlmodel import SQLModel, create_engine, Session, select
from .models import UserDb, DataDb
from typing import Annotated
from fastapi import Depends
from utilities import FernetUtility

# Database Engine Configuration
ENGINE = create_engine(
    "mysql+pymysql://root:123@localhost/pn",
    echo=False,
)


def create_db_and_tables():
    """
    Create database tables based on SQLModel-defined models.

    This function initializes all the tables defined in the `SQLModel` metadata.
    """
    SQLModel.metadata.create_all(ENGINE)


def get_session():
    """
    Dependency function to provide a database session.

    This function is used as a dependency in FastAPI routes to ensure
    that a session is provided to handle database operations. It uses
    a context manager to automatically close the session after the operation
    is complete.

    Yields:
        Session: A SQLModel database session.
    """
    with Session(ENGINE) as session:
        yield session


SESSIONDEP = Annotated[Session, Depends(get_session)]


class UserSQL:
    """
    A class to interact with the User database, providing methods to
    retrieve and add users.

    This class contains static methods for querying and modifying user data
    in the database.
    """

    @staticmethod
    def get_user(username: str, session: SESSIONDEP) -> UserDb:
        """
        Retrieves a user from the database by their username.

        Args:
            username (str): The username of the user to retrieve.
            session (SESSIONDEP): The database session to use for the query.

        Returns:
            UserDb: The user object retrieved from the database, or None if not found.
        """
        statement = select(UserDb).where(UserDb.username == username)
        return (session.exec(statement)).first()

    @staticmethod
    def add_user(username: str, hashed_password: str, session: SESSIONDEP) -> None:
        """
        Adds a new user to the database with a username and hashed password.

        Args:
            username (str): The username of the new user.
            hashed_password (str): The hashed password of the new user.
            session (SESSIONDEP): The database session to use for adding the new user.

        Returns:
            None: This method doesn't return any value.
        """
        new_user = UserDb(username=username, password=hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)


class DataSQL:
    """
    A class to interact with the Data database, providing methods to
    retrieve and add data associated with a user.

    This class contains static methods to query and modify data entries
    in the database, specifically tied to individual users.
    """

    @staticmethod
    def get_data(username: str, session: SESSIONDEP) -> dict:
        """
        Retrieves all data associated with a specific user.

        Args:
            username (str): The username of the user whose data is to be retrieved.
            session (SESSIONDEP): The database session to use for the query.

        Returns:
            dict: A list of dictionaries representing the user's data, with
                  decrypted content.
        """
        user: UserDb = UserSQL.get_user(username, session)
        statement = select(DataDb).where(DataDb.user_id == user.id)
        user_result = (session.exec(statement)).all()

        decrypted_results = []

        for result in user_result:
            decrypted_result = {
                "id": result.id,
                "title": result.title,
                "content": FernetUtility.fernet_decrypt(result.content),
                "user_id": result.user_id,
            }
            decrypted_results.append(decrypted_result)
        return decrypted_results

    @staticmethod
    def get_content_id(username: str, datadb_id: int, session: SESSIONDEP) -> DataDb:
        """
        Retrieves a specific data entry by its ID for a particular user.
        Args:
            username (str): The username of the user to whose data the entry belongs.
            datadb_id (int): The ID of the data entry to retrieve.
            session (SESSIONDEP): The database session to use for the query.

        Returns:
            DataDb: The data entry object with decrypted content, or None if not found.
        """
        user: UserDb = UserSQL.get_user(username, session)
        statement = select(DataDb).where(
            DataDb.id == datadb_id and DataDb.user_id == user.id
        )
        result = (session.exec(statement)).first()
        result.content = FernetUtility.fernet_decrypt(result.content)
        return result

    @staticmethod
    def add_data(
        title: str, hashed_content: bytes, user_id: int, session: SESSIONDEP
    ) -> None:
        """
        Adds a new data entry for a specific user.

        Args:
            title (str): The title of the data entry.
            hashed_content (bytes): The encrypted content to store in the data entry.
            user_id (int): The ID of the user who owns the data.
            session (SESSIONDEP): The database session to use for adding the new entry.

        Returns:
            None: This method doesn't return any value.
        """
        new_content = DataDb(title=title, content=hashed_content, user_id=user_id)
        session.add(new_content)
        session.commit()
        session.refresh(new_content)
