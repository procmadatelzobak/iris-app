from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import markdown
import os
from ..dependencies import get_current_user_cookie
from ..database import User, UserRole

router = APIRouter(prefix="/doc", tags=["docs"])
templates = Jinja2Templates(directory="app/templates")

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs")

def get_manual_path(doc_key: str) -> str:
    mapping = {
        "user": "manual_user.md",
        "agent": "manual_agent.md",
        "admin": "manual_admin.md",
        "root": "manual_admin.md", # Root shares admin manual
        "system": "README.md" # System docs = README (for now, or ARCHITEKTURA.md)
    }
    filename = mapping.get(doc_key)
    if not filename:
        return None
    return os.path.join(DOCS_DIR, filename)

@router.get("/view/{doc_key}", response_class=HTMLResponse)
async def view_documentation(request: Request, doc_key: str, current_user: User = Depends(get_current_user_cookie)):
    # Security check: Only Admin can see 'system' docs
    if doc_key == "system" and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access Denied")
    
    # Access check: Users shouldn't see Admin manual
    if doc_key in ["admin", "root"] and current_user.role != UserRole.ADMIN:
         raise HTTPException(status_code=403, detail="Access Denied")

    file_path = get_manual_path(doc_key)
    if not file_path or not os.path.exists(file_path):
        # Fallback for system docs if README missing
        if doc_key == "system":
             file_path = os.path.join(DOCS_DIR, "ARCHITEKTURA.md")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Documentation not found")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Pre-process image links to point to /static/docs/images or similar?
    # Actually, if we serve /docs/images statically, we can just replace relative paths.
    # But for now, let's assume the markdown has `/docs/images/...` and we mount that path.
    # OR we replace `/docs/images` with a route.
    # Implementation Plan said "Create docs/images". We need to mount StaticFiles for it or serve it.
    # Let's check main.py later. For now, render HTML.

    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables'])

    theme = "green" # Default user
    if current_user.role == UserRole.AGENT:
        theme = "pink"
    elif current_user.role == UserRole.ADMIN:
        theme = "gold"

    return templates.TemplateResponse("doc_viewer.html", {
        "request": request, 
        "content": html_content,
        "title": f"Manual: {doc_key.upper()}",
        "theme": theme
    })
