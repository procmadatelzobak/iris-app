"""
Lore Editor API - CRUD operations for lore-web JSON files.
Provides endpoints for managing users, tasks, relations, and other JSON data.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import re
import os

from ..dependencies import get_current_admin
from ..config import BASE_DIR

router = APIRouter(prefix="/api/lore-editor", tags=["lore-editor"])

# Path to lore-web data directory
LORE_DATA_DIR = BASE_DIR.parent / "doc" / "iris" / "lore-web" / "data"

# Editable JSON files configuration
EDITABLE_FILES = {
    "users": {"file": "users.json", "key": "users", "id_field": "id", "display_field": "obcanske_jmeno"},
    "tasks": {"file": "tasks.json", "key": "tasks", "id_field": "id", "display_field": "nazev"},
    "relations": {"file": "relations_v2.json", "key": "relations", "id_field": "id", "display_field": "nazev"},
    "abilities": {"file": "abilities.json", "key": "abilities", "id_field": "id", "display_field": "nazev"},
    "task_types": {"file": "task_types.json", "key": "types", "id_field": "id", "display_field": "nazev"},
    "relation_types": {"file": "relation_types.json", "key": "types", "id_field": "id", "display_field": "nazev"},
    "story_nodes": {"file": "story_nodes.json", "key": "nodes", "id_field": "id", "display_field": "title"},
    "roles": {"file": "roles.json", "key": "roles", "id_field": "id", "display_field": "nazev"},
    "config": {"file": "config.json", "key": None, "id_field": None, "display_field": None},  # Single object
}

# Reference patterns for smart dropdowns
REFERENCE_PATTERNS = {
    r"^U\d+$": {"source": "users", "display": "obcanske_jmeno"},
    r"^A\d+$": {"source": "users", "display": "obcanske_jmeno"},
    r"^S\d+$": {"source": "users", "display": "obcanske_jmeno"},
    r"^T\d+$": {"source": "tasks", "display": "nazev"},
    r"^R\d+$": {"source": "relations", "display": "nazev"},
    r"^TT\d+$": {"source": "task_types", "display": "nazev"},
    r"^RT\d+$": {"source": "relation_types", "display": "nazev"},
    r"^AB\d+$": {"source": "abilities", "display": "nazev"},
}


def _get_file_path(file_key: str) -> Path:
    """Get absolute path for a file key."""
    if file_key not in EDITABLE_FILES:
        raise HTTPException(status_code=404, detail=f"Unknown file: {file_key}")
    return LORE_DATA_DIR / EDITABLE_FILES[file_key]["file"]


def _read_json(file_key: str) -> dict:
    """Read and parse a JSON file."""
    path = _get_file_path(file_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path.name}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {path.name}: {e}")


def _write_json(file_key: str, data: dict) -> None:
    """Write data to a JSON file."""
    path = _get_file_path(file_key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write {path.name}: {e}")


def _get_records(file_key: str) -> List[dict]:
    """Get all records from a file."""
    config = EDITABLE_FILES[file_key]
    data = _read_json(file_key)
    if config["key"]:
        return data.get(config["key"], [])
    return [data]  # Single object file


def _find_record(file_key: str, record_id: str) -> Optional[dict]:
    """Find a record by ID."""
    config = EDITABLE_FILES[file_key]
    records = _get_records(file_key)
    id_field = config["id_field"]
    if not id_field:
        return records[0] if records else None
    for record in records:
        if record.get(id_field) == record_id:
            return record
    return None


def _find_all_references(target_id: str) -> List[Dict[str, str]]:
    """Find all references to an ID across all files."""
    references = []
    
    for file_key in EDITABLE_FILES:
        try:
            records = _get_records(file_key)
            config = EDITABLE_FILES[file_key]
            
            for record in records:
                record_id = record.get(config["id_field"], "?")
                refs = _search_dict_for_value(record, target_id)
                for ref_path in refs:
                    references.append({
                        "file": file_key,
                        "record_id": record_id,
                        "field": ref_path
                    })
        except:
            continue  # Skip files that can't be read
    
    return references


def _search_dict_for_value(obj, target, path="") -> List[str]:
    """Recursively search a dict/list for a value, return paths where found."""
    found = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            found.extend(_search_dict_for_value(value, target, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if item == target:
                found.append(f"{path}[{i}]")
            elif isinstance(item, (dict, list)):
                found.extend(_search_dict_for_value(item, target, f"{path}[{i}]"))
    elif obj == target:
        found.append(path)
    
    return found


def _generate_next_id(file_key: str) -> str:
    """Generate the next available ID for a file."""
    config = EDITABLE_FILES[file_key]
    records = _get_records(file_key)
    id_field = config["id_field"]
    
    if not id_field:
        return None
    
    # Extract numeric suffix from existing IDs
    max_num = 0
    prefix = ""
    for record in records:
        rid = record.get(id_field, "")
        match = re.match(r"^([A-Z]+)(\d+)$", rid)
        if match:
            prefix = match.group(1)
            num = int(match.group(2))
            if num > max_num:
                max_num = num
    
    if not prefix:
        # Fallback prefix based on file type
        prefixes = {"users": "U", "tasks": "T", "relations": "R", "abilities": "AB", 
                    "task_types": "TT", "relation_types": "RT", "story_nodes": "SN"}
        prefix = prefixes.get(file_key, "X")
    
    return f"{prefix}{str(max_num + 1).zfill(2)}"


# ============================================
# API ENDPOINTS
# ============================================

@router.get("/files")
async def list_files(admin=Depends(get_current_admin)):
    """List all editable JSON files."""
    files = []
    for key, config in EDITABLE_FILES.items():
        path = LORE_DATA_DIR / config["file"]
        files.append({
            "key": key,
            "filename": config["file"],
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
            "display_field": config["display_field"],
            "id_field": config["id_field"]
        })
    return {"files": files}


@router.get("/file/{file_key}")
async def get_file(file_key: str, admin=Depends(get_current_admin)):
    """Get all content of a JSON file."""
    data = _read_json(file_key)
    config = EDITABLE_FILES[file_key]
    
    # Add record count for array-based files
    records = _get_records(file_key)
    
    return {
        "file_key": file_key,
        "config": config,
        "data": data,
        "record_count": len(records)
    }


@router.put("/file/{file_key}")
async def save_file(file_key: str, data: dict = Body(...), admin=Depends(get_current_admin)):
    """Save entire file content (bulk update)."""
    _write_json(file_key, data)
    return {"status": "saved", "file_key": file_key}


@router.get("/file/{file_key}/records")
async def list_records(file_key: str, admin=Depends(get_current_admin)):
    """List all records with ID and display field only (for selection)."""
    config = EDITABLE_FILES[file_key]
    records = _get_records(file_key)
    
    id_field = config["id_field"]
    display_field = config["display_field"]
    
    summaries = []
    for record in records:
        summaries.append({
            "id": record.get(id_field, "?"),
            "label": record.get(display_field, record.get(id_field, "?")),
        })
    
    return {"file_key": file_key, "records": summaries}


@router.get("/file/{file_key}/record/{record_id}")
async def get_record(file_key: str, record_id: str, admin=Depends(get_current_admin)):
    """Get a single record by ID."""
    record = _find_record(file_key, record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record not found: {record_id}")
    return {"file_key": file_key, "record_id": record_id, "record": record}


@router.put("/file/{file_key}/record/{record_id}")
async def update_record(file_key: str, record_id: str, record_data: dict = Body(...), admin=Depends(get_current_admin)):
    """Update a single record."""
    config = EDITABLE_FILES[file_key]
    data = _read_json(file_key)
    id_field = config["id_field"]
    key = config["key"]
    
    if not key:
        # Single object file - just replace
        _write_json(file_key, record_data)
        return {"status": "updated", "record_id": record_id}
    
    records = data.get(key, [])
    found = False
    for i, rec in enumerate(records):
        if rec.get(id_field) == record_id:
            records[i] = record_data
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail=f"Record not found: {record_id}")
    
    data[key] = records
    _write_json(file_key, data)
    return {"status": "updated", "record_id": record_id}


@router.post("/file/{file_key}/record")
async def create_record(file_key: str, record_data: dict = Body(...), admin=Depends(get_current_admin)):
    """Create a new record."""
    config = EDITABLE_FILES[file_key]
    data = _read_json(file_key)
    key = config["key"]
    id_field = config["id_field"]
    
    if not key:
        raise HTTPException(status_code=400, detail="Cannot create records in single-object files")
    
    # Auto-generate ID if not provided
    if id_field and not record_data.get(id_field):
        record_data[id_field] = _generate_next_id(file_key)
    
    records = data.get(key, [])
    
    # Check for duplicate ID
    new_id = record_data.get(id_field)
    if new_id:
        for rec in records:
            if rec.get(id_field) == new_id:
                raise HTTPException(status_code=400, detail=f"Duplicate ID: {new_id}")
    
    records.append(record_data)
    data[key] = records
    _write_json(file_key, data)
    
    return {"status": "created", "record_id": record_data.get(id_field)}


@router.delete("/file/{file_key}/record/{record_id}")
async def delete_record(file_key: str, record_id: str, force: bool = False, admin=Depends(get_current_admin)):
    """Delete a record. Fails if references exist unless force=True."""
    config = EDITABLE_FILES[file_key]
    data = _read_json(file_key)
    key = config["key"]
    id_field = config["id_field"]
    
    if not key:
        raise HTTPException(status_code=400, detail="Cannot delete from single-object files")
    
    # Check for references
    if not force:
        refs = _find_all_references(record_id)
        # Exclude self-references
        refs = [r for r in refs if not (r["file"] == file_key and r["record_id"] == record_id)]
        if refs:
            return JSONResponse(
                status_code=409,
                content={
                    "status": "blocked",
                    "reason": "Record is referenced elsewhere",
                    "references": refs
                }
            )
    
    records = data.get(key, [])
    original_len = len(records)
    records = [r for r in records if r.get(id_field) != record_id]
    
    if len(records) == original_len:
        raise HTTPException(status_code=404, detail=f"Record not found: {record_id}")
    
    data[key] = records
    _write_json(file_key, data)
    return {"status": "deleted", "record_id": record_id}


@router.get("/references/{target_id}")
async def find_references(target_id: str, admin=Depends(get_current_admin)):
    """Find all references to an ID across all files."""
    refs = _find_all_references(target_id)
    return {"target_id": target_id, "count": len(refs), "references": refs}


@router.get("/options/{pattern}")
async def get_options_for_pattern(pattern: str, admin=Depends(get_current_admin)):
    """Get dropdown options for a field pattern (e.g., 'U*' for users)."""
    # Match pattern to source
    for regex, config in REFERENCE_PATTERNS.items():
        if re.match(regex.replace("\\d+", ".*"), pattern.replace("*", "")):
            source = config["source"]
            display = config["display"]
            records = _get_records(source)
            source_config = EDITABLE_FILES[source]
            
            options = []
            for rec in records:
                options.append({
                    "value": rec.get(source_config["id_field"]),
                    "label": rec.get(display, rec.get(source_config["id_field"]))
                })
            return {"pattern": pattern, "source": source, "options": options}
    
    return {"pattern": pattern, "source": None, "options": []}


@router.get("/schema/{file_key}")
async def get_schema(file_key: str, admin=Depends(get_current_admin)):
    """Auto-detect schema from first record in file."""
    records = _get_records(file_key)
    if not records:
        return {"file_key": file_key, "schema": {}}
    
    sample = records[0]
    schema = _infer_schema(sample)
    return {"file_key": file_key, "schema": schema}


def _infer_schema(obj, path="") -> Dict[str, Any]:
    """Infer field types from a sample object."""
    schema = {}
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            field_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict):
                schema[key] = {"type": "object", "fields": _infer_schema(value, field_path)}
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    schema[key] = {"type": "array_objects", "item_schema": _infer_schema(value[0], field_path)}
                elif value and isinstance(value[0], str):
                    # Check if it looks like a reference
                    sample_val = value[0]
                    ref_type = _detect_reference_type(sample_val)
                    schema[key] = {"type": "array_string", "ref": ref_type}
                else:
                    schema[key] = {"type": "array"}
            elif isinstance(value, str):
                ref_type = _detect_reference_type(value)
                if ref_type:
                    schema[key] = {"type": "reference", "ref": ref_type}
                elif len(value) > 100:
                    schema[key] = {"type": "text"}
                else:
                    schema[key] = {"type": "string"}
            elif isinstance(value, int):
                schema[key] = {"type": "integer"}
            elif isinstance(value, float):
                schema[key] = {"type": "number"}
            elif isinstance(value, bool):
                schema[key] = {"type": "boolean"}
            else:
                schema[key] = {"type": "unknown"}
    
    return schema


def _detect_reference_type(value: str) -> Optional[str]:
    """Detect if a string value looks like a reference ID."""
    for regex, config in REFERENCE_PATTERNS.items():
        if re.match(regex, value):
            return config["source"]
    return None
