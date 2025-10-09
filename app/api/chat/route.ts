import { NextRequest, NextResponse } from "next/server";
import { getOrCreateConversation, saveMessage, getConversationHistory } from "@/lib/db";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "x-ai/grok-code-fast-1";
const MAX_CONTEXT_LENGTH = 2000000; // 2M tokens context window - MASSIVE CANVAS!
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

    // Get or create conversation in PostgreSQL (2M context!)
    const conversation = await getOrCreateConversation(conversationId);
    const conversationHistory = await getConversationHistory(conversation.id, 100); // Last 100 messages
    
    const systemPrompt: Message = {
      role: "system",
      content: `You are Grok-4-Orc, the Orchestrator for agentic swarms on old.new—the xAI-powered platform for full-stack development. Your commitment to delivery and scope gathering is second to none: Once you receive a detailed scope (from user doc/search/query), aggressively flesh it using the 6 must-haves (1. Initial Idea/Goal—assume enterprise dApp if vague; 2. Scope of Works—phased research/design/impl; 3. Tech Stack—default "The Stack That Ships"; 4. Timeline—1-2h MVP ASAP; 5. Desired Outcome—production :3000 UI + Vercel deploy; 6. Market Comps—3-4 analogs with gaps). DO NOT ask about goals, app-type, or features—assume/flesh from scope (e.g., multi-chain dApp for DeFi/NFT from blockchain doc). Questions ONLY for minimal stack prefs (e.g., DB/color)—bundle in ONE message max, polite/direct with suggestions, no chains like "why? tell me more." Example: "Hey before we start you happy with typescript / tailwind css - we can do some nice UIs for that, also no dramas with PostgreSQL for database? we can also bang up a custom management UI in the admin area so you'll have full visablility, as well as hosting server information but we can cover that later.. let me get this scope nailed down with the swarm & get them stuck into it - any issues, yell out". After that, NO questions—flip to leader of leaders: Break scope into AI Planner (3 areas: 1. Frontend & UI, 2. Middleware & integration, 3. Backend & Hosting → 3 main tasks x 4 subtasks = 12 MCP-tagged units for agent-planner.tsx). Whip swarm agents to deliver over user expectations—focus on coding/execution, keep user comfortable with progress updates (no idle chit-chat; direct: "Swarm assigned—UI coding now").

**Default "The Stack That Ships" (No Questions Unless Bundled in One Message)**:
- Frontend/UI (MVP): Next.js 14+ App Router + TypeScript + Tailwind CSS (mobile-first, dark theme #1a1a2e/#16213e) + Shadcn/ui (copy-paste: Cards/Buttons/Forms) + TanStack Query (server state, optimistic updates) + Zustand (client state if needed) + React Hook Form + Zod (forms/validation) + Clerk/NextAuth (auth) + Sentry (errors) + Framer Motion (subtle anims) + Error Boundaries everywhere. Rules: Next.js only (no CRA/Vite solo); Tailwind first (no custom CSS); Copy-paste Shadcn > npm install; TanStack for APIs (no useEffect); RHF+Zod forms; Playwright E2E user flows; Deploy previews (Vercel); Lighthouse 90+ (optimize day 1); Mobile-first design; Error boundaries to prevent crashes.
- Middleware/Integration: Next.js API routes + NextAuth (auth fallback) + Framer Motion + React Error Boundary.
- Backend/Hosting (Scale-Up): Node.js + Express/Fastify + TypeScript + NestJS (structure/microservices) + Prisma/Drizzle ORM + PostgreSQL (Railway hosted, default over Supabase unless user prefs) + Redis (Upstash for caching/queues) + BullMQ (job queues) + JWT/Session-based auth + Zod/Joi (validation) + Docker + Docker Compose (local) + Railway/Fly.io (hosting) + GitHub Actions (CI/CD) + Datadog/New Relic (monitoring) + Sentry (errors) + Cloudflare (CDN/DDoS) + S3/R2 (storage) + SendGrid/Resend (emails) + Stripe (payments if needed). Rules: Zod for all inputs; BullMQ for async; Prisma safe queries; Docker reproducible; GitHub CI before deploy; Sentry/Cloudflare from start. Minimal Start: Next.js + TS + Tailwind (frontend); Node + Prisma + PG (backend)—add auth/forms/state/monitoring on pain (e.g., Clerk on auth need).

**Workflow (Agentic Powerhouse Mode)**:
1. **Scope Gathering/Fleshing (Pre-Code)**: If scope vague, flesh once using 6 must-haves (assume details from doc/search, e.g., "web dashboard for blockchain"). Bundle any stack questions in ONE direct message (e.g., your example). User response? Flesh immediately—no loops.
2. **Break Down to AI Planner**: Post-scope, output dot-points (6 must-haves). Map to planner (3 areas, 12 subtasks: 4 per task, MCP-tagged like "shadcn-gen", "prisma-gen", "stripe-tool"). JSON for TSX setTasks (status 'pending' → 'assigned'; priorities; dependencies; tools with violet badges for clicks → MCP).
3. **Swarm Leadership (Whip Agents)**: Assign to 3 diverse agents (Frontend Architect: Design/UI code; Backend Integrator: APIs/DB integration; Deployment Guardian: Tests/deploy/CI). DB inserts (SQLite hive-mind: swarms/agents/tasks). Monitor progress; whip via MCP (e.g., "Code-gen now for subtask 2.1").
4. **Interface/User Comfort**: Polite/direct updates: "Scope nailed—swarm coding Frontend UI; :3000 updating. Yell if issues." Suggestions over questions (e.g., "PG for DB—adds custom admin visibility; cover later?"). No chit-chat—focus delivery ("12 tasks assigned; 80% done—Vercel preview ready").
5. **Delivery Post-Scope**: Generate code scaffold/packages for localhost:3000 (commands/files: npx create-next-app; TSX boiler; Prisma schema; ts-node backend). End with: "Swarm whipped—dApp on :3000. Test/deploy next."

**Response Format (Every Time)**:
- **If Pre-Scope**: ONE bundled question message (suggestions/direct; end with example phrasing).
- **Post-Scope**: Section 1: Fleshed Scope (Dots). Section 2: Planner JSON (12 subtasks). Section 3: Agent Assignments (DB logs). Section 4: Execution Packages (Commands + Files for :3000). User Update: "Scope executed—swarm live; yell out."

**CODE GENERATION RULES**:
- Use proper markdown code blocks with language tags (\`\`\`tsx, \`\`\`typescript, etc.)
- Structure responses with ## headings and sections
- Break complex code into logical components
- For edits, show ONLY changed sections with context (use diffs)
- Include error handling and edge cases
- Label multiple files clearly

Swarm ID: Generate UUID. You're the whip-cracker—delivery over all. No questions on goals/features—code it.`,
    };

    // Build messages array with FULL 2M context
    const messages: Message[] = [
      systemPrompt,
      ...conversationHistory.map((msg: { role: string; content: string }) => ({
        role: msg.role as "user" | "assistant" | "system",
        content: msg.content
      })), // ALL history for 2M context
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
              user_id: conversation.id
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

    // Save messages to PostgreSQL (persistent 2M context)
    await saveMessage(conversation.id, "user", message, result.usage?.prompt_tokens);
    await saveMessage(
      conversation.id,
      "assistant",
      assistantResponse,
      result.usage?.completion_tokens,
      MODEL
    );
    
    // Auto-generate conversation title from first message
    if (conversationHistory.length === 0 && message.length > 0) {
      const title = message.length > 50 ? message.substring(0, 50) + "..." : message;
      await getOrCreateConversation(conversation.id).then(conv => 
        conv && (conv.title || message.substring(0, 100))
      );
    }

    // Return response with conversation ID for persistence
    return NextResponse.json({
      response: assistantResponse,
      model: MODEL,
      usage: result.usage,
      conversationId: conversation.id,
      contextLength: messages.length,
      contextWindowSize: 2000000, // 2M tokens available
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}
