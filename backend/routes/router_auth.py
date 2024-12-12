from fastapi import APIRouter, HTTPException, status, Depends, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from database.models import UserDb
from database.database import UserSQL, SESSIONDEP
from utilities import TEMPLATES, PWD, JWTUtility


router_auth = APIRouter(tags=["Auth"])


def authenticate_user(user: OAuth2PasswordRequestForm, session: SESSIONDEP) -> UserDb:
    """
    Authenticates a user by verifying their username and password.

    Args:
        user (OAuth2PasswordRequestForm): The user credentials provided via a login form.
                                          Contains the username and password.
        session (SESSIONDEP): The database session dependency for interacting with the database.

    Returns:
        UserDb: The authenticated user's database object if the credentials are correct.

    Raises:
        HTTPException:
            - If the user does not exist (status code 404).
            - If the password is incorrect (status code 401).
    """
    user_db: UserDb = UserSQL.get_user(user.username, session)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist"
        )

    if not PWD.verify_hash(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect"
        )
    return user_db


async def verify_cookies(
    session: SESSIONDEP,
    access_token: Annotated[str | None, Cookie()] = None,
) -> UserDb:
    """
    Verifies the user's authentication cookies by decoding the JWT and retrieving user data.

    Args:
        session (SESSIONDEP): The database session dependency for interacting with the database.
        access_token (Annotated[str | None, Cookie()]): The JWT access token extracted from cookies.

    Returns:
        UserDb: The authenticated user's database object.

    Raises:
        HTTPException: If the credentials cannot be validated or the user does not exist in the database.
                       Returns status code 401 with a `WWW-Authenticate` header.
    """
    payload: dict = JWTUtility.decode_jwt(access_token=access_token)
    if payload.get("sub"):
        username: str = payload.get("sub")
    user: UserDb = UserSQL.get_user(username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router_auth.get("/token", response_class=HTMLResponse)
async def show_register_page(
    request: Request, error: str | None = None
) -> HTMLResponse:
    """
    Renders the registration or login page for the user.

    Args:
        request (Request): The incoming HTTP request object, required by the template engine.
        error (str | None): An optional error message to be displayed on the page if provided.

    Returns:
        HTMLResponse: The rendered HTML page with the provided context, including the error message if applicable.
    """
    return TEMPLATES.TemplateResponse(
        "A_home.html", {"request": request, "error": error}
    )


@router_auth.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SESSIONDEP
) -> RedirectResponse:
    """
    Handles user login, validates credentials, and sets an access token cookie.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): The login form data containing
                                                                     the username and password.
        session (SESSIONDEP): The database session dependency for querying user data.

    Returns:
        RedirectResponse:
            - Redirects to the user's home page (`/user/home`) with a valid access token set as an HTTP-only cookie.
            - Redirects back to the login page (`/token`) with an error message in the query string if login fails.

    Raises:
        HTTPException: If authentication fails, captures and processes the exception to determine the error message.
    """
    try:
        user = authenticate_user(form_data, session)
        access_token = JWTUtility.create_jwt(data={"sub": user.username})
        response = RedirectResponse(
            url="/user/home",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(key="access_token", value=access_token)
        return response
    except HTTPException as e:
        error_message = (
            e.detail
            if (
                e.status_code == status.HTTP_404_NOT_FOUND
                or e.status_code == status.HTTP_401_UNAUTHORIZED
            )
            else "invalid credentials"
        )
        print(error_message)
        return RedirectResponse(
            url=f"/token?error={error_message}",
            status_code=status.HTTP_302_FOUND,
        )
