from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .routers import auth, sockets, admin_api, translations, docs
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
        last_load = -1
        last_treasury = -1
        last_overload = False
        
        while True:
            await asyncio.sleep(1)
            
            # 0. Check for agent response timeouts
            import time
            current_time = time.time()
            timeout_window = gamestate.agent_response_window
            
            # Copy keys to avoid modification during iteration
            pending_sessions = list(routing_logic.pending_responses.keys())
            for session_id in pending_sessions:
                start_time = routing_logic.pending_responses.get(session_id)
                if start_time and (current_time - start_time) >= timeout_window:
                    # Timeout occurred - send error to user and block agent
                    await routing_logic.send_timeout_error_to_user(session_id)
                    await routing_logic.send_timeout_to_agent(session_id)
                    routing_logic.mark_session_timeout(session_id)
            
            # 1. Tick Chernobyl
            new_val = gamestate.process_tick()
            
            # 2. Calc Load
            counts = routing_logic.get_active_counts()
            is_low_latency = gamestate.agent_response_window <= 30
            current_load = gamestate.calc_load(
                active_terminals=counts["users"],
                active_autopilots=counts["autopilots"],
                low_latency_active=is_low_latency
            )
            
            # 3. Check Overload
            is_overloaded = gamestate.check_overload()
            
            # 4. Broadcast
            # Detect changes (Optimization: only send if changed)
            if (int(new_val) != int(last_val) or 
                current_load != last_load or 
                gamestate.treasury_balance != last_treasury or
                is_overloaded != last_overload):
                
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update",
                    "temperature": new_val,
                    "shift": gamestate.global_shift_offset,
                    "power_load": current_load,
                    "power_capacity": gamestate.power_capacity,
                    "treasury": gamestate.treasury_balance,
                    "is_overloaded": is_overloaded,
                    "agent_window": gamestate.agent_response_window,
                    "hyper_mode": gamestate.hyper_visibility_mode.value
                }))
                
                last_val = new_val
                last_load = current_load
                last_treasury = gamestate.treasury_balance
                last_overload = is_overloaded
                
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
app.include_router(translations.router)
app.include_router(docs.router)

@app.get("/")
async def root(request: Request):
    # Test Mode Logic
    from .logic.gamestate import gamestate
    from .database import SessionLocal, User
    
    users = []
    if gamestate.test_mode:
        db = SessionLocal()
        users = db.query(User).order_by(User.role, User.username).all()
        db.close()
        
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "title": "IRIS Login",
        "test_mode": gamestate.test_mode,
        "users": users
    })
