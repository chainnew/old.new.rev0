import sqlite3
import json

conn = sqlite3.connect('raw_themes.db')
cursor = conn.cursor()

# First, let's check what tables exist in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables in database: {[table[0] for table in tables]}")

# Check the structure of the themes table
if ('themes',) in tables:
    cursor.execute("PRAGMA table_info(themes);")
    columns = cursor.fetchall()
    print(f"Columns in themes table: {[col[1] for col in columns]}")
    
    # Get the actual column names
    column_names = [col[1] for col in columns]
    
    # Build the SELECT query with actual column names
    select_query = f"SELECT {', '.join(column_names)} FROM themes"
    
    # Fetch all rows
    cursor.execute(select_query)
    rows = cursor.fetchall()
    
    # Create a mapping of column names to indices
    col_index = {col: idx for idx, col in enumerate(column_names)}
    
    # Transform to structured list
    data = []
    for row in rows:
        # Try to access columns by name, handling potential missing columns
        repo = row[col_index.get('repo', 0)] if 'repo' in col_index else row[0]
        desc = row[col_index.get('description', 1)] if 'description' in col_index else row[1] if len(row) > 1 else ""
        stars = row[col_index.get('stars', 2)] if 'stars' in col_index else row[2] if len(row) > 2 else 0
        contents_str = row[col_index.get('contents', 3)] if 'contents' in col_index else row[3] if len(row) > 3 else "[]"
        
        try:
            # Parse the contents JSON string from DB (it's a stringified array)
            contents = json.loads(contents_str) if contents_str else []
        except json.JSONDecodeError:
            # Handle any malformed JSON (from scraping errors)—set to empty
            contents = []
            print(f"Warning: Skipped invalid JSON for {repo}")
        
        data.append({
            "repo": repo,
            "description": desc,
            "stars": int(stars) if stars else 0,  # Ensure int
            "contents": contents
            # Add extras if you query more cols: e.g., "url": f"https://github.com/{repo}"
        })
    
    # Write to file
    with open('themes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)  # indent for readability; set to 0 for compact
    
    print(f"Exported {len(data)} themes to themes.json")
else:
    print("Error: 'themes' table not found in the database")

conn.close()
