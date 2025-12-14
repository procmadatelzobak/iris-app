"""
Documentation Router - Serves markdown manuals and documentation
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated
import os
import re
from pathlib import Path

from .. import dependencies, database

router = APIRouter(prefix="/docs", tags=["documentation"])
templates = Jinja2Templates(directory="app/templates")

# Base paths for documentation
DOCS_BASE = Path(__file__).parent.parent.parent.parent / "docs"
MANUALS_PATH = DOCS_BASE / "manuals"
IRIS_DOCS_PATH = DOCS_BASE / "iris"
IMAGES_PATH = DOCS_BASE / "images"

# Role to manual file mapping
ROLE_MANUAL_MAP = {
    database.UserRole.USER: "PRIRUCKA_UZIVATEL.md",
    database.UserRole.AGENT: "PRIRUCKA_AGENT.md",
    database.UserRole.ADMIN: "PRIRUCKA_SPRAVCE.md",
}

def convert_md_to_html(md_content: str) -> str:
    """Convert markdown to simple HTML without external dependencies"""
    html = md_content
    
    # Escape HTML entities first (except for our conversions)
    html = html.replace('&', '&amp;')
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    
    # Convert headers
    html = re.sub(r'^######\s+(.+)$', r'<h6 class="text-sm font-bold mt-4 mb-2">\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5 class="text-base font-bold mt-4 mb-2">\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4 class="text-lg font-bold mt-4 mb-2">\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3 class="text-xl font-bold mt-6 mb-3">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2 class="text-2xl font-bold mt-8 mb-4 border-b border-current pb-2">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1 class="text-3xl font-bold mb-6">\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code class="bg-black/50 px-1 rounded">\1</code>', html)
    
    # Convert code blocks
    html = re.sub(r'```(\w+)?\n([\s\S]*?)```', r'<pre class="bg-black/50 p-4 rounded my-4 overflow-x-auto"><code>\2</code></pre>', html)
    
    # Convert images - update path to use our docs image endpoint
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="/docs/images/\2" alt="\1" class="max-w-full my-4 border border-current rounded">', html)
    
    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="underline hover:opacity-80">\1</a>', html)
    
    # Convert horizontal rules
    html = re.sub(r'^---+$', r'<hr class="my-8 border-current opacity-30">', html, flags=re.MULTILINE)
    
    # Convert tables
    lines = html.split('\n')
    in_table = False
    table_lines = []
    result_lines = []
    
    for line in lines:
        if '|' in line and not in_table:
            in_table = True
            table_lines = [line]
        elif '|' in line and in_table:
            table_lines.append(line)
        elif in_table and '|' not in line:
            # End of table
            result_lines.append(convert_table(table_lines))
            in_table = False
            table_lines = []
            result_lines.append(line)
        else:
            result_lines.append(line)
    
    if in_table:
        result_lines.append(convert_table(table_lines))
    
    html = '\n'.join(result_lines)
    
    # Convert blockquotes (including admonitions)
    html = re.sub(r'^\&gt; \[!CAUTION\]\s*\n(\&gt; .+\n?)+', lambda m: convert_admonition(m.group(0), 'caution'), html, flags=re.MULTILINE)
    html = re.sub(r'^\&gt; \[!WARNING\]\s*\n(\&gt; .+\n?)+', lambda m: convert_admonition(m.group(0), 'warning'), html, flags=re.MULTILINE)
    html = re.sub(r'^\&gt; \[!NOTE\]\s*\n(\&gt; .+\n?)+', lambda m: convert_admonition(m.group(0), 'note'), html, flags=re.MULTILINE)
    html = re.sub(r'^\&gt; (.+)$', r'<blockquote class="border-l-4 border-current pl-4 my-4 opacity-80">\1</blockquote>', html, flags=re.MULTILINE)
    
    # Convert unordered lists
    html = re.sub(r'^- (.+)$', r'<li class="ml-4">\1</li>', html, flags=re.MULTILINE)
    
    # Convert numbered lists
    html = re.sub(r'^\d+\. (.+)$', r'<li class="ml-4">\1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive list items
    html = re.sub(r'(<li[^>]*>.*?</li>\n)+', lambda m: '<ul class="my-4 list-disc">' + m.group(0) + '</ul>', html)
    
    # Convert paragraphs (lines with content that aren't already wrapped)
    lines = html.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.startswith('|'):
            result.append(f'<p class="my-2">{line}</p>')
        else:
            result.append(line)
    
    return '\n'.join(result)


def convert_table(lines: list) -> str:
    """Convert markdown table to HTML"""
    if len(lines) < 2:
        return '\n'.join(lines)
    
    html = '<table class="w-full my-4 border-collapse">'
    
    for i, line in enumerate(lines):
        # Skip separator line
        if re.match(r'^\|[-:|]+\|$', line.strip()):
            continue
        
        cells = [c.strip() for c in line.split('|')[1:-1]]
        tag = 'th' if i == 0 else 'td'
        row_class = 'bg-black/30' if i == 0 else ''
        cell_class = 'border border-current/30 p-2'
        
        html += f'<tr class="{row_class}">'
        for cell in cells:
            html += f'<{tag} class="{cell_class}">{cell}</{tag}>'
        html += '</tr>'
    
    html += '</table>'
    return html


def convert_admonition(text: str, type_: str) -> str:
    """Convert GitHub-style admonitions to styled divs"""
    colors = {
        'caution': 'border-red-500 bg-red-900/20',
        'warning': 'border-yellow-500 bg-yellow-900/20',
        'note': 'border-blue-500 bg-blue-900/20'
    }
    icons = {
        'caution': '⚠️',
        'warning': '⚠️',
        'note': 'ℹ️'
    }
    
    # Remove > prefix and type marker
    content = re.sub(r'^\&gt; \[!\w+\]\s*\n?', '', text)
    content = re.sub(r'^\&gt; ', '', content, flags=re.MULTILINE)
    
    return f'''<div class="border-l-4 {colors.get(type_, "")} p-4 my-4 rounded-r">
        <div class="font-bold mb-2">{icons.get(type_, "")} {type_.upper()}</div>
        <div>{content}</div>
    </div>'''


def get_theme_class(role: database.UserRole, username: str = "") -> dict:
    """Get theme colors based on user role"""
    if username == "root":
        return {
            "bg": "bg-gray-900",
            "text": "text-yellow-500",
            "border": "border-yellow-500",
            "accent": "text-yellow-300"
        }
    
    themes = {
        database.UserRole.USER: {
            "bg": "bg-gray-900",
            "text": "text-green-500",
            "border": "border-green-500",
            "accent": "text-green-300"
        },
        database.UserRole.AGENT: {
            "bg": "bg-gray-900",
            "text": "text-pink-500",
            "border": "border-pink-500",
            "accent": "text-pink-300"
        },
        database.UserRole.ADMIN: {
            "bg": "bg-gray-900",
            "text": "text-red-500",
            "border": "border-red-500",
            "accent": "text-red-300"
        },
    }
    return themes.get(role, themes[database.UserRole.USER])


@router.get("/manual", response_class=HTMLResponse)
async def get_user_manual(
    request: Request,
    current_user: Annotated[database.User, Depends(dependencies.get_current_user_cookie)]
):
    """Get the manual appropriate for the current user's role"""
    
    # Root gets ROOT manual
    if current_user.username == "root":
        manual_file = "PRIRUCKA_ROOT.md"
    else:
        manual_file = ROLE_MANUAL_MAP.get(current_user.role, "PRIRUCKA_UZIVATEL.md")
    
    manual_path = MANUALS_PATH / manual_file
    
    if not manual_path.exists():
        raise HTTPException(status_code=404, detail=f"Manual not found: {manual_file}")
    
    with open(manual_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = convert_md_to_html(md_content)
    theme = get_theme_class(current_user.role, current_user.username)
    
    return templates.TemplateResponse("docs/manual_viewer.html", {
        "request": request,
        "title": "Uživatelská příručka",
        "content": html_content,
        "theme": theme,
        "user": current_user
    })


@router.get("/system", response_class=HTMLResponse)
async def get_system_docs(
    request: Request,
    current_user: Annotated[database.User, Depends(dependencies.get_current_user_cookie)]
):
    """Get full system documentation (admin/root only)"""
    
    # Check permissions
    if current_user.role != database.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied - Admin only")
    
    # Build documentation index
    docs_index = []
    
    # Add manuals
    docs_index.append({"title": "Uživatelské příručky", "type": "section"})
    for file in sorted(MANUALS_PATH.glob("*.md")):
        docs_index.append({
            "title": file.stem.replace("_", " "),
            "path": f"manuals/{file.name}",
            "type": "file"
        })
    
    # Add IRIS documentation
    if IRIS_DOCS_PATH.exists():
        docs_index.append({"title": "IRIS Systém - Lore", "type": "section"})
        for folder in sorted(IRIS_DOCS_PATH.glob("*")):
            if folder.is_dir():
                docs_index.append({
                    "title": folder.name.replace("_", " "),
                    "path": f"iris/{folder.name}",
                    "type": "folder"
                })
    
    theme = get_theme_class(current_user.role, current_user.username)
    
    return templates.TemplateResponse("docs/system_docs.html", {
        "request": request,
        "title": "Dokumentace systému",
        "docs_index": docs_index,
        "theme": theme,
        "user": current_user
    })


@router.get("/view/{doc_path:path}", response_class=HTMLResponse)
async def view_document(
    request: Request,
    doc_path: str,
    current_user: Annotated[database.User, Depends(dependencies.get_current_user_cookie)]
):
    """View a specific documentation file"""
    
    # Only admins can view arbitrary docs
    if current_user.role != database.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied - Admin only")
    
    # Sanitize path to prevent directory traversal
    doc_path = doc_path.replace("..", "")
    full_path = DOCS_BASE / doc_path
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not full_path.suffix == ".md":
        raise HTTPException(status_code=400, detail="Only markdown files can be viewed")
    
    with open(full_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = convert_md_to_html(md_content)
    theme = get_theme_class(current_user.role, current_user.username)
    
    return templates.TemplateResponse("docs/manual_viewer.html", {
        "request": request,
        "title": full_path.stem.replace("_", " "),
        "content": html_content,
        "theme": theme,
        "user": current_user
    })


@router.get("/images/{image_path:path}")
async def get_doc_image(image_path: str):
    """Serve documentation images"""
    
    # Sanitize path
    image_path = image_path.replace("..", "")
    full_path = IMAGES_PATH / image_path
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Check extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
    if full_path.suffix.lower() not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    return FileResponse(full_path)
