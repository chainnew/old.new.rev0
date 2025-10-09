import json

# Load full dataset and enriched entry
with open('full_themes.json', 'r') as f:
    themes = json.load(f)

with open('enriched_entry.json', 'r') as f:
    enriched = json.load(f)

# Find and replace matching entry (case-insensitive)
enriched_name = enriched['full_name'].lower()
for i, theme in enumerate(themes):
    if theme['full_name'].lower() == enriched_name:
        print(f"Updating {enriched_name} with enriched data...")
        themes[i] = enriched  # Merge: enriched overwrites
        break
else:
    print(f"No match for {enriched_name}—appending.")
    themes.append(enriched)

# Optional: Enrich others lightly (e.g., just update stars if you have API keys/multiple entries)
# For now, save
with open('super_themes.json', 'w', encoding='utf-8') as f:
    json.dump(themes, f, indent=0, ensure_ascii=False)  # Compact for agents

print(f"Merged! Total entries: {len(themes)}. Output: super_themes.json")
