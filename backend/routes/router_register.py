from fastapi import APIRouter, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from database.database import SESSIONDEP, UserSQL
from utilities import PWD_CONTEXT, TEMPLATES


class UserAPI(BaseModel):
    username: str
    password: str


router_register = APIRouter(tags=["Register"])


@router_register.get("/user/register", response_class=HTMLResponse)
async def show_register_page(request: Request):
    return TEMPLATES.TemplateResponse("B_register.html", {"request": request})


@router_register.post("/user/register")
async def register_acces(
    session: SESSIONDEP, username: str = Form(...), password: str = Form(...)
):
    try:
        user_db = UserSQL.get_user(user_name=username, session=session)
        if user_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The_user_already_exists",
            )

        hashed_password = PWD_CONTEXT.hash(password)
        UserSQL.add_user(
            user_name=username, hashed_password=hashed_password, session=session
        )
        return RedirectResponse("/token", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        # Capturamos los errores de autenticación y redirigimos con el mensaje de error adecuado
        error_message = (
            e.detail
            if e.status_code == status.HTTP_400_BAD_REQUEST
            else "invalid_credentials"
        )
        return RedirectResponse(
            url=f"/?error={error_message}",
            status_code=status.HTTP_302_FOUND,
        )
