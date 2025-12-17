import json

def migrate_timeline():
    with open('timeline.json', 'r') as f:
        timeline = json.load(f)

    nodes = []
    for event in timeline:
        phase_id = f"PH{event['phase']:02d}"
        
        # Combine actors and target_actors for "uzivatele"
        users = event.get('actors', [])
        if 'target_actors' in event:
            users.extend(event['target_actors'])
        # Unique users
        users = sorted(list(set(users)))

        node = {
            "id": event['id'],
            "nazev": event['title'],
            "popis": event['description'], # Using description for short desc
            "dlouhy_popis": event['description'], # And also for long desc for now
            "uzivatele": users,
            "faze": phase_id,
            "cas_start": event['time_start'],
            "trvani": event['duration'],
            "typ": event['type'],
            "kontext": event.get('related_nodes', [])
        }
        nodes.append(node)

    with open('story_nodes.json', 'w') as f:
        json.dump({"nodes": nodes}, f, indent=4, ensure_ascii=False)
    
    print(f"Migrated {len(nodes)} nodes to story_nodes.json")

if __name__ == "__main__":
    migrate_timeline()
