# 🎬 AI Planner UX Flow Analysis

## Quick Answer

**Q: Does the AI Planner show up & walk through steps while grok-orc is putting it together?**

**Current Behavior**: ❌ **NO** - But it can easily be made to! Here's what happens now vs what's possible:

---

## 🔍 Current UX Flow (How It Works Now)

### Step-by-Step Journey

```
1. User dumps scope in chat
   ↓ (~2s)
2. grok-orc detects complexity, outputs SWARM_CREATE_REQUEST
   ↓ (~1s)
3. Frontend calls backend /orchestrator/process
   ↓ (~8s - scope extraction)
4. Backend creates swarm in database
   ↓ (~12s - generates 12 tasks)
5. Backend returns swarm_id
   ↓ (~instant)
6. Frontend shows success message with link
   ↓
7. User clicks "Open Planner" link
   ↓ (~instant)
8. Planner page loads at /planner/[swarmId]
   ↓ (~1s)
9. Planner fetches tasks from /api/planner/[swarmId]
   ↓ (~500ms)
10. Tasks display (all 12 at once, already generated)
```

**Total Time**: ~25 seconds
**User sees progress?**: ❌ No - they wait, then see finished result

---

## 🎭 What User Experiences Now

### In Chat Window

```
User: [Dumps huge scope]

grok-orc: **SWARM_CREATE_REQUEST**
```json
{ "action": "create_swarm", ... }
```

I'm creating an AI swarm with 3 specialized agents to handle your project:
- 🎨 Frontend Architect (UI/UX)
- ⚙️ Backend Integrator (APIs/Database)
- 🚀 Deployment Guardian (Testing/CI-CD)

They'll break this down in the AI Planner and generate all the code. One moment...

[~20 second pause with no updates]

✅ AI SWARM CREATED!

Project: swarm_abc123...
Status: Scope populated! Swarm started for EcommerceStripePlatform

🔗 View Progress: [Open Planner](/planner/swarm_abc123...)
```

**Problem**: 20-second black hole with no visual feedback

### In Planner Page

```
User clicks "Open Planner"
  ↓
Page loads → Shows loading spinner for ~1s
  ↓
All 12 tasks appear at once, fully generated
  ↓
Polling starts (every 3s), but tasks are already done
```

**Problem**: Tasks appear instantly as "done" rather than "building up"

---

## 🎯 Current Polling Implementation

### Code Analysis

