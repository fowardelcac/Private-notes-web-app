from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from src.db.models import UserDb
from src.db.database import SESSIONDEP, DataSQL, UserSQL
from src.utils.security import TEMPLATES, FernetUtility
from .auth import verify_cookies
 
router_new_content = APIRouter(tags=["Content"])


@router_new_content.get("/user/home/content/new", response_class=HTMLResponse)
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


@router_new_content.post("/user/home/content/new")
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
