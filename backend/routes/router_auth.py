from fastapi import APIRouter, HTTPException, status, Depends, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from jwt import decode, PyJWKError
from pydantic import BaseModel
import os
from database.models import UserDb
from utilities import TEMPLATES, verify_hash, create_jwt
from database.database import UserSQL, SESSIONDEP


class TokenData(BaseModel):
    username: str | None = None


router_auth = APIRouter(tags=["Auth"])


def authenticate_user(user: OAuth2PasswordRequestForm, session: SESSIONDEP) -> UserDb:
    user_db: UserDb = UserSQL.get_user(user.username, session)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The_user_does_not_exist"
        )

    if not verify_hash(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password_is_incorrect"
        )
    return user_db


async def verify_cookies(
    session: SESSIONDEP,
    access_token: Annotated[str | None, Cookie()] = None,
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Payload es el DICCIONARIO/JSON {'name': 'Dua', 'password': '$2b$12$ynImoN278Oc9umoatK.LyO.lwR4HPjNxPx3v/JKB1Amwn.0k2HU0i'}
        payload = decode(
            access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except PyJWKError:
        raise credential_exception

    user: UserDb = UserSQL.get_user(token_data.username, session)
    if user is None:
        raise credential_exception
    return user


@router_auth.get("/token", response_class=HTMLResponse)
async def show_register_page(request: Request):
    return TEMPLATES.TemplateResponse("A_home.html", {"request": request})


@router_auth.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SESSIONDEP
) -> RedirectResponse:
    try:
        user = authenticate_user(form_data, session)
        access_token = create_jwt(data={"sub": user.username})
        response = RedirectResponse(
            url="/user/home",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except HTTPException as e:
        error_message = (
            e.detail
            if (
                e.status_code == status.HTTP_404_NOT_FOUND
                or e.status_code == status.HTTP_401_UNAUTHORIZED
            )
            else "invalid_credentials"
        )
        return RedirectResponse(
            url=f"/?error={error_message}",
            status_code=status.HTTP_302_FOUND,
        )
