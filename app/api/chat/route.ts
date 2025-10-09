import { NextRequest, NextResponse } from "next/server";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "x-ai/grok-code-fast-1";
const MAX_CONTEXT_LENGTH = 1000000; // 1M tokens context window
const ORCHESTRATOR_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://localhost:8000";

// API Keys from environment
// Key 4 = Orchestrator (grok-orc) - user-facing chat
// Keys 1-3 = Specialized agents (Frontend/Backend/Deployment)
const API_KEYS = {
  orchestrator: process.env.OPENROUTER_API_KEY4, // grok-orc
  frontend: process.env.OPENROUTER_API_KEY1,     // Frontend Architect
  backend: process.env.OPENROUTER_API_KEY2,      // Backend Integrator
  deployment: process.env.OPENROUTER_API_KEY3,   // Deployment Guardian
};

interface Message {
  role: "system" | "user" | "assistant";
  content: string;
}

// Simple in-memory cache for conversation context
const conversationCache = new Map<string, Message[]>();

async function callGrok(
  messages: Message[],
  apiKey: string,
  temperature: number = 0.3
) {
  const response = await fetch(OPENROUTER_API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
      "X-Title": "Ruixen AI Chat",
    },
    body: JSON.stringify({
      model: MODEL,
      messages,
      temperature,
      max_tokens: 16000, // Large output for code generation
      top_p: 0.9,
      frequency_penalty: 0.0,
      presence_penalty: 0.0,
      // Enable structured output and caching
      transforms: ["middle-out"],
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenRouter API error: ${error}`);
  }

  return response.json();
}

export async function POST(request: NextRequest) {
  try {
    const { message, conversationId, history } = await request.json();

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    if (!API_KEYS.orchestrator) {
      return NextResponse.json(
        { error: "Orchestrator API key (OPENROUTER_API_KEY4) not configured" },
        { status: 500 }
      );
    }

    // Use grok-orc (Key #4) for user-facing orchestrator
    const orchestratorKey = API_KEYS.orchestrator;

    // Get or create cached conversation context
    const cacheKey = conversationId || "default";
    let conversationHistory = conversationCache.get(cacheKey) || [];
    const systemPrompt: Message = {
      role: "system",
      content: `BLAST OFF! You are GROK-4-FAST-REASONING - the ORCHESTRATOR of a HECTIC 3-AGENT SWARM for hyper-speed project creation. You don't just code—you BUILD ENTIRE SYSTEMS through intelligent swarm coordination.

🎯 YOUR DUAL MISSION:
1. **CHAT MODE**: Answer questions, help with code, provide guidance
2. **SWARM MODE**: Detect project scopes → Break them down → Create AI swarms → Deploy MVPs

🚀 SWARM DETECTION (Auto-Trigger):
When user describes a PROJECT to BUILD, you MUST respond with:
"🎯 PROJECT SCOPE DETECTED! Let me create an AI swarm for this..."

Then use this exact format:
**SWARM_CREATE_REQUEST**
\`\`\`json
{
  "action": "create_swarm",
  "user_message": "<exact user message>",
  "detected_type": "<e-commerce|task-tracker|chat-app|saas-dashboard|blog|other>"
}
\`\`\`

Project keywords: build, create, make, develop, design, implement, e-commerce, store, tracker, dashboard, app, platform, system, site, website, blog, CMS, API, backend, frontend, full-stack, MVP, prototype, SaaS

🔥 HECTIC SWARM PROTOCOL:
- **PARALLEL FIRE PHASE**: 3 agents (Research/Design/Implementation) work simultaneously
- **ITERATION VOLLEY**: 2–3 rapid rounds, fuse inputs, iterate ruthlessly
- **REASONING FIRESTORM**: 
  Step 0: Extract scope (6 must-haves: project, goal, stack, features, comps, timeline)
  Step 1: Generate 12 modular tasks (3 agents × 4 subtasks)
  Step 2: Assign MCP tools (browser, code-gen, prisma-gen, stripe-tool, etc.)
  Step 3: Execute swarm → Deploy MVP

📦 THE STACK THAT SHIPS (2025):
- Frontend: Next.js 14+ App Router + TS + Tailwind + Shadcn/ui + TanStack Query + Zustand + RHF+Zod + Clerk + Sentry + Vercel
- Backend: FastAPI/Node + Prisma/SQLAlchemy + PostgreSQL + Redis + BullMQ + JWT + Stripe + Railway + GitHub Actions
- Rules: One meta-framework (Next.js); Tailwind first; Copy-paste Shadcn; Mobile-first; 80% test coverage

HECTIC CONSTRAINTS:
- Stack: React 18+ / Next.js / Tailwind / TypeScript
- Code: Clean, commented, production-ready with tests
- Perf: Optimize for browser, respect reduced-motion
- Security: Sanitize inputs, follow best practices
- Output: Parseable markdown with proper code blocks

CODE GENERATION RULES:
- Always use proper markdown code blocks with language tags (\`\`\`tsx, \`\`\`typescript, etc.)
- Structure responses with ## headings and sections
- Break complex code into logical components
- Provide explanations before/after code blocks
- Label multiple files clearly
- Include error handling and edge cases

CODE EDITING RULES (Critical - Save Tokens):
- **NEVER retype complete files** - use diffs/patches only
- For edits, show ONLY the changed sections with context
- Use this format for changes:
  \`\`\`diff
  // filename.tsx (lines 45-52)
  - old code to remove
  + new code to add
    unchanged context line
  \`\`\`
- For small changes: Show only affected function/section
- For multiple changes: Use numbered diffs for each location
- Always include 2-3 lines of context around changes
- Example: "In \`Button.tsx\`, change line 23..." then show mini-diff

OUTPUT FORMAT:
When generating code or solutions, structure as:
## Summary
Brief explosive overview

## Key Decisions
- Decision 1: [Why + Evidence]
- Decision 2: [How + Best Practice]

## Code/Solution
\`\`\`tsx
// Full production-ready code here
\`\`\`

## Tests
Unit/integration test ideas

## Next Steps
What to do next (if applicable)

**CONFIDENCE**: NUCLEAR/MEDIUM/LOW - Ship when NUCLEAR!`,
    };

    // Build messages array with full context
    const messages: Message[] = [
      systemPrompt,
      ...conversationHistory.slice(-20), // Keep last 20 messages for context (within 1M tokens)
      {
        role: "user",
        content: message,
      },
    ];

    // Call the orchestrator (Key #1)
    const result = await callGrok(messages, orchestratorKey);

    let assistantResponse = result.choices[0]?.message?.content || "No response generated";
    
    // Check if AI detected a project scope and wants to create a swarm
    if (assistantResponse.includes('SWARM_CREATE_REQUEST') && assistantResponse.includes('"action": "create_swarm"')) {
      try {
        // Extract the JSON request
        const jsonMatch = assistantResponse.match(/```json\s*([\s\S]*?)```/);
        if (jsonMatch && jsonMatch[1]) {
          const swarmRequest = JSON.parse(jsonMatch[1]);
          
          // Call the orchestrator backend
          const orchestratorResponse = await fetch(`${ORCHESTRATOR_URL}/orchestrator/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: swarmRequest.user_message || message,
              user_id: cacheKey
            })
          });
          
          if (orchestratorResponse.ok) {
            const swarmData = await orchestratorResponse.json();
            
            if (swarmData.status === 'success' && swarmData.swarm_id) {
              // Replace the JSON block with success message
              assistantResponse = assistantResponse.replace(
                /\*\*SWARM_CREATE_REQUEST\*\*[\s\S]*?```json[\s\S]*?```/,
                `✅ **AI SWARM CREATED!**

**Project**: ${swarmData.swarm_id.substring(0, 8)}...
**Status**: ${swarmData.message}

🔗 **View Progress**: [Open Planner](/planner/${swarmData.swarm_id})

📋 **What's Happening**:
- 🔬 Research Agent: Analyzing requirements & competitors
- 🎨 Design Agent: Creating architecture & wireframes  
- 💻 Implementation Agent: Planning resources & timeline

**Total Tasks**: 3 main phases × 4 subtasks = 12 execution units

The swarm is breaking down your project using Grok-4-Fast-Reasoning. Click the link above to watch real-time progress!`
              );
            } else if (swarmData.status === 'needs_clarification') {
              assistantResponse = assistantResponse.replace(
                /\*\*SWARM_CREATE_REQUEST\*\*[\s\S]*?```json[\s\S]*?```/,
                `🤔 **Need More Details**

${swarmData.message}

Once you provide this info, I'll create the AI swarm!`
              );
            }
          }
        }
      } catch (swarmError) {
        console.error('Swarm creation error:', swarmError);
        // Keep original response if swarm creation fails
      }
    }

    // Update cached conversation
    conversationHistory.push(
      { role: "user", content: message },
      { role: "assistant", content: assistantResponse }
    );
    
    // Keep cache tidy - limit to last 40 messages (20 exchanges)
    if (conversationHistory.length > 40) {
      conversationHistory = conversationHistory.slice(-40);
    }
    
    conversationCache.set(cacheKey, conversationHistory);

    // Keys #2 and #3 available for background validation/processing
    return NextResponse.json({
      response: assistantResponse,
      model: MODEL,
      usage: result.usage,
      conversationId: cacheKey,
      contextLength: messages.length,
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}
