import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient | null };

// Fallback: Check if DATABASE_URL exists, otherwise use in-memory cache
const hasDatabaseUrl = process.env.DATABASE_URL && process.env.DATABASE_URL.length > 0;

export const prisma = hasDatabaseUrl ? (
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })
) : null;

if (process.env.NODE_ENV !== 'production' && prisma) globalForPrisma.prisma = prisma;

// In-memory fallback cache
const inMemoryConversations = new Map<string, any>();
const inMemoryMessages = new Map<string, any[]>();

// Helper function to get or create conversation
export async function getOrCreateConversation(conversationId?: string, userId?: string) {
  // Fallback to in-memory if no DB
  if (!prisma) {
    const id = conversationId || `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    if (!inMemoryConversations.has(id)) {
      inMemoryConversations.set(id, {
        id,
        userId,
        title: 'New Chat',
        status: 'active',
        contextWindowSize: 2000000,
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      });
      inMemoryMessages.set(id, []);
    }
    return inMemoryConversations.get(id)!;
  }

  // Use PostgreSQL if available
  if (conversationId) {
    const existing = await prisma.conversation.findUnique({
      where: { id: conversationId },
      include: {
        messages: {
          orderBy: { createdAt: 'asc' },
          take: 100, // Last 100 messages for 2M context
        },
      },
    });
    if (existing) return existing;
  }

  // Create new conversation
  return await prisma.conversation.create({
    data: {
      userId,
      title: 'New Chat',
      status: 'active',
      contextWindowSize: 2000000, // 2M tokens
    },
    include: {
      messages: true,
    },
  });
}

// Save message to DB
export async function saveMessage(
  conversationId: string,
  role: 'user' | 'assistant' | 'system',
  content: string,
  tokensUsed?: number,
  model?: string
) {
  // Fallback to in-memory if no DB
  if (!prisma) {
    const messages = inMemoryMessages.get(conversationId) || [];
    const newMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      conversationId,
      role,
      content,
      tokensUsed,
      model: model || 'x-ai/grok-code-fast-1',
      createdAt: new Date(),
    };
    messages.push(newMessage);
    inMemoryMessages.set(conversationId, messages);
    return newMessage;
  }

  return await prisma.message.create({
    data: {
      conversationId,
      role,
      content,
      tokensUsed,
      model: model || 'x-ai/grok-code-fast-1',
    },
  });
}

// Get conversation history (for 2M context)
export async function getConversationHistory(conversationId: string, limit: number = 100) {
  // Fallback to in-memory if no DB
  if (!prisma) {
    const messages = inMemoryMessages.get(conversationId) || [];
    return messages.slice(-limit).map(msg => ({
      role: msg.role,
      content: msg.content,
      createdAt: msg.createdAt,
      tokensUsed: msg.tokensUsed,
    }));
  }

  return await prisma.message.findMany({
    where: { conversationId },
    orderBy: { createdAt: 'asc' },
    take: limit,
    select: {
      role: true,
      content: true,
      createdAt: true,
      tokensUsed: true,
    },
  });
}

// Update conversation title based on first message
export async function updateConversationTitle(conversationId: string, title: string) {
  // Fallback to in-memory if no DB
  if (!prisma) {
    const conv = inMemoryConversations.get(conversationId);
    if (conv) {
      conv.title = title.substring(0, 100);
      conv.updatedAt = new Date();
    }
    return conv;
  }

  return await prisma.conversation.update({
    where: { id: conversationId },
    data: { title: title.substring(0, 100) },
  });
}
