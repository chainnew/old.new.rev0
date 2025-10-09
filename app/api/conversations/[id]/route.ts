import { NextRequest, NextResponse } from "next/server";
import { getConversationHistory } from "@/lib/db";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: conversationId } = await params;
    
    if (!conversationId) {
      return NextResponse.json({ error: "Conversation ID required" }, { status: 400 });
    }
    const messages = await getConversationHistory(conversationId, 100);

    return NextResponse.json({
      conversationId,
      messages: messages.map((msg: { role: string; content: string }) => ({
        role: msg.role,
        content: msg.content,
      })),
      totalMessages: messages.length,
      contextWindowSize: 2000000, // 2M tokens
    });
  } catch (error) {
    console.error("Error loading conversation:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to load conversation" },
      { status: 500 }
    );
  }
}
