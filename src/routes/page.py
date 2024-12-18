from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from src.db.models import UserDb
from src.db.database import SESSIONDEP, DataSQL
from src.utils.security import TEMPLATES
from .auth import verify_cookies


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
