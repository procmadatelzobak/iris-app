#!/usr/bin/env python3
"""
IRIS Lore-Web Feature Sync Script
Automatically extracts features from FEATURE_LIST.md and TEST_LOGS.md
and generates a JSON file for the Lore-Web frontend.

Usage:
    python tools/sync_features_to_web.py
"""

import json
import re
from pathlib import Path
from datetime import datetime


def parse_feature_list(content: str) -> list[dict]:
    """
    Parse FEATURE_LIST.md and extract features with their status.
    
    Returns a list of feature dictionaries.
    """
    features = []
    current_category = ""
    current_subcategory = ""
    feature_id_counter = 0
    
    # Category to role mapping
    category_role_map = {
        "core features": "All",
        "user features": "User",
        "agent features": "Agent",
        "admin features": "Admin",
        "root features": "Root",
        "ai features": "AI",
        "ui/ux features": "All",
        "developer features": "Developer",
        "power & performance": "System",
    }
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Match H2 headers (## 1. Core Features)
        h2_match = re.match(r'^##\s+(?:\d+\.\s+)?(.+)$', line)
        if h2_match:
            current_category = h2_match.group(1).strip()
            current_subcategory = ""
            continue
        
        # Match H3 headers (### Authentication & Authorization)
        h3_match = re.match(r'^###\s+(.+)$', line)
        if h3_match:
            current_subcategory = h3_match.group(1).strip()
            continue
        
        # Match feature list items (- ✅ Feature name: description)
        # Handle lines like: "- ✅ JWT-based authentication"
        # or "- ✅ **Feature Name**: Description"
        feature_match = re.match(r'^-\s*(✅|⚠️|❌|🔄)?\s*(.+)$', line)
        if feature_match and current_category and current_category != "Table of Contents":
            status_icon = feature_match.group(1) or ""
            full_text = feature_match.group(2).strip()
            
            # Parse name and description
            # Patterns: "**Name**: Description" or "Name: Description" or just "Name"
            name_desc_match = re.match(r'^\*\*(.+?)\*\*:?\s*(.*)$', full_text)
            if name_desc_match:
                name = name_desc_match.group(1).strip()
                description = name_desc_match.group(2).strip()
            else:
                # Try simple colon split
                if ':' in full_text:
                    parts = full_text.split(':', 1)
                    name = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = full_text
                    description = ""
            
            # Clean up name (remove any remaining bold markers)
            name = re.sub(r'\*\*', '', name).strip()
            
            # Determine status
            if status_icon == "✅":
                status = "DONE"
            elif status_icon == "⚠️":
                status = "PARTIAL"
            elif status_icon == "❌":
                status = "TODO"
            elif status_icon == "🔄":
                status = "IN_PROGRESS"
            else:
                status = "TODO"
            
            # Determine role from category
            category_lower = current_category.lower()
            role = "All"
            for key, value in category_role_map.items():
                if key in category_lower:
                    role = value
                    break
            
            # Generate feature ID
            feature_id_counter += 1
            feature_id = f"feat_{feature_id_counter:03d}"
            
            # Create subcategory display name
            subcategory_display = current_subcategory if current_subcategory else current_category
            
            features.append({
                "id": feature_id,
                "category": current_category,
                "subcategory": subcategory_display,
                "role": role,
                "name": name,
                "description": description if description else name,
                "status": status,
                "test_status": None  # Will be filled later
            })
    
    return features


def parse_test_logs(content: str) -> dict:
    """
    Parse TEST_LOGS.md and extract test results.
    
    Returns a dictionary mapping keywords to test results.
    """
    test_results = {}
    
    # Parse automated tests table
    table_pattern = r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*\*\*?(PASS|FAIL|Not Run)\*?\*?\s*\|\s*([^|]*)\s*\|'
    
    for match in re.finditer(table_pattern, content):
        date = match.group(1)
        test_suite = match.group(2).strip()
        scope = match.group(3).strip()
        result = match.group(4).strip()
        notes = match.group(5).strip()
        
        # Extract keywords from scope for matching
        keywords = scope.lower().split()
        
        for keyword in keywords:
            if len(keyword) > 3:  # Skip short words
                test_results[keyword] = {
                    "last_test_date": date,
                    "test_result": result,
                    "test_type": "Automated" if "py" in test_suite else "Manual",
                    "test_suite": test_suite,
                    "notes": notes
                }
    
    # Parse manual verification items
    manual_pattern = r'-\s*\[(x| )\]\s*\*\*([^*]+)\*\*:\s*(.+)'
    for match in re.finditer(manual_pattern, content):
        checked = match.group(1) == 'x'
        item_name = match.group(2).strip()
        description = match.group(3).strip()
        
        keywords = item_name.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:
                test_results[keyword] = {
                    "last_test_date": None,
                    "test_result": "PASS" if checked else "PENDING",
                    "test_type": "Manual",
                    "test_suite": "Manual Verification",
                    "notes": description
                }
    
    return test_results


def match_tests_to_features(features: list[dict], test_results: dict) -> list[dict]:
    """
    Match test results to features based on keyword matching.
    """
    for feature in features:
        feature_keywords = (feature["name"] + " " + feature["description"]).lower().split()
        
        matched_test = None
        for keyword in feature_keywords:
            if keyword in test_results:
                matched_test = test_results[keyword]
                break
        
        if matched_test:
            if matched_test["test_result"] == "PASS":
                feature["test_status"] = f"Automated - PASS"
            elif matched_test["test_result"] == "FAIL":
                feature["test_status"] = f"Automated - FAIL"
            elif matched_test["test_result"] == "PENDING":
                feature["test_status"] = f"Manual - Pending"
            else:
                feature["test_status"] = f"{matched_test['test_type']} - {matched_test['test_result']}"
        else:
            # Default test status based on implementation status
            if feature["status"] == "DONE":
                feature["test_status"] = "Untested"
            else:
                feature["test_status"] = None
    
    return features


def main():
    """Main function to run the sync process."""
    # Define paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    feature_list_path = repo_root / "IRIS_LARP" / "docs" / "FEATURE_LIST.md"
    test_logs_path = repo_root / "docs" / "TEST_LOGS.md"
    output_path = repo_root / "doc" / "iris" / "lore-web" / "data" / "features.json"
    
    print(f"📂 Repository root: {repo_root}")
    print(f"📄 Feature list: {feature_list_path}")
    print(f"📄 Test logs: {test_logs_path}")
    print(f"📤 Output: {output_path}")
    print()
    
    # Read feature list
    if not feature_list_path.exists():
        print(f"❌ Error: Feature list not found at {feature_list_path}")
        return 1
    
    with open(feature_list_path, 'r', encoding='utf-8') as f:
        feature_content = f.read()
    
    # Parse features
    print("🔍 Parsing FEATURE_LIST.md...")
    features = parse_feature_list(feature_content)
    print(f"   Found {len(features)} features")
    
    # Read test logs (optional)
    test_results = {}
    if test_logs_path.exists():
        print("🔍 Parsing TEST_LOGS.md...")
        with open(test_logs_path, 'r', encoding='utf-8') as f:
            test_content = f.read()
        test_results = parse_test_logs(test_content)
        print(f"   Found {len(test_results)} test entries")
    else:
        print(f"⚠️  Test logs not found at {test_logs_path}, skipping test matching")
    
    # Match tests to features
    if test_results:
        print("🔗 Matching test results to features...")
        features = match_tests_to_features(features, test_results)
    
    # Generate statistics
    stats = {
        "total": len(features),
        "done": sum(1 for f in features if f["status"] == "DONE"),
        "partial": sum(1 for f in features if f["status"] == "PARTIAL"),
        "todo": sum(1 for f in features if f["status"] == "TODO"),
        "in_progress": sum(1 for f in features if f["status"] == "IN_PROGRESS"),
    }
    
    # Create output structure
    output = {
        "generated_at": datetime.now().isoformat(),
        "source": "IRIS_LARP/docs/FEATURE_LIST.md",
        "statistics": stats,
        "features": features
    }
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    print(f"💾 Writing {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print()
    print("✅ Sync complete!")
    print(f"   📊 Statistics:")
    print(f"      Total features: {stats['total']}")
    print(f"      ✅ Done: {stats['done']}")
    print(f"      ⚠️  Partial: {stats['partial']}")
    print(f"      ❌ TODO: {stats['todo']}")
    print(f"      🔄 In Progress: {stats['in_progress']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
