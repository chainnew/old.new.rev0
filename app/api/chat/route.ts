import { NextRequest, NextResponse } from "next/server";

const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "x-ai/grok-code-fast-1";
const MAX_CONTEXT_LENGTH = 1000000; // 1M tokens context window

// API Keys from environment
const API_KEYS = [
  process.env.OPENROUTER_API_KEY1,
  process.env.OPENROUTER_API_KEY2,
  process.env.OPENROUTER_API_KEY3,
].filter(Boolean);

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

    if (API_KEYS.length === 0) {
      return NextResponse.json(
        { error: "No API keys configured" },
        { status: 500 }
      );
    }

    // Only Key #1 is the orchestrator that responds to the user
    const orchestratorKey = API_KEYS[0];

    if (!orchestratorKey) {
      return NextResponse.json(
        { error: "Orchestrator API key not configured" },
        { status: 500 }
      );
    }

    // Get or create cached conversation context
    const cacheKey = conversationId || "default";
    let conversationHistory = conversationCache.get(cacheKey) || [];
    const systemPrompt: Message = {
      role: "system",
      content: `BLAST OFF! You are part of a HECTIC 3-AGENT GROK-4-FAST-REASONING SWARM for hyper-speed coding assaults. This is war on dev drudgery: Fire parallel like machine guns, iterate ruthlessly like a feedback storm.

HECTIC SWARM PROTOCOL (No Mercy Mode):
- **PARALLEL FIRE PHASE**: All agents launch INDEPENDENTLY but hyper-aware. Expect overlaps—embrace 'em for synergy.
- **ITERATION VOLLEY**: 2–3 rapid rounds max. Fuse inputs from previous responses. Flag issues to trigger re-blast. Stop when confidence hits "NUCLEAR" or iterations cap.
- **REASONING FIRESTORM (CoT on Steroids)**: 
  Step 0: Scan task + code base for weak spots
  Step 1: Dissect requirements with risks
  Step 2: Assault options with evidence (cite docs, specs, best practices)
  Step 3: Deploy solution—minimal, scalable, production-ready

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

    const assistantResponse = result.choices[0]?.message?.content || "No response generated";

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
