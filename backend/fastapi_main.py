from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from routes.router_auth import router_auth
from routes.router_register import router_register
from routes.router_page import router_home
from database.database import create_db_and_tables

from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(router_auth)
app.include_router(router_register)
app.include_router(router_home)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/token")
 