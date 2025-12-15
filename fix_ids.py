import json
import re

def fix_duplicates(filename, prefix):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        items = data.get('issues') or data.get('tests') or data.get('definitions') or []
        if not items:
            print(f"No items in {filename}")
            return

        seen_ids = set()
        duplicates = []
        all_ids = []
        
        # Check for duplicates
        for item in items:
            iid = item['id']
            if iid in seen_ids:
                duplicates.append(item)
            else:
                seen_ids.add(iid)
            all_ids.append(iid)
            
        if not duplicates:
            print(f"No duplicates in {filename}")
            return # Nothing to do

        print(f"Found {len(duplicates)} duplicates in {filename}. Renumbering...")
        
        # Find max ID
        max_num = 0
        for iid in all_ids:
            match = re.search(f"{prefix}-(\d+)", iid)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        
        # Renumber duplicates
        for item in duplicates:
            max_num += 1
            old_id = item['id']
            new_id = f"{prefix}-{max_num:03d}"
            item['id'] = new_id
            print(f"Renamed {old_id} to {new_id}")

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False) # ensure_ascii=False for Czech chars
            
    except Exception as e:
        print(f"Error processing {filename}: {e}")

fix_duplicates('/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/issues.json', 'ISS')
fix_duplicates('/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/tests.json', 'TEST')
fix_duplicates('/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/definitions.json', 'DEF')
