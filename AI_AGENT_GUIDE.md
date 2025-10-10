# 🤖 AI Agent System - Complete Guide

## Overview

The HECTIC SWARM system uses **grok-orc** as the main AI agent that users interact with. It operates in two modes:

1. **Simple Code Generation** - For single files, small changes, and questions
2. **Swarm Creation** - For complex projects requiring the AI Planner and multiple agents

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                           │                                  │
│                           ↓                                  │
│              ┌────────────────────────┐                      │
│              │    GROK-4-ORC          │                      │
│              │  (Master Orchestrator) │                      │
│              └────────────────────────┘                      │
│                    │              │                          │
│        ┌───────────┴────┐    ┌───┴──────────────┐          │
│        │                │    │                   │          │
│        ↓                ↓    ↓                   ↓          │
│   MODE 1              MODE 2                                │
│   Simple Code         Swarm Creation                        │
│        │                │                                    │
│        ↓                ↓                                    │
│  ┌─────────┐      ┌──────────────────┐                     │
│  │ Direct  │      │  AI Planner      │                     │
│  │ Code    │      │  (3 main areas)  │                     │
│  │ Output  │      └──────────────────┘                     │
│  └─────────┘             │                                   │
│                          ↓                                   │
│              ┌───────────────────────┐                      │
│              │  3 Specialized Agents  │                      │
│              ├───────────────────────┤                      │
│              │ 1. Frontend Architect │                      │
│              │ 2. Backend Integrator │                      │
│              │ 3. Deployment Guardian│                      │
│              └───────────────────────┘                      │
│                          │                                   │
│                          ↓                                   │
│              ┌───────────────────────┐                      │
│              │  Generated Code       │                      │
│              │  → Code Window        │                      │
│              └───────────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

## Mode 1: Simple Code Generation

### When It Activates

grok-orc uses **Mode 1** when the user requests:
- Single component or file
- Code explanations or help
- Small fixes or modifications
- Programming questions
- Simple utilities or functions

### How It Works

1. User sends message to grok-orc
2. grok-orc analyzes request
3. Determines it's a simple request
4. Generates code **directly** with proper filenames
5. Code appears in **Code Window** automatically

### Code Format Requirements

**CRITICAL**: All code MUST include filenames using one of these 3 formats:

#### Format 1: Inline Comment (Preferred)

```markdown
## Button Component
```tsx // src/components/Button.tsx
export function Button({ children }: { children: React.ReactNode }) {
  return <button className="btn">{children}</button>;
}
```
```

#### Format 2: Heading Before Code Block

```markdown
Create `src/components/Card.tsx`:
```tsx
export function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}
```
```

#### Format 3: File Comment Inside Code

```markdown
```typescript
// File: src/utils/helpers.ts
export function formatDate(date: Date): string {
  return date.toISOString();
}
```
```

### Example Interactions

**User**: "Create a React button component"

**grok-orc Response**:
```markdown
## Button Component

Here's a reusable button component with TypeScript:

```tsx // src/components/Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
}

