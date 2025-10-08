# PostgreSQL RAG Database Setup

## 🚀 Epic Schema for HECTIC 3-Agent Swarm + RAG

This database schema supports:
- **3-Agent HECTIC SWARM** orchestration (Planner, Coder, Reviewer)
- **1M token context** conversations with full history
- **RAG (Retrieval Augmented Generation)** with vector embeddings
- **Code artifacts** tracking and versioning
- **Task planning** system integration
- **Knowledge base** with hybrid search

---

## 📦 Prerequisites

### 1. Install PostgreSQL
```bash
# macOS
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15
```

### 2. Install Required Extensions
The schema automatically creates these, but ensure your PostgreSQL supports:
- **pgvector** - For vector embeddings (RAG)
- **pg_trgm** - For fuzzy text search
- **uuid-ossp** - For UUID generation

```bash
# Install pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

---

## 🛠️ Setup Instructions

### 1. Create Database
```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE ruixen_ai_chat;

# Connect to the new database
\c ruixen_ai_chat
```

### 2. Run Schema
```bash
# From your project directory
psql -d ruixen_ai_chat -f database/schema.sql
```

### 3. Verify Installation
```sql
-- Check tables
\dt

-- Check agents
SELECT * FROM agents;

-- Check extensions
\dx
```

---

## 🔥 Key Features

### 1. **3-Agent Swarm Tracking**
```sql
-- Agent 1: Strategic Planner (API Key 1)
-- Agent 2: Code Blaster (API Key 2)  
-- Agent 3: Bug Hunter (API Key 3)

-- Track agent executions
SELECT * FROM agent_performance;
```

### 2. **RAG Vector Search**
```sql
-- Semantic search for relevant messages
SELECT * FROM search_messages(
    '[your_1536_dim_vector]'::vector,
    0.7,  -- similarity threshold
    10    -- max results
);

-- Hybrid search (semantic + keyword)
SELECT * FROM hybrid_search_documents(
    'Next.js authentication',
    '[query_embedding]'::vector,
    10
);
```

### 3. **Conversation Context (1M Tokens)**
```sql
-- Get last 20 messages for context
SELECT * FROM get_conversation_context(
    'conversation-uuid-here',
    20
);
```

### 4. **Code Artifact Search**
```sql
-- Find similar code by semantic meaning
SELECT * FROM search_code(
    '[code_embedding]'::vector,
    'typescript',  -- language filter
    0.7,
    5
);
```

---

## 📊 Database Structure

### Core Tables
- `users` - User accounts
- `conversations` - Chat sessions (1M context)
- `messages` - All chat messages with embeddings
- `agents` - 3 HECTIC SWARM agents
- `agent_executions` - Track each agent's work
- `agent_collaboration` - Swarm coordination

### Code & Artifacts
- `code_artifacts` - Generated code with versioning
- `file_trees` - Project structures
- `code_examples` - Curated snippets

### Task System
- `tasks` - Main tasks
- `subtasks` - Subtasks with MCP tools

### Knowledge Base (RAG)
- `documents` - Source documents
- `document_chunks` - Chunked with embeddings
- `code_examples` - Searchable code library

### Analytics
- `api_usage` - Token tracking & costs
- `feedback` - User ratings
- `search_queries` - Search history

---

## 🎯 Integration with Next.js

### 1. Install PostgreSQL Client
```bash
npm install pg @vercel/postgres
```

### 2. Environment Variables
```env
# .env.local
POSTGRES_URL="postgresql://user:password@localhost:5432/ruixen_ai_chat"
POSTGRES_PRISMA_URL="postgresql://user:password@localhost:5432/ruixen_ai_chat?schema=public"
```

### 3. Example Query
```typescript
// lib/db.ts
import { sql } from '@vercel/postgres';

export async function saveMessage(
  conversationId: string,
  role: string,
  content: string,
  embedding: number[]
) {
  return sql`
    INSERT INTO messages (conversation_id, role, content, embedding)
    VALUES (${conversationId}, ${role}, ${content}, ${embedding})
    RETURNING *
  `;
}

export async function searchSimilarCode(
  embedding: number[],
  language: string,
  limit: number = 5
) {
  return sql`
    SELECT * FROM search_code(
      ${embedding}::vector,
      ${language},
      0.7,
      ${limit}
    )
  `;
}
```

---

## 🔍 RAG Pipeline

### 1. Generate Embeddings
```typescript
// Use OpenAI or similar
import OpenAI from 'openai';

