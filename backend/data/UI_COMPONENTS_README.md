# 🎨 UI Component Database - Catalog

## Overview

The UI component database contains **125 high-quality GitHub repositories** (stars > 500) categorized into 10 distinct categories. These are pre-scraped UI libraries, component collections, and design resources that AI agents can use to build interfaces.

---

## 📊 Categories

### 1. **Component Libraries** (11 repos)
Pre-built component libraries like shadcn/ui, DaisyUI, Radix, etc.

**Top Components:**
- **shadcn-ui/ui** (96,240 ⭐) - Beautifully-designed, accessible components. Works with React, Vue, Svelte
- **saadeghi/daisyui** (38,885 ⭐) - Most popular Tailwind CSS component library
- **tailwindlabs/headlessui** (28,011 ⭐) - Unstyled, accessible UI components for Tailwind
- **magicuidesign/magicui** (19,126 ⭐) - Animated components for design engineers
- **radix-ui/primitives** (17,964 ⭐) - High-quality, accessible design system primitives

**Use Cases:** Pre-built buttons, forms, modals, dropdowns, navigation, cards

---

### 2. **CSS Frameworks** (5 repos)
Tailwind, Bootstrap, and other CSS frameworks

**Top Frameworks:**
- **tailwindlabs/tailwindcss** (90,474 ⭐) - Utility-first CSS framework
- **tabler/tabler** (40,146 ⭐) - Free HTML Dashboard UI Kit (Bootstrap)
- **froala/design-blocks** (13,774 ⭐) - 170+ Bootstrap design blocks
- **troxler/awesome-css-frameworks** (8,922 ⭐) - List of CSS frameworks

**Use Cases:** Styling systems, utility classes, responsive grids

---

### 3. **React UI** (3 repos)
React-specific component libraries and UI kits

**Top Libraries:**
- **brillout/awesome-react-components** (45,720 ⭐) - Curated list of React components
- **tremorlabs/tremor-npm** (16,448 ⭐) - React components for charts and dashboards
- **tremorlabs/tremor** (2,978 ⭐) - Copy & paste React components

**Use Cases:** React dashboards, data visualization, modern web apps

---

### 4. **Vue UI** (1 repo)
Vue.js component libraries

**Top Library:**
- **vuejs/awesome-vue** (73,290 ⭐) - Curated list of Vue.js resources

**Use Cases:** Vue component discovery, ecosystem tools

---

### 5. **Dashboards/Templates** (8 repos)
Dashboard templates, admin panels, and boilerplates

**Top Templates:**
- **h5bp/html5-boilerplate** (57,180 ⭐) - Professional front-end template
- **pure-admin/vue-pure-admin** (18,973 ⭐) - Vue3 + Vite admin system
- **cobiwave/simplefolio** (13,989 ⭐) - Minimal portfolio template

**Use Cases:** Admin panels, SaaS dashboards, portfolio sites

---

### 6. **Charts & Graphs** (15 repos)
Data visualization, flowcharts, diagrams

**Top Libraries:**
- **excalidraw/excalidraw** (108,093 ⭐) - Virtual whiteboard for sketching diagrams
- **mermaid-js/mermaid** (83,302 ⭐) - Generate diagrams from text
- **chartjs/Chart.js** (66,609 ⭐) - Simple HTML5 charts
- **xyflow/xyflow** (31,834 ⭐) - React/Svelte flow diagram library

**Use Cases:** Analytics dashboards, workflow editors, data viz

---

### 7. **Forms & Inputs** (3 repos)
Form builders, validation, input components

**Top Tools:**
- **vantezzen/autoform** (3,407 ⭐) - Auto-render forms from schema
- **jsonresume/resume-schema** (2,289 ⭐) - JSON schema for resumes

**Use Cases:** Dynamic forms, validation, schema-based UIs

---

### 8. **Icons & Assets** (1 repo)
Icon sets and visual assets

**Top Library:**
- **fabricjs/fabric.js** (30,458 ⭐) - Javascript canvas library, SVG parser

**Use Cases:** Canvas manipulation, SVG handling

---

### 9. **Animation** (1 repo)
Animation libraries and motion effects

**Top Library:**
- **dubinc/dub** (22,409 ⭐) - Modern link attribution platform

**Use Cases:** Smooth transitions, micro-interactions

---

### 10. **Other** (77 repos)
Awesome lists, general development resources, and uncategorized gems

Includes: awesome-python, awesome-go, awesome-selfhosted, three.js, and more

---

## 🔍 How Agents Use This

AI agents can search the UI catalog using the **MCP UI Component Tool**:

```json
{
  "tool_name": "ui-component",
  "args": {
    "query": "dashboard",
    "component_type": "dashboards",  // Optional category filter
    "limit": 5
  }
}
```

### Search Examples:

1. **Find Tailwind components:**
   ```
   query: "component", component_type: "component_libraries"
   ```

2. **Find React charts:**
   ```
   query: "chart", component_type: "react_ui"
   ```

3. **Find dashboards:**
   ```
   query: "admin", component_type: "dashboards"
   ```

---

## 📦 Database Schema

### `ui_catalog` table:
- **full_name** - GitHub repo name (e.g., "shadcn-ui/ui")
- **category** - Component category (e.g., "component_libraries")
- **description** - Repo description
- **stars** - GitHub stars (quality indicator)
- **files** - JSON array of repo files
- **readme** - Repository README
- **ai_description** - AI-generated description
- **stencil_patterns** - Reusable code patterns (JSON)
- **tweaked_variants** - Component variants (JSON)
- **github_url** - Full GitHub URL

---

## 🚀 Agent Recommendations

### Building a Dashboard:
1. Search `component_libraries` for "dashboard"
2. Search `charts_graphs` for "chart"
3. Use `tailwindlabs/tailwindcss` for styling

### Building a Landing Page:
1. Search `component_libraries` for "hero" or "landing"
2. Search `dashboards` for templates
3. Use `shadcn-ui/ui` for components

### Building a Form:
1. Search `forms_inputs` for "form"
2. Use `vantezzen/autoform` for schema-based forms
3. Add validation with React Hook Form

---

## 📊 Statistics

- **Total Repos:** 125
- **Quality Filter:** Stars > 500
- **Top Repo:** sindresorhus/awesome (405,061 ⭐)
- **Most Components:** Component Libraries (11)
- **Most Charts:** Charts & Graphs (15)

---

## 🔧 Files

- **Database:** `db-cleaning/raw_themes.db`
- **Categorized Table:** `ui_catalog`
- **JSON Catalog:** `backend/data/ui_catalog.json`
- **Manager:** `backend/agents/ui_component_manager.py`
- **MCP Tool:** `backend/mcp_servers.py` (line 571)

---

Generated by old.new UI Categorization System
Last Updated: 2025-10-10
