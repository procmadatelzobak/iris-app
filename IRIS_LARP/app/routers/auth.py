from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Annotated
from .. import dependencies, database

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

from fastapi.responses import HTMLResponse, JSONResponse

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(dependencies.get_db)):
    user = db.query(database.User).filter(database.User.username == form_data.username).first()
    if not user or not dependencies.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = dependencies.create_access_token(data={"sub": user.username, "role": user.role.value})
    
    # Server-side cookie setting for robust session management
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer", "role": user.role.value})
    # HTTPOnly=False because we might need JS to read it? 
    # Actually, login.html uses localStorage for WS. 
    # But get_current_user_cookie needs it. 
    # Let's use httponly=False so JS can sync if needed, but path=/ is key.
    response.set_cookie(key="access_token", value=access_token, httponly=False, path="/")
    return response

@router.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request, "title": "IRIS Login"})
    # Must match path set in login
    response.delete_cookie("access_token", path="/")
    return response

@router.get("/terminal", response_class=HTMLResponse)
async def terminal(request: Request, current_user: Annotated[database.User, Depends(dependencies.get_current_user_cookie)]):
    # Route to correct template based on role
    if current_user.role == database.UserRole.USER:
        return templates.TemplateResponse("user_terminal.html", {"request": request, "user": current_user})
    elif current_user.role == database.UserRole.AGENT:
         return templates.TemplateResponse("agent_terminal.html", {"request": request, "user": current_user})
    elif current_user.role == database.UserRole.ADMIN:
        if current_user.username == "root":
             return templates.TemplateResponse("admin/root_dashboard.html", {"request": request, "user": current_user})
        return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": current_user})
    
    raise HTTPException(status_code=400, detail="Unknown Role")

@router.get("/me")
async def read_users_me(current_user: Annotated[database.User, Depends(dependencies.get_current_user)]):
    return {
        "username": current_user.username, 
        "role": current_user.role, 
        "id": current_user.id,
        "session_id_bound": current_user.id if current_user.role == database.UserRole.USER else None 
    }