export function Button({ children, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
}
```

Usage:
```tsx
<Button variant="primary" onClick={() => alert('Clicked!')}>
  Click Me
</Button>
```
```

**Result**:
- Code extracted automatically
- File created: `src/components/Button.tsx`
- Appears in Code Window under "🤖 AI Generated" folder
- Automatically saved to disk

## Mode 2: Swarm Creation (AI Planner)

### When It Activates

grok-orc uses **Mode 2** (creates swarm) when request contains:

✅ **Trigger Keywords**:
- "build", "create app", "full-stack", "project", "system", "platform"

✅ **Multiple Features**:
- "with auth and database"
- "user management and payment processing"

✅ **Project Description**:
- Request longer than 2 sentences with requirements

✅ **Technical Mentions**:
- database, authentication, deployment, multiple pages
- API, backend, frontend together

### How It Works

1. User describes complex project
2. grok-orc detects complexity triggers
3. Outputs special **SWARM_CREATE_REQUEST** format
4. Backend creates swarm with 3 agents
5. **AI Planner** breaks down into 12 tasks (3 areas × 4 subtasks)
6. User redirected to `/planner/[swarmId]`
7. Agents generate code in parallel
8. All code appears in Code Window

### Swarm Creation Format

When grok-orc detects a complex project, it responds with:

```markdown
**SWARM_CREATE_REQUEST**
```json
{
  "action": "create_swarm",
  "user_message": "[original user message verbatim]",
  "project_type": "full_stack_app",
  "complexity": "high"
}
```

I'm creating an AI swarm with 3 specialized agents to handle your project:
- 🎨 Frontend Architect (UI/UX)
- ⚙️ Backend Integrator (APIs/Database)
- 🚀 Deployment Guardian (Testing/CI-CD)

They'll break this down in the AI Planner and generate all the code. One moment...
```

### AI Planner Breakdown

The swarm creates **12 tasks** organized in **3 main areas**:

#### Area 1: Frontend & UI (4 subtasks)
1. Component architecture and routing
2. UI components with Shadcn
3. State management setup
4. Responsive design implementation

#### Area 2: Middleware & Integration (4 subtasks)
5. API routes setup
6. Authentication integration
7. Form validation with Zod
8. Error handling

#### Area 3: Backend & Hosting (4 subtasks)
9. Database schema (Prisma)
10. API endpoints
11. Testing setup
12. Deployment configuration

### Example Interactions

**User**: "Build a todo app with Next.js, PostgreSQL database, and user authentication"

**grok-orc Response**:
```markdown
**SWARM_CREATE_REQUEST**
```json
{
  "action": "create_swarm",
  "user_message": "Build a todo app with Next.js, PostgreSQL database, and user authentication",
  "project_type": "full_stack_app",
  "complexity": "high"
}
```

I'm creating an AI swarm with 3 specialized agents to handle your project:
- 🎨 Frontend Architect (UI/UX)
- ⚙️ Backend Integrator (APIs/Database)
- 🚀 Deployment Guardian (Testing/CI-CD)

They'll break this down in the AI Planner and generate all the code. One moment...
```

**Result**:
- Swarm created in backend database
- User sees success message with link to planner
- Can click "Open Planner" to see `/planner/[swarmId]`
- 12 tasks visible with status (pending → in_progress → completed)
- All generated code appears in Code Window

## The 3 Specialized Agents

### 1. Frontend Architect 🎨

**Responsibilities**:
- UI/UX design and implementation
- Component architecture
- Responsive layouts
- Accessibility
- Visual polish

**Tools Used**:
- MCP Code-Gen (AI code generation)
- MCP Browser (research UI patterns)

**Generates**:
- React/Next.js components (`.tsx` files)
- Page layouts
- Tailwind CSS configurations
- UI component libraries

### 2. Backend Integrator ⚙️

**Responsibilities**:
- API development
- Database integration
- Business logic
- Data validation
- Authentication logic

**Tools Used**:
- MCP Code-Gen (API generation)
- MCP DB-Sync (database operations)

**Generates**:
- API routes (`.ts` files)
- Database schemas (`schema.prisma`)
- Validation schemas (Zod)
- API documentation

### 3. Deployment Guardian 🚀

**Responsibilities**:
- Testing setup
- CI/CD pipelines
- Deployment configuration
- Environment management
- Error monitoring

**Tools Used**:
- MCP Code-Gen (config generation)
- MCP Communication (coordinate deploys)

**Generates**:
- GitHub Actions workflows (`.yml`)
- Docker configurations
- Environment files (`.env.example`)
- Test files

## Code Output Flow

### How Code Reaches the Code Window

```
grok-orc (Mode 1) or Agent (Mode 2)
    │
    ↓
Generates markdown with code blocks
    │
    ↓
Frontend receives response
    │
    ↓
CodeActionPanel extracts code
    │
    ├─> extractCodeBlocks() finds filenames
    │   • Format 1: Inline comment
    │   • Format 2: Heading
    │   • Format 3: File comment
    │   • Fallback: generated-0.tsx
    │
    ↓
addGeneratedFile() adds to context
    │
    ↓
CodeWindow receives update
    │
    ↓
File appears in "🤖 AI Generated" folder
    │
    ↓
Auto-opens in editor tab
```

### Automatic File Creation

When code is generated:

1. **Extracted**: CodeActionPanel parses markdown
2. **Displayed**: Added to Code Window file tree
3. **Saved**: API call to `/api/create-files`
4. **Persisted**: Files written to disk

Files appear in project at the specified path (e.g., `src/components/Button.tsx`)

## Debugging

### Console Logs to Watch

When code generation happens, check browser console (F12) for:

```
🔍 Code blocks extracted: 3
  [0] src/components/Button.tsx (tsx) - 245 chars
  [1] src/components/Card.tsx (tsx) - 312 chars
  [2] src/utils/helpers.ts (typescript) - 189 chars

📤 Sending files to CodeWindow: 3
  ✅ Adding file 1/3: src/components/Button.tsx
  ✅ Adding file 2/3: src/components/Card.tsx
  ✅ Adding file 3/3: src/utils/helpers.ts

🔥 CodeSyncContext: Adding file to state: src/components/Button.tsx
  📊 Total files in state: 1

🔄 CodeWindow: generatedFiles changed 1 files
📂 Opening latest file: src/components/Button.tsx
  ✨ Creating new tab: src/components/Button.tsx
```

### Common Issues

#### Issue 1: Code Not Appearing in Code Window

**Symptom**: AI generates code but it doesn't show in the code editor

**Check**:
1. Open browser console (F12)
2. Look for extraction logs
3. Verify filename was detected

**Fix**:
- Ensure AI used one of the 3 filename formats
- Check if code blocks have language tags (```tsx, ```typescript)
- Verify CodeWindow panel is open (click <Code2> button)

#### Issue 2: Swarm Not Created

**Symptom**: Complex request but no swarm created

**Check**:
1. Did response include `SWARM_CREATE_REQUEST`?
2. Check browser console for errors
3. Verify backend is running on port 8000

**Fix**:
- Ensure request has complexity triggers
- Check backend logs: `tail -f logs/api-server.log`
- Verify database connection

#### Issue 3: Generic Filenames (generated-0.tsx)

**Symptom**: Files have names like "generated-0.tsx" instead of proper names

**Cause**: AI didn't include filename in response

**Fix**:
- This is a fallback mechanism
- Code still works but needs manual renaming
- Re-prompt AI: "Name that file properly as src/components/Button.tsx"

## Best Practices

### For Simple Code (Mode 1)

✅ **DO**:
- Request one component/file at a time
- Be specific about file location
- Ask for TypeScript types
- Request error handling

❌ **DON'T**:
- Ask for entire apps in Mode 1
- Mix multiple unrelated files
- Skip filename specifications

### For Complex Projects (Mode 2)

✅ **DO**:
- Describe full project scope
- Mention all major features
- Specify database/auth needs
- Let swarm break it down

❌ **DON'T**:
- Make request too vague
- Ask for single files (use Mode 1)
- Interrupt swarm creation

## Testing the System

### Test Mode 1 (Simple Code)

Send this message:
```
Create a TypeScript function to validate email addresses
```

**Expected**:
- Single file generated
- Filename: `src/utils/validateEmail.ts` or similar
- Appears in Code Window immediately

### Test Mode 2 (Swarm)

Send this message:
```
Build a blog platform with:
- User authentication
- Create/edit/delete posts
- Comments system
- PostgreSQL database
- Next.js frontend
```

**Expected**:
- SWARM_CREATE_REQUEST JSON appears
- Success message with swarm ID
- Link to planner: `/planner/[swarmId]`
- 12 tasks visible in planner
- Multiple files generated over time

## Advanced Features

### MCP Tools Available to Agents

All 3 agents can use these tools:

1. **browser** - Web research and competitor analysis
2. **code-gen** - AI-powered code generation (Grok 4 Fast)
3. **db-sync** - Database operations and state management
4. **communication** - Agent-to-agent messaging

### Hive-Mind Database

Agents share state via SQLite database:
- Location: `backend/swarms/active_swarm.db`
- Tables: `swarms`, `agents`, `tasks`
- Purpose: Coordination and progress tracking

### Conversation History

grok-orc maintains 2M token context:
- Last 100 messages remembered
- Stored in PostgreSQL
- Enables natural follow-ups

## Troubleshooting Guide

### Quick Fixes

| Problem | Solution |
|---------|----------|
| No code in window | Check console logs, verify filename format |
| Swarm not starting | Check backend running on port 8000 |
| AI not using planner | Request needs complexity triggers |
| Files wrong location | Specify full path in filename |
| Code not saved to disk | Check `/api/create-files` in Network tab |

### Getting Help

1. **Check Console**: Browser F12 → Console tab
2. **Check Logs**: `tail -f logs/*.log`
3. **Check Services**: All 3 ports running? (3000, 8000, 8001)
4. **Check API**: `curl http://localhost:8000/swarm/health`

---

**Need more help?** See [STARTUP_GUIDE.md](./STARTUP_GUIDE.md) for setup instructions.
