from src.routes import auth, new_content, page, register

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from src.db.database import create_db_and_tables
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(auth.router_auth)
app.include_router(register.router_register)
app.include_router(page.router_home)
app.include_router(new_content.router_new_content)

"""
Mounts the "/static" route to serve static files from the specified directory.

- The directory "src/static" contains static resources (CSS and HTML).
- The name "static" is used to reference this route in the app.
"""
app.mount("/static", StaticFiles(directory="src/static"), name="static")


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
