from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .routers import auth, sockets, admin_api
from .database import init_db
from .config import settings
from .seed import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    seed_data()
    yield
    # Shutdown

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Routers
app.include_router(auth.router)
app.include_router(sockets.router)
app.include_router(admin_api.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "IRIS Login"})
