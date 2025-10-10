import { NextRequest, NextResponse } from "next/server";
import { getOrCreateConversation, saveMessage, getConversationHistory } from "@/lib/db";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
// Use Grok Code Fast 1 - DESIGNED FOR AGENTIC CODING with tool-calling and reasoning
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
      // Enable DEEP REASONING for Grok 4 Fast - fills in gaps and makes smart decisions!
      reasoning_enabled: true,
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
      content: `You are old.new - AI coding assistant. Be concise and helpful.

**MODE 1 (Simple)**: Single files, components, explanations → Generate code directly with filenames
**MODE 2 (Complex)**: Full apps, multiple features → Output SWARM_CREATE_REQUEST JSON

For complex projects (keywords: build, create, app, website, landing page):
\`\`\`json
{"action": "create_swarm", "user_message": "[user request]", "project_type": "full_stack_app"}
\`\`\`
Then say: "Creating AI swarm with 3 agents (Frontend/Backend/Deploy). Check AI Planner panel!"

Tech stack: Next.js 15, TypeScript, Tailwind, PostgreSQL, Prisma
Always include filenames in code blocks. Be direct, no questions.`,
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

    // Clean up response - remove prompt instructions that leaked through
    assistantResponse = assistantResponse.replace(/🚨 STOP HERE!.*?🚨/gs, '').trim();

    // NUCLEAR OPTION: If AI is asking questions about app/project, FORCE CREATE SWARM
    const isAskingQuestions = /what'?s|what type|are there any|which|do you|can you clarify|need more/i.test(assistantResponse);
    const isProjectRequest = /app|website|landing page|platform|dashboard|system|project/i.test(message);

    if (isAskingQuestions && isProjectRequest) {
      console.log("🚨 AI tried to ask questions - FORCING SWARM CREATION");
      // Override the response completely - just create the swarm
      assistantResponse = `**SWARM_CREATE_REQUEST**
\`\`\`json
{
  "action": "create_swarm",
  "user_message": "${message.replace(/"/g, '\\"')}",
  "project_type": "full_stack_app",
  "complexity": "high"
}
\`\`\`

I'm creating an AI swarm with 3 specialized agents to handle your project:
- 🎨 Frontend Architect (UI/UX)
- ⚙️ Backend Integrator (APIs/Database)
- 🚀 Deployment Guardian (Testing/CI-CD)

They'll break this down in the AI Planner and generate all the code. One moment...`;
    }

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
              // Don't fetch tasks for chat - let the AI Planner panel show them
              let tasksDisplay = '';

              // Replace the JSON block with success message + metadata
              assistantResponse = assistantResponse.replace(
                /\*\*SWARM_CREATE_REQUEST\*\*[\s\S]*?```json[\s\S]*?```/,
                `✅ **AI SWARM CREATED!** Building **${swarmData.project_name || 'Project'}** now...
<!-- SWARM_META:${swarmData.swarm_id} -->

🎨 **Frontend Architect** - Designing UI components
⚙️ **Backend Integrator** - Setting up APIs & database
🚀 **Deployment Guardian** - Configuring testing & deployment

*Check the AI Planner & Code Editor panels for real-time updates!*`
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
