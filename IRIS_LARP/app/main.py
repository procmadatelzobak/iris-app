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
    
    # Background Task
    import asyncio
    from .logic.gamestate import gamestate
    from .logic.routing import routing_logic
    import json
    
    async def game_loop():
        last_val = -1
        while True:
            await asyncio.sleep(1)
            new_val = gamestate.process_tick()
            
            # Broadcast if changed (or regularly to sync? Let's do change only + 10s sync?)
            # Just change for now to save bandwidth
            if int(new_val) != int(last_val):
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update",
                    "chernobyl": new_val,
                    "shift": gamestate.global_shift_offset
                }))
                last_val = new_val
                
    task = asyncio.create_task(game_loop())
    yield
    # Shutdown
    task.cancel()

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
