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

"""
Mounts the "/static" route to serve static files from the specified directory.

- The directory "backend/static" contains static resources (e.g., CSS, JS, images).
- The name "static" is used to reference this route in the app.
"""
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


@app.on_event("startup")
def on_startup():
    """
    Initializes the application during startup.

    This function is triggered when the application starts. It ensures that
    the database schema is created by invoking `create_db_and_tables()`.
    """
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
async def root() -> RedirectResponse:
    """
    Redirects the root URL ("/") to the login page.

    Returns:
        RedirectResponse: A response that redirects users to the "/token" route.
    """
    return RedirectResponse(url="/token")
