import json
import os
from datetime import datetime

TEST_RUNS_DIR = '/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/test_runs'
RUNS_DIR = os.path.join(TEST_RUNS_DIR, 'runs')
INDEX_FILE = os.path.join(TEST_RUNS_DIR, 'index.json')

def scan_test_runs():
    runs = []
    
    if not os.path.exists(RUNS_DIR):
        print(f"Directory not found: {RUNS_DIR}")
        return

    print(f"Scanning {RUNS_DIR}...")
    
    files = os.listdir(RUNS_DIR)
    json_files = [f for f in files if f.endswith('.json')]
    
    print(f"Found {len(json_files)} JSON files.")

    for filename in json_files:
        filepath = os.path.join(RUNS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Basic validation - check if it looks like a test run
                if not isinstance(data, dict):
                    print(f"Skipping {filename}: Not a dictionary")
                    continue
                
                # Extract essential fields for the index, using defaults if missing
                run_entry = {
                    "timestamp": data.get("timestamp", datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()),
                    "scenario_name": data.get("scenario_name", "Unknown Scenario"),
                    "status": data.get("status", "unknown"),
                    "duration": data.get("duration", 0),
                    "filename": filename,
                    "stats": data.get("stats", {})
                }
                
                # If specific note exists
                if "duration_note" in data:
                    run_entry["duration_note"] = data["duration_note"]
                    
                runs.append(run_entry)
                print(f"Processed {filename}")
                
        except json.JSONDecodeError:
            print(f"Error decoding {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Sort by timestamp descending
    runs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    print(f"Total valid runs: {len(runs)}")
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(runs, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {INDEX_FILE}")

if __name__ == "__main__":
    scan_test_runs()
