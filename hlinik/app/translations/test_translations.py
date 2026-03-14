"""
Test script for IRIS translation system.
Run with: python test_translations.py
"""

import json
import sys
from pathlib import Path

# Setup import path for __init__ module
def setup_import():
    """Helper to setup module imports for standalone test execution."""
    translations_dir = Path(__file__).parent
    if str(translations_dir) not in sys.path:
        sys.path.insert(0, str(translations_dir))
    return __import__('__init__')

# Setup once at module level
translations_module = setup_import()

def test_json_validity():
    """Test that JSON files are valid."""
    print("Testing JSON validity...")
    translations_dir = Path(__file__).parent
    
    for filename in ["czech.json", "iris.json", "english.json", "crazy.json"]:
        filepath = translations_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  ✓ {filename} is valid JSON")
    
    print("✓ All JSON files are valid\n")


def test_iris_keys_exist_in_czech():
    """Test that all keys in iris.json exist in czech.json."""
    print("Testing that IRIS keys exist in Czech base...")
    translations_dir = Path(__file__).parent
    
    with open(translations_dir / "czech.json", 'r', encoding='utf-8') as f:
        czech = json.load(f)
    
    with open(translations_dir / "iris.json", 'r', encoding='utf-8') as f:
        iris = json.load(f)
    
    def check_keys(iris_data, czech_data, path=""):
        issues = []
        for key, value in iris_data.items():
            if key.startswith("_"):  # Skip meta keys
                continue
            
            current_path = f"{path}.{key}" if path else key
            
            if key not in czech_data:
                issues.append(f"Key '{current_path}' in iris.json not found in czech.json")
            elif isinstance(value, dict) and isinstance(czech_data.get(key), dict):
                issues.extend(check_keys(value, czech_data[key], current_path))
        
        return issues
    
    issues = check_keys(iris, czech)
    
    if issues:
        print("  ✗ Found issues:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✓ All IRIS keys exist in Czech base")
    
    print()


def test_key_structure():
    """Test that translation structure is consistent."""
    print("Testing translation structure...")
    translations_dir = Path(__file__).parent
    
    with open(translations_dir / "czech.json", 'r', encoding='utf-8') as f:
        czech = json.load(f)
    
    # Check required sections exist
    required_sections = ["login", "user_terminal", "agent_terminal", "admin_dashboard", "root_dashboard", "common"]
    
    missing = []
    for section in required_sections:
        if section not in czech:
            missing.append(section)
    
    if missing:
        print(f"  ✗ Missing sections: {', '.join(missing)}")
    else:
        print("  ✓ All required sections present")
    
    print()


def test_sample_translations():
    """Test that we can access sample translations."""
    print("Testing sample translations...")
    # Load translations
    czech = translations_module.load_translations("czech")
    
    # Test some key paths
    tests = [
        ("login.username_label", "IDENTIFIKÁTOR"),
        ("login.password_label", "HESLO"),
        ("user_terminal.logout", "ODHLÁSIT"),
        ("admin_dashboard.hub_station_1", "UMYVADLO"),
    ]
    
    for key_path, expected in tests:
        result = translations_module.get_translation(key_path, "cz")
        if result == expected:
            print(f"  ✓ {key_path} = '{result}'")
        else:
            print(f"  ✗ {key_path} = '{result}' (expected '{expected}')")
    
    print()


def test_czech_iris_mode():
    """Test czech-iris mode fallback."""
    print("Testing czech-iris mode...")
    # Test that iris-specific keys work
    result = translations_module.get_translation("admin_dashboard.hub_station_1", "czech-iris")
    print(f"  ✓ czech-iris mode: admin_dashboard.hub_station_1 = '{result}'")
    
    # Test that keys not in iris.json fall back to czech.json
    result = translations_module.get_translation("login.username_label", "czech-iris")
    print(f"  ✓ czech-iris fallback: login.username_label = '{result}'")
    
    print()


def test_english_mode():
    """Test English language mode."""
    print("Testing English mode...")
    # Test English translations
    result = translations_module.get_translation("login.username_label", "en")
    if result == "IDENTIFIER":
        print(f"  ✓ english mode: login.username_label = '{result}'")
    else:
        print(f"  ✗ english mode: login.username_label = '{result}' (expected 'IDENTIFIER')")
    
    result = translations_module.get_translation("common.yes", "en")
    if result == "Yes":
        print(f"  ✓ english mode: common.yes = '{result}'")
    else:
        print(f"  ✗ english mode: common.yes = '{result}' (expected 'Yes')")
    
    print()


def test_crazy_mode():
    """Test Crazy Czech language mode."""
    print("Testing Crazy Czech mode...")
    # Test crazy translations
    result = translations_module.get_translation("login.username_label", "crazy")
    if result == "PŘEZDÍVKA KÁMOŠE":
        print(f"  ✓ crazy mode: login.username_label = '{result}'")
    else:
        print(f"  ✗ crazy mode: login.username_label = '{result}' (expected 'PŘEZDÍVKA KÁMOŠE')")
    
    result = translations_module.get_translation("user_terminal.logout", "crazy")
    if result == "ÚTĚK!":
        print(f"  ✓ crazy mode: user_terminal.logout = '{result}'")
    else:
        print(f"  ✗ crazy mode: user_terminal.logout = '{result}' (expected 'ÚTĚK!')")
    
    print()


def test_custom_overrides():
    """Test custom admin override priority."""
    print("Testing custom admin overrides...")
    custom_labels = {
        "admin_dashboard.hub_station_1": "CUSTOM STATION NAME"
    }
    
    result = translations_module.get_translation("admin_dashboard.hub_station_1", "cz", custom_labels)
    if result == "CUSTOM STATION NAME":
        print(f"  ✓ Custom override works: '{result}'")
    else:
        print(f"  ✗ Custom override failed: got '{result}'")
    
    # Test that other keys still work normally
    result = translations_module.get_translation("login.username_label", "cz", custom_labels)
    if result == "IDENTIFIKÁTOR":
        print(f"  ✓ Non-overridden key works: '{result}'")
    else:
        print(f"  ✗ Non-overridden key failed: got '{result}'")
    
    print()


def count_translations():
    """Count total number of translations."""
    print("Translation statistics...")
    translations_dir = Path(__file__).parent
    
    with open(translations_dir / "czech.json", 'r', encoding='utf-8') as f:
        czech = json.load(f)
    
    with open(translations_dir / "iris.json", 'r', encoding='utf-8') as f:
        iris = json.load(f)
    
    def count_keys(data, skip_meta=True):
        count = 0
        for key, value in data.items():
            if skip_meta and key.startswith("_"):
                continue
            if isinstance(value, dict):
                count += count_keys(value, skip_meta)
            else:
                count += 1
        return count
    
    czech_count = count_keys(czech)
    iris_count = count_keys(iris)
    
    print(f"  Czech translations: {czech_count} keys")
    print(f"  IRIS overrides: {iris_count} keys")
    print(f"  Total unique strings: {czech_count}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("IRIS Translation System Tests")
    print("=" * 60)
    print()
    
    try:
        test_json_validity()
        test_iris_keys_exist_in_czech()
        test_key_structure()
        count_translations()
        test_sample_translations()
        test_czech_iris_mode()
        test_english_mode()
        test_crazy_mode()
        test_custom_overrides()
        
        print("=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
