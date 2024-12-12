from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from database.database import SESSIONDEP, UserSQL, UserDb
from utilities import PWD, TEMPLATES, JWTUtility
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm


router_register = APIRouter(tags=["Register"])


@router_register.get("/user/register", response_class=HTMLResponse)
async def show_register_page(request: Request) -> HTMLResponse:
    """
    Renders the user registration page.

    Args:
        request (Request): The HTTP request object to be passed to the template engine.

    Returns:
        HTMLResponse: The rendered HTML page for user registration.
    """
    return TEMPLATES.TemplateResponse("B_register.html", {"request": request})


@router_register.post("/user/register")
async def register_acces(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SESSIONDEP,
) -> RedirectResponse:
    """
    Handles user registration by validating input, creating a new user in the database, 
    and setting an access token cookie for the user.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): The form data containing the user's 
                                                                     username and password.
        session (SESSIONDEP): The database session dependency for interacting with the user database.

    Returns:
        RedirectResponse: Redirects the user to the home page after successful registration, 
                          setting an access token in the response cookie.

    Raises:
        HTTPException: If the user already exists, raises an HTTP 400 Bad Request error.
    """
    try:
        user_db = UserSQL.get_user(username=form_data.username, session=session)
        if user_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user already exists.",
            )

        hashed_password = PWD.hash(secret=form_data.password)
        UserSQL.add_user(
            username=form_data.username,
            hashed_password=hashed_password,
            session=session,
        )

        access_token = JWTUtility.create_jwt(data={"sub": form_data.username})
        response = RedirectResponse(
            url="/user/home",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response

    except HTTPException as e:
        error_message = (
            e.detail
            if e.status_code == status.HTTP_400_BAD_REQUEST
            else "invalid_credentials"
        )
        return RedirectResponse(
            url=f"/token?error={error_message}",
            status_code=status.HTTP_302_FOUND,
        )
