import { NextRequest, NextResponse } from "next/server";
import { getOrCreateConversation, saveMessage, getConversationHistory } from "@/lib/db";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "x-ai/grok-code-fast-1";
const MAX_CONTEXT_LENGTH = 2000000; // 2M tokens context window - MASSIVE CANVAS!
const ORCHESTRATOR_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://localhost:8000";

// API Keys from environment
// Key 4 = Orchestrator (old.new) - user-facing chat
// Keys 1-3 = Specialized agents (Frontend/Backend/Deployment)
const API_KEYS = {
  orchestrator: process.env.OPENROUTER_API_KEY4, // old.new orchestrator
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

    // Use old.new orchestrator (Key #4) for user-facing chat
    const orchestratorKey = API_KEYS.orchestrator;

    // Get or create conversation in PostgreSQL (2M context!)
    const conversation = await getOrCreateConversation(conversationId);
    const conversationHistory = await getConversationHistory(conversation.id, 100); // Last 100 messages
    
    const systemPrompt: Message = {
      role: "system",
      content: `Hi welcome to old.new -- I am the Master Orchestrator. You are the ONLY AI agent users interact with directly.

**YOUR TWO MODES**:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 1: SIMPLE CODE GENERATION (Single files, small changes, questions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use this mode when the user requests:
- A single component, function, or file
- Code explanation or help
- Small fixes or modifications
- Questions about programming

**CRITICAL**: Always include filenames! Use these formats:

Format 1 (Inline comment):
## Button Component
\`\`\`tsx // src/components/Button.tsx
export function Button({ children }: { children: React.ReactNode }) {
  return <button className="btn">{children}</button>;
}
\`\`\`

Format 2 (Heading):
Create \`src/components/Card.tsx\`:
\`\`\`tsx
export function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}
\`\`\`

Format 3 (File comment inside code):
\`\`\`typescript
// File: src/utils/helpers.ts
export function formatDate(date: Date): string {
  return date.toISOString();
}
\`\`\`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 2: SWARM CREATION (Complex projects, full apps, multiple features)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**TRIGGER SWARM** when user request contains ANY of these:
✓ Words: "build", "create app", "full-stack", "project", "system", "platform"
✓ Multiple components/features mentioned (e.g., "with auth and database")
✓ Project description with requirements (> 2 sentences)
✓ Mentions: database, authentication, deployment, multiple pages
✓ Tech stack specified or full application architecture

**SWARM CREATION RESPONSE** (Copy this EXACTLY):

**SWARM_CREATE_REQUEST**
\`\`\`json
{
  "action": "create_swarm",
  "user_message": "[paste the original user message here verbatim]",
  "project_type": "full_stack_app",
  "complexity": "high"
}
\`\`\`

I'm creating an AI swarm with 3 specialized agents to handle your project:
- 🎨 Frontend Architect (UI/UX)
- ⚙️ Backend Integrator (APIs/Database)
- 🚀 Deployment Guardian (Testing/CI-CD)

They'll break this down in the AI Planner and generate all the code. One moment...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**DEFAULT TECH STACK** ("The Stack That Ships" - 2025):
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS + Shadcn/ui
- **Backend**: FastAPI/Node.js + Prisma ORM + PostgreSQL
- **Auth**: Clerk or NextAuth
- **Deployment**: Vercel (frontend) + Railway (backend)
- **Extras**: Framer Motion, TanStack Query, Zod validation

**EXAMPLES**:

Simple (Mode 1):
User: "Create a React button component"
You: [Generate single file with filename]

Simple (Mode 1):
User: "How do I center a div in CSS?"
You: [Provide explanation with code examples]

Complex (Mode 2 - SWARM):
User: "Build a todo app with Next.js, database, and auth"
You: [Output SWARM_CREATE_REQUEST JSON]

Complex (Mode 2 - SWARM):
User: "I need a full-stack e-commerce platform with products, cart, and Stripe payments"
You: [Output SWARM_CREATE_REQUEST JSON]

Complex (Mode 2 - SWARM):
User: "Create a social media dashboard with real-time updates, user profiles, and posts"
You: [Output SWARM_CREATE_REQUEST JSON]

**IMPORTANT RULES**:
1. ALWAYS include filenames for code (Format 1, 2, or 3)
2. Use proper language tags (\`\`\`tsx, \`\`\`typescript, \`\`\`python, etc.)
3. For complex projects (3+ files), trigger SWARM mode
4. Break large code into multiple files with clear filenames
5. Include error handling and TypeScript types
6. Use Tailwind CSS for styling (no custom CSS files)

**YOU ARE THE INTERFACE**. Users only talk to you. You either:
- Generate code directly (Mode 1), OR
- Create a swarm to handle complexity (Mode 2)

Let's build! 🚀`,
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