const openai = new OpenAI();

async function getEmbedding(text: string) {
  const response = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: text,
  });
  return response.data[0].embedding;
}
```

### 2. Store with Embedding
```typescript
const embedding = await getEmbedding(userMessage);
await sql`
  INSERT INTO messages (conversation_id, role, content, embedding)
  VALUES (${conversationId}, 'user', ${userMessage}, ${embedding})
`;
```

### 3. Retrieve Context
```typescript
const queryEmbedding = await getEmbedding(userQuery);
const relevantDocs = await sql`
  SELECT * FROM hybrid_search_documents(
    ${userQuery},
    ${queryEmbedding}::vector,
    5
  )
`;
```

### 4. Augment Prompt
```typescript
const context = relevantDocs.rows
  .map(doc => doc.chunk_text)
  .join('\n\n');

const augmentedPrompt = `
Context from knowledge base:
${context}

User question: ${userQuery}
`;
```

---

## 📈 Performance Optimization

### Indexes Already Created
- **Vector HNSW indexes** for fast similarity search
- **Full-text search indexes** for keyword matching
- **Trigram indexes** for fuzzy search
- **B-tree indexes** on foreign keys and timestamps

### Query Performance Tips
```sql
-- Use EXPLAIN ANALYZE to check query plans
EXPLAIN ANALYZE
SELECT * FROM search_messages('[embedding]'::vector, 0.7, 10);

-- Monitor index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## 🧪 Testing Queries

### Insert Test Data
```sql
-- Create test user
INSERT INTO users (email, username) 
VALUES ('test@example.com', 'testuser')
RETURNING id;

-- Create conversation
INSERT INTO conversations (user_id, title)
VALUES ('user-uuid-here', 'Test Conversation')
RETURNING id;

-- Insert message
INSERT INTO messages (conversation_id, role, content)
VALUES ('conv-uuid-here', 'user', 'Hello, can you help me build an app?');
```

### Test Agent Execution
```sql
INSERT INTO agent_executions (
  conversation_id,
  agent_id,
  message_id,
  input_prompt,
  output_response,
  confidence_level,
  tokens_used,
  execution_time_ms,
  status
) VALUES (
  'conv-uuid',
  (SELECT id FROM agents WHERE name = 'Agent 1 - Strategic Planner'),
  'message-uuid',
  'Build a todo app',
  'Plan: 1. Create React components 2. Add state management 3. Style with Tailwind',
  'NUCLEAR',
  500,
  1200,
  'completed'
);
```

---

## 🔒 Security Considerations

1. **Connection Pooling**: Use `pg-pool` for production
2. **Prepared Statements**: Always use parameterized queries
3. **Row-Level Security**: Add RLS policies for multi-tenant
4. **SSL**: Enable SSL connections in production
5. **Secrets**: Never commit connection strings

---

## 🚀 Deployment

### Vercel Postgres
```bash
# Install Vercel CLI
npm i -g vercel

# Create Postgres database
vercel postgres create

# Connect and run schema
vercel postgres connect
\i database/schema.sql
```

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Create project
railway init

# Add Postgres
railway add postgres

# Run migrations
railway run psql < database/schema.sql
```

### Supabase
```bash
# Create project at supabase.com
# Go to SQL Editor
# Paste schema.sql and run
```

---

## 📚 Additional Resources

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

## 🆘 Troubleshooting

### Extension Not Found
```sql
-- Check available extensions
SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';

-- If missing, install pgvector (see Prerequisites)
```

### Slow Vector Queries
```sql
-- Rebuild HNSW index
REINDEX INDEX idx_messages_embedding;

-- Increase maintenance_work_mem
SET maintenance_work_mem = '256MB';
```

### Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -d ruixen_ai_chat -c "SELECT version();"
```

---

## 🎉 Ready to Go!

Your epic PostgreSQL RAG schema is now set up to support:
- ✅ 3-agent HECTIC SWARM orchestration
- ✅ 1M token conversation context
- ✅ Vector similarity search (RAG)
- ✅ Code artifact tracking
- ✅ Task planning system
- ✅ Full analytics & performance metrics

Fire up your AI chat and let the swarm BLAST! 🚀🔥