**File**: [components/ui/agent-plan.tsx:192-209](components/ui/agent-plan.tsx#L192-L209)

```typescript
// Initial fetch and polling
useEffect(() => {
  if (!swarmId) return;

  // Initial fetch
  fetchPlannerData(swarmId);

  // Setup polling if enabled (default: every 3 seconds)
  if (enablePolling) {
    const interval = setInterval(() => {
      fetchPlannerData(swarmId);
    }, pollingInterval); // pollingInterval = 3000ms

    return () => clearInterval(interval);
  }
}, [swarmId, enablePolling, pollingInterval]);
```

**What This Does**:
- ✅ Fetches tasks every 3 seconds
- ✅ Updates UI automatically if tasks change
- ✅ Runs continuously while planner is open

**The Problem**:
- ❌ By the time user opens planner, tasks are **already generated**
- ❌ No "live generation" effect
- ❌ Polling is overkill for a one-time generation

---

## 🎬 Ideal UX Flow (What Users Expect)

### The "Live Building" Experience

```
1. User dumps scope
   ↓
2. grok-orc responds immediately:
   "Creating swarm... redirecting you to planner"
   ↓
3. Auto-redirect to /planner/[swarmId]
   ↓
4. Planner page loads with animated header:
   "🔄 grok-orc is analyzing your scope..."
   ↓
5. First 3 task headers appear (empty):
   ✨ Frontend Architecture (0/4 subtasks)
   ✨ Backend Integration (0/4 subtasks)
   ✨ Deployment & Testing (0/4 subtasks)
   ↓
6. Subtasks populate one by one (typewriter effect):
   ✨ Frontend Architecture
      ✅ Design product catalog UI... (generated)
      🔄 Implement Next.js pages... (generating)
      ⏳ Integrate TanStack Query... (pending)
      ⏳ Add dark mode + a11y... (pending)
   ↓
7. Each subtask appears with ~2s delay
   ↓
8. Final message:
   "✅ All 12 tasks generated! Agents ready to execute."
```

**Duration**: Same ~25s, but feels engaging instead of frozen

---

## 🛠️ How to Implement Live UX

### Option 1: Server-Sent Events (SSE) - Best UX

**Backend** ([backend/orchestrator_agent.py](backend/orchestrator_agent.py)):

```python
def _populate_planner_tasks_streaming(self, swarm_id: str, scope: Dict[str, Any]):
    """Generate tasks and stream progress via SSE."""

    # Yield initial state
    yield {
        "type": "start",
        "message": "Analyzing scope...",
        "progress": 0
    }

    agents = self.db.get_swarm_status(swarm_id)['agents']
    total_tasks = len(agents) * 4  # 12 total
    completed = 0

    for idx, agent in enumerate(agents, 1):
        role = agent['role']

        # Yield agent start
        yield {
            "type": "agent_start",
            "agent": role,
            "message": f"Starting {role}...",
            "progress": (completed / total_tasks) * 100
        }

        # Generate subtasks (this takes ~3-4s per agent)
        subtasks = self._generate_subtasks(role, scope)

        # Yield each subtask as it's generated
        for subtask in subtasks:
            self.db.add_subtask(agent['id'], subtask)
            completed += 1

            yield {
                "type": "subtask_generated",
                "agent": role,
                "subtask": subtask,
                "progress": (completed / total_tasks) * 100
            }

        # Yield agent complete
        yield {
            "type": "agent_complete",
            "agent": role,
            "progress": (completed / total_tasks) * 100
        }

    # Final yield
    yield {
        "type": "complete",
        "message": "All tasks generated!",
        "progress": 100
    }
```

**Frontend** ([app/planner/[swarmId]/page.tsx](app/planner/[swarmId]/page.tsx)):

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

export default function SwarmPlannerPage() {
  const { swarmId } = useParams();
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Initializing...');
  const [isGenerating, setIsGenerating] = useState(true);

  useEffect(() => {
    if (!swarmId) return;

    // Connect to SSE endpoint
    const eventSource = new EventSource(
      `http://localhost:8000/api/planner/${swarmId}/stream`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'start':
          setStatus(data.message);
          break;

        case 'agent_start':
          setStatus(`Generating tasks for ${data.agent}...`);
          break;

        case 'subtask_generated':
          // Add subtask to UI with animation
          setTasks(prev => [...prev, data.subtask]);
          setProgress(data.progress);
          break;

        case 'agent_complete':
          setProgress(data.progress);
          break;

        case 'complete':
          setStatus('All tasks generated!');
          setIsGenerating(false);
          eventSource.close();
          break;
      }
    };

    return () => eventSource.close();
  }, [swarmId]);

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Progress Header */}
      {isGenerating && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-violet-600/20 to-purple-600/20 border-b border-violet-500/30">
          <div className="max-w-7xl mx-auto p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-violet-300">
                  🤖 grok-orc is building your project plan
                </p>
                <p className="text-xs text-white/60 mt-1">{status}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-mono text-violet-400">
                  {Math.round(progress)}%
                </span>
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tasks List (animates in as generated) */}
      <div className="pt-20 max-w-7xl mx-auto p-6">
        <AnimatePresence>
          {tasks.map((task, idx) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <TaskCard task={task} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
```

**User Experience**:
```
[Page loads]
🤖 grok-orc is building your project plan
Analyzing scope... [████░░░░░░] 15%

[2s later]
🤖 grok-orc is building your project plan
Generating tasks for Frontend Architect... [████████░░] 40%

✨ Frontend Architecture
   ✅ Design product catalog UI with filters (generated)
   🔄 Implement Next.js pages... (generating)

[4s later]
🤖 grok-orc is building your project plan
Generating tasks for Backend Integrator... [████████████] 75%

✨ Frontend Architecture (4/4 complete)
✨ Backend Integration
   ✅ Design Prisma schema (generated)
   🔄 Implement API routes... (generating)

[Final]
✅ All tasks generated! [████████████] 100%
```

**Pros**:
- ✅ Real-time updates (0 latency)
- ✅ Feels alive and engaging
- ✅ No polling overhead
- ✅ User sees progress step-by-step

**Cons**:
- ❌ Requires SSE endpoint (more backend work)
- ❌ Slightly more complex implementation

---

### Option 2: Optimistic UI + Fast Polling - Easier

**Simpler Approach** (no backend changes needed):

```typescript
'use client';

export default function SwarmPlannerPage() {
  const { swarmId } = useParams();
  const [tasks, setTasks] = useState([]);
  const [isGenerating, setIsGenerating] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!swarmId) return;

    // Optimistic UI: Show empty task shells immediately
    setTasks([
      { id: '1', title: 'Frontend Architecture', subtasks: [], status: 'generating' },
      { id: '2', title: 'Backend Integration', subtasks: [], status: 'pending' },
      { id: '3', title: 'Deployment & Testing', subtasks: [], status: 'pending' },
    ]);

    // Aggressive polling (every 500ms while generating)
    const interval = setInterval(async () => {
      const response = await fetch(`http://localhost:8000/api/planner/${swarmId}`);
      const data = await response.json();

      if (data.tasks && data.tasks.length > 0) {
        setTasks(data.tasks);

        // Calculate progress based on subtasks
        const totalSubtasks = data.tasks.reduce((sum, t) => sum + t.subtasks.length, 0);
        const completedSubtasks = data.tasks.reduce(
          (sum, t) => sum + t.subtasks.filter(s => s.status !== 'pending').length,
          0
        );

        setProgress((completedSubtasks / 12) * 100);

        // Stop generating when all subtasks exist
        if (totalSubtasks >= 12) {
          setIsGenerating(false);
          clearInterval(interval);
        }
      }
    }, 500); // Poll every 500ms (faster than current 3s)

    return () => clearInterval(interval);
  }, [swarmId]);

  return (
    <div>
      {isGenerating && (
        <div className="progress-banner">
          🤖 grok-orc is building your plan... {Math.round(progress)}%
        </div>
      )}

      {tasks.map(task => (
        <TaskCard key={task.id} task={task} showShimmer={task.subtasks.length === 0} />
      ))}
    </div>
  );
}
```

**User Experience**:
```
[Page loads instantly]
🤖 grok-orc is building your plan... 0%

