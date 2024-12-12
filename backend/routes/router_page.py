from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from routes.router_auth import verify_cookies
from typing import Annotated
from database.models import UserDb
from database.database import SESSIONDEP, DataSQL, UserSQL
from utilities import TEMPLATES, FernetUtility

router_home = APIRouter(tags=["Home"])


@router_home.get("/user/home", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
    session: SESSIONDEP,
) -> HTMLResponse:
    """
    Serves the user's homepage, displaying their private data.

    Args:
        request (Request): The HTTP request object for rendering the template.
        current_user (Annotated[UserDb, Depends(verify_cookies)]): The authenticated user retrieved via cookies.
        session (SESSIONDEP): The database session dependency.

    Returns:
        HTMLResponse: A rendered template of the homepage containing user data.
    """
    result: dict = DataSQL.get_data(username=current_user.username, session=session)
    return TEMPLATES.TemplateResponse(
        "C_homepage.html", {"request": request, "user": current_user, "items": result}
    )


@router_home.get("/user/home/content/new", response_class=HTMLResponse)
async def new_content(
    request: Request,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
) -> HTMLResponse:
    """
    Serves the page for creating new content.

    Args:
        request (Request): The HTTP request object for rendering the template.
        current_user (Annotated[UserDb, Depends(verify_cookies)]): The authenticated user retrieved via cookies.

    Returns:
        HTMLResponse: A rendered template for creating new content.
    """
    return TEMPLATES.TemplateResponse(
        "D_content.html", {"request": request, "user": current_user}
    )


@router_home.post("/user/home/content/new")
async def create_content(
    session: SESSIONDEP,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
    title: str = Form(...),
    content: str = Form(...),
) -> RedirectResponse:
    """
    Handles the creation of new user content by saving it in the database.

    Args:
        session (SESSIONDEP): The database session dependency.
        current_user (Annotated[UserDb, Depends(verify_cookies)]): The authenticated user.
        title (str): The title of the new content, retrieved from the form.
        content (str): The actual content, retrieved from the form.

    Returns:
        RedirectResponse: Redirects the user to their homepage after content creation.
    """
    hashed_content: bytes = FernetUtility.fernet_crypt(content)
    user_data: UserDb = UserSQL.get_user(current_user.username, session)
    DataSQL.add_data(
        title=title,
        hashed_content=hashed_content,
        user_id=user_data.id,
        session=session,
    )
    return RedirectResponse(url="/user/home", status_code=303)


@router_home.get("/user/home/content/note/{note_id}", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    note_id: int,
    session: SESSIONDEP,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
) -> HTMLResponse:
    """
    Serves the detailed view of a specific note.

    Args:
        request (Request): The HTTP request object for rendering the template.
        note_id (int): The ID of the note to display.
        session (SESSIONDEP): The database session dependency.
        current_user (Annotated[UserDb, Depends(verify_cookies)]): The authenticated user.

    Returns:
        HTMLResponse: A rendered template containing the note details.
    """
    list_data = DataSQL.get_content_id(
        username=current_user.username, datadb_id=note_id, session=session
    )
    return TEMPLATES.TemplateResponse(
        "C_note_page.html",
        {"request": request, "user": current_user, "data_list": list_data},
    )


@router_home.post("/user/home/logout", response_class=HTMLResponse)
async def logout() -> RedirectResponse:
    """
    Logs the user out by deleting the authentication cookie and redirecting to the login page.

    Returns:
        RedirectResponse: A response that deletes the user's cookie and redirects to the specified URL.
    """
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(
        key="access_token",  # The name of the cookie to be deleted, in this case, "access_token".
    )

    return response
