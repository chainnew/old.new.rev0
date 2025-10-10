# 🎨 UI Component Database - Agent Instructions

## What Agents Need to Know

You have access to **218 production-quality UI components** from top repositories:
- shadcn/ui (50 components)
- Tremor (40 dashboard/chart components)
- Radix UI (30 accessible primitives)
- Vercel Commerce (25 e-commerce components)
- HeadlessUI (15 Tailwind components)
- And 7 more repos

## How to Use Components

### 1. Query the Database

**Database Location:** `backend/data/ui_components.db`

**Simple Queries:**

```sql
-- Get all buttons
SELECT name, code, github_url FROM components WHERE category='buttons' LIMIT 5;

-- Get Tailwind components with dark mode
SELECT name, category, code FROM components
WHERE has_tailwind=1 AND has_dark_mode=1 LIMIT 10;

-- Get responsive navigation components
SELECT name, code, github_url FROM components
WHERE category='navigation' AND is_responsive=1;

-- Get TypeScript React components
SELECT name, code FROM components
WHERE framework='react-ts' AND has_typescript=1 LIMIT 5;

-- Get chart components (for dashboards)
SELECT name, code FROM components WHERE category='charts';
```

### 2. Available Categories

- `buttons` - Button components (7 components)
- `forms` - Input, select, textarea, etc. (14 components)
- `navigation` - Nav, menu, sidebar (18 components)
- `cards` - Card layouts (6 components)
- `modals` - Dialogs, popups (8 components)
- `data` - Tables, grids (4 components)
- `charts` - Visualizations (8 components)
- `feedback` - Alerts, toasts (2 components)
- `loading` - Spinners, skeletons (2 components)
- `other` - Misc components (149 components)

### 3. Component Metadata

Each component includes:
```python
{
    "name": "Button",
    "category": "buttons",
    "code": "export function Button() { ... }",  // Full source code
    "framework": "react-ts",
    "file_size": 1234,
    "line_count": 45,

    # Feature flags (simple regex detection)
    "has_typescript": true,
    "has_tailwind": true,
    "has_props": true,
    "is_responsive": true,
    "has_dark_mode": true,
    "has_animation": false,

    "repo": "shadcn-ui/ui",
    "github_url": "https://github.com/shadcn-ui/ui/blob/main/..."
}
```

## When Building UI

### Step 1: Check Database First
**Before generating UI from scratch**, check if we have a similar component:

```python
# Example: User wants a pricing table
import sqlite3

conn = sqlite3.connect('backend/data/ui_components.db')
cursor = conn.cursor()

# Search for pricing/table components
cursor.execute("""
    SELECT name, code, github_url
    FROM components
    WHERE (name LIKE '%pricing%' OR name LIKE '%table%' OR category='data')
    AND has_tailwind=1
    LIMIT 5
""")

components = cursor.fetchall()
```

### Step 2: Adapt, Don't Reinvent
If you find a matching component:
1. Use its code as a foundation
2. Adapt it to project needs
3. Credit the source repo
4. Modify styling/props as needed

### Step 3: Combine Components
Build complex UIs by combining simple components:

```python
# Dashboard = Nav + Cards + Charts
nav = query("SELECT code FROM components WHERE category='navigation' LIMIT 1")
cards = query("SELECT code FROM components WHERE category='cards' LIMIT 3")
charts = query("SELECT code FROM components WHERE category='charts' LIMIT 2")

# Combine into dashboard layout
```

## Quality Filters

### Get High-Quality Components
```sql
-- Tailwind + TypeScript + Responsive
SELECT * FROM components
WHERE has_tailwind=1
  AND has_typescript=1
  AND is_responsive=1;

-- Production-ready (from top repos)
SELECT * FROM components
WHERE repo IN ('shadcn-ui/ui', 'tremorlabs/tremor', 'radix-ui/primitives');

-- Dark mode support
SELECT * FROM components WHERE has_dark_mode=1;
```

## Framework Support

### React (TypeScript)
```sql
SELECT * FROM components WHERE framework='react-ts' LIMIT 20;
-- Returns 204 components
```

### Vue
```sql
SELECT * FROM components WHERE framework='vue' LIMIT 10;
-- Returns 14 components
```

## Example Workflows

### Building a Landing Page
```sql
-- 1. Hero section
SELECT code FROM components WHERE name LIKE '%hero%' OR category='other' LIMIT 1;

-- 2. Features section (cards)
SELECT code FROM components WHERE category='cards' LIMIT 3;

-- 3. Navigation
SELECT code FROM components WHERE category='navigation' AND is_responsive=1 LIMIT 1;

-- 4. Forms (contact/signup)
SELECT code FROM components WHERE category='forms' LIMIT 3;
```

### Building a Dashboard
```sql
-- 1. Sidebar navigation
SELECT code FROM components WHERE category='navigation' AND name LIKE '%sidebar%';

-- 2. Chart components
SELECT code FROM components WHERE category='charts';

-- 3. Data tables
SELECT code FROM components WHERE category='data';

-- 4. Cards for stats
SELECT code FROM components WHERE category='cards' AND has_tailwind=1;
```

### Building a Form
```sql
-- Get all form components
SELECT name, code FROM components WHERE category='forms';

-- Responsive forms with validation
SELECT code FROM components
WHERE category='forms'
  AND is_responsive=1
  AND has_typescript=1;
```

## Best Practices

### 1. Always Check Database First
Don't generate UI from scratch if we have production-quality components.

### 2. Use Production Code
Components from shadcn/ui, Tremor, Radix are battle-tested and accessible.

### 3. Combine and Adapt
Mix components from different sources to build complete UIs.

### 4. Credit Sources
When using a component, add a comment:
```typescript
// Adapted from shadcn-ui/ui
// https://github.com/shadcn-ui/ui/blob/main/...
```

### 5. Filter by Quality
Prefer components with:
- `has_tailwind=1` (modern styling)
- `has_typescript=1` (type safety)
- `is_responsive=1` (mobile-friendly)
- `has_dark_mode=1` (theme support)

## Cost Optimization

Using existing components = **$0.00 cost**
- No AI reasoning needed
- No code generation
- Just database queries
- Copy/paste/adapt

Generating from scratch = **$5-10 per component** (with reasoning)

**Always prefer database components!**

## Quick Reference

```python
# Python helper function
def get_components(category=None, framework='react-ts', limit=10):
    import sqlite3
    conn = sqlite3.connect('backend/data/ui_components.db')
    cursor = conn.cursor()

    query = "SELECT name, code, github_url FROM components WHERE framework=?"
    params = [framework]

    if category:
        query += " AND category=?"
        params.append(category)

    query += " LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    return cursor.fetchall()

# Usage
buttons = get_components(category='buttons', limit=5)
charts = get_components(category='charts', framework='react-ts')
```

## Summary

- **218 components ready to use**
- **Database:** `backend/data/ui_components.db`
- **Cost:** $0.00 (vs $5-10 per generated component)
- **Quality:** Production-tested from top repos
- **Speed:** Instant lookup vs minutes of generation

**Use the database first, generate only if needed!**