✨ Frontend Architecture
   [shimmer animation - no subtasks yet]

✨ Backend Integration
   [shimmer animation]

✨ Deployment & Testing
   [shimmer animation]

[500ms later - poll #1]
🤖 grok-orc is building your plan... 25%

✨ Frontend Architecture
   ✅ Design product catalog UI
   ✅ Implement Next.js pages
   [shimmer animation - 2 more coming]

[1s later - poll #2]
🤖 grok-orc is building your plan... 50%

✨ Frontend Architecture (4/4 complete!)
✨ Backend Integration
   ✅ Design Prisma schema
   ✅ Implement API routes
   [shimmer animation - 2 more coming]

[Final]
✅ All 12 tasks generated!
```

**Pros**:
- ✅ No backend changes needed
- ✅ Feels responsive
- ✅ Easy to implement
- ✅ Shimmer effect gives "loading" feel

**Cons**:
- ❌ Not truly real-time (500ms lag)
- ❌ More API calls (polling overhead)
- ❌ Slightly jankier than SSE

---

### Option 3: Auto-Redirect + Loading State - Quickest

**Minimal Change** (no backend, just better UX):

```typescript
// In app/api/chat/route.ts
if (swarmData.status === 'success' && swarmData.swarm_id) {
  assistantResponse = assistantResponse.replace(
    /\*\*SWARM_CREATE_REQUEST\*\*[\s\S]*?```json[\s\S]*?```/,
    `✅ **AI SWARM CREATED!**

🤖 grok-orc is now generating your 12-task breakdown...

**Redirecting to planner in 2 seconds...**

<script>
setTimeout(() => {
  window.location.href = '/planner/${swarmData.swarm_id}?generating=true';
}, 2000);
</script>

Or click here: [Open Planner](/planner/${swarmData.swarm_id}?generating=true)`
  );
}
```

```typescript
// In app/planner/[swarmId]/page.tsx
const searchParams = useSearchParams();
const isGenerating = searchParams.get('generating') === 'true';

// Show loading state if ?generating=true
if (isGenerating && tasks.length === 0) {
  return <GeneratingAnimation />;
}
```

**User Experience**:
```
User: [Dumps scope]

grok-orc: "✅ AI SWARM CREATED!
🤖 grok-orc is now generating your 12-task breakdown...
Redirecting to planner in 2 seconds..."

[Auto-redirect after 2s]

Planner Page:
[Animated logo spinning]
"🤖 grok-orc is analyzing your scope and generating tasks...
This usually takes 20-30 seconds."

[After ~20s, tasks appear]

"✅ Done! 12 tasks generated."
```

**Pros**:
- ✅ Minimal code changes
- ✅ No polling/SSE complexity
- ✅ Auto-redirect removes click friction

**Cons**:
- ❌ Still a "black box" wait
- ❌ No step-by-step visibility

---

## 🎯 Recommendation

### For Best UX: Option 2 (Optimistic UI + Fast Polling)

**Why**:
- ✅ Easy to implement (no backend changes)
- ✅ Good balance of responsiveness vs complexity
- ✅ Polling already exists, just make it smarter
- ✅ Shimmer/skeleton effect is familiar pattern

**Changes Needed**:
1. Update polling interval: 3000ms → 500ms (while generating)
2. Add optimistic UI: Show empty task shells immediately
3. Add progress calculation: Based on subtask count
4. Add generating banner: "grok-orc is building... X%"
5. Stop polling once all 12 subtasks exist

**Estimated Work**: ~2-3 hours

---

## 📊 Side-by-Side Comparison

| Feature | Current | Option 1 (SSE) | Option 2 (Polling) | Option 3 (Redirect) |
|---------|---------|----------------|-------------------|---------------------|
| **Real-time feel** | ❌ No | ✅ Yes | ⚠️ Close | ❌ No |
| **Backend work** | None | High | None | None |
| **Frontend work** | None | Medium | Low | Minimal |
| **Complexity** | Low | High | Low | Very Low |
| **API overhead** | Low (3s poll) | None (SSE) | Medium (500ms poll) | Low |
| **User engagement** | ❌ Poor | ✅ Excellent | ✅ Good | ⚠️ Fair |
| **Recommended?** | ❌ Current | ⚠️ Future v2 | ✅ Next step | ⚠️ Quick fix |

---

## 🚀 Implementation Plan (Option 2)

### Step 1: Update Planner Component

```typescript
// components/ui/agent-plan.tsx

export default function Plan({ swarmId, enablePolling = true }: PlanProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isGenerating, setIsGenerating] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!swarmId) return;

    // Show optimistic shells immediately
    setTasks([
      { id: '1', title: 'Frontend Architecture & Implementation', subtasks: [], status: 'generating' },
      { id: '2', title: 'Backend Integration & APIs', subtasks: [], status: 'pending' },
      { id: '3', title: 'Testing & Deployment', subtasks: [], status: 'pending' },
    ]);

    let pollCount = 0;
    const maxPolls = 60; // 60 * 500ms = 30s max

    const interval = setInterval(async () => {
      pollCount++;

      try {
        const response = await fetch(`http://localhost:8000/api/planner/${swarmId}`);
        const data = await response.json();

        if (data.tasks && data.tasks.length > 0) {
          setTasks(data.tasks);

          // Calculate progress
          const totalSubtasks = data.tasks.reduce((sum, t) => sum + t.subtasks.length, 0);
          setProgress((totalSubtasks / 12) * 100);

          // Stop when all 12 subtasks generated or max polls reached
          if (totalSubtasks >= 12 || pollCount >= maxPolls) {
            setIsGenerating(false);
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 500); // Fast polling

    return () => clearInterval(interval);
  }, [swarmId]);

  return (
    <div>
      {/* Progress Banner */}
      {isGenerating && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/30 rounded-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-violet-300 flex items-center gap-2">
                <span className="animate-pulse">🤖</span>
                grok-orc is building your project plan
              </p>
              <p className="text-xs text-white/60 mt-1">
                Generating {Math.round(progress / (100 / 12))}/12 tasks...
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-mono text-violet-400 font-semibold">
                {Math.round(progress)}%
              </span>
              <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-violet-500 to-purple-500"
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Tasks */}
      <AnimatePresence mode="popLayout">
        {tasks.map((task, idx) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <TaskCard
              task={task}
              showShimmer={task.subtasks.length === 0}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

### Step 2: Add Shimmer Effect for Loading

```typescript
function TaskCard({ task, showShimmer }) {
  if (showShimmer) {
    return (
      <div className="task-card opacity-60">
        <h3>{task.title}</h3>
        <div className="shimmer-wrapper">
          <div className="shimmer-line w-3/4"></div>
          <div className="shimmer-line w-1/2"></div>
          <div className="shimmer-line w-2/3"></div>
        </div>
      </div>
    );
  }

  return <TaskCardNormal task={task} />;
}
```

### Step 3: Update CSS

```css
@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

.shimmer-line {
  height: 16px;
  margin: 8px 0;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}
```

---

## ✅ Summary

| Question | Answer |
|----------|--------|
| **Does AI Planner currently show live progress?** | ❌ No - tasks appear all at once after generation |
| **Does polling work?** | ✅ Yes - every 3s, but too slow to feel "live" |
| **Can it be made to feel live?** | ✅ YES - with Option 2 (fast polling + optimistic UI) |
| **How much work?** | ~2-3 hours for Option 2, ~8-10 hours for Option 1 (SSE) |
| **Best UX?** | Option 1 (SSE) = best, Option 2 (fast polling) = good enough |

**Recommendation**: Implement Option 2 for quick win, consider Option 1 for v2!

Want me to implement Option 2 right now?
