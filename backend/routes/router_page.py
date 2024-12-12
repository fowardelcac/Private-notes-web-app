from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from routes.router_auth import verify_cookies
from typing import Annotated
from database.models import UserDb
from database.database import SESSIONDEP, DataSQL, UserSQL
from utilities import TEMPLATES, fernet_crypt

router_home = APIRouter(tags=["Home"])


@router_home.get("/user/home", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
    session: SESSIONDEP,
):
    result = DataSQL.get_data(user_name=current_user.username, session=session)
    print(result)
    return TEMPLATES.TemplateResponse(
        "C_homepage.html", {"request": request, "user": current_user, "items": result}
    )


@router_home.get("/user/home/content/new", response_class=HTMLResponse)
async def new_content(
    request: Request,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
):
    return TEMPLATES.TemplateResponse(
        "D_content.html", {"request": request, "user": current_user}
    )


@router_home.post("/user/home/content/new")
async def create_content(
    session: SESSIONDEP,
    current_user: Annotated[UserDb, Depends(verify_cookies)],
    title: str = Form(...),
    content: str = Form(...),
):
    hashed_content = fernet_crypt(content)
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
):
    list_data = DataSQL.get_content_id(
        username=current_user.username, datadb_id=note_id, session=session
    )
    return TEMPLATES.TemplateResponse(
        "C_note_page.html",
        {"request": request, "user": current_user, "data_list": list_data},
    )
