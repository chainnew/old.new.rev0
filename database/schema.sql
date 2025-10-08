-- =====================================================
-- RUIXEN AI CHAT - PostgreSQL RAG Schema
-- Epic schema for agents, chat, code, and knowledge base
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- CORE TABLES
-- =====================================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active', -- active, archived, deleted
    context_window_size INTEGER DEFAULT 1000000, -- 1M tokens
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model VARCHAR(100) DEFAULT 'x-ai/grok-code-fast-1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    embedding vector(1536) -- OpenAI ada-002 dimension
);

-- =====================================================
-- AGENT SYSTEM
-- =====================================================

-- Agents table - For 3-agent HECTIC SWARM
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL, -- planner, coder, reviewer
    description TEXT,
    api_key_index INTEGER NOT NULL, -- 1, 2, or 3
    system_prompt TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent executions - Track each agent's work
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    input_prompt TEXT NOT NULL,
    output_response TEXT,
    reasoning_steps JSONB, -- CoT steps
    confidence_level VARCHAR(20), -- NUCLEAR, MEDIUM, LOW
    iterate_flag BOOLEAN DEFAULT false,
    iterate_reason TEXT,
    tokens_used INTEGER,
    execution_time_ms INTEGER,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Agent collaboration - Track swarm interactions
CREATE TABLE agent_collaboration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    iteration_round INTEGER DEFAULT 1,
    planner_execution_id UUID REFERENCES agent_executions(id),
    coder_execution_id UUID REFERENCES agent_executions(id),
    reviewer_execution_id UUID REFERENCES agent_executions(id),
    merged_output TEXT,
    final_confidence VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CODE & ARTIFACTS
-- =====================================================

-- Code artifacts - Store generated code
CREATE TABLE code_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    filename VARCHAR(500),
    language VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    description TEXT,
    line_count INTEGER,
    is_diff BOOLEAN DEFAULT false,
    parent_artifact_id UUID REFERENCES code_artifacts(id),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding vector(1536) -- For code similarity search
);

-- File trees - Track project structures
CREATE TABLE file_trees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    tree_structure JSONB NOT NULL, -- Hierarchical file structure
    root_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TASKS & PLANNING (Agent Planner Integration)
-- =====================================================

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- completed, in-progress, pending, need-help, failed
    priority VARCHAR(20) DEFAULT 'medium', -- high, medium, low
    level INTEGER DEFAULT 0,
    dependencies UUID[], -- Array of task IDs
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Subtasks table
CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    mcp_tools VARCHAR(100)[], -- Array of MCP tool names
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- KNOWLEDGE BASE & RAG
-- =====================================================

-- Documents - Store knowledge base documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(500), -- URL, file path, etc.
    doc_type VARCHAR(50), -- api_doc, code_example, tutorial, etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks - For RAG retrieval
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    tokens INTEGER,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Code examples - Curated code snippets
CREATE TABLE code_examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    tags VARCHAR(100)[],
    use_cases TEXT[],
    difficulty VARCHAR(20), -- beginner, intermediate, advanced
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SEARCH & RETRIEVAL
-- =====================================================

-- Search history
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    results_returned INTEGER,
    search_type VARCHAR(50), -- semantic, keyword, hybrid
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PERFORMANCE & ANALYTICS
-- =====================================================

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    model VARCHAR(100),
    api_key_index INTEGER,
    tokens_input INTEGER,
    tokens_output INTEGER,
    total_cost DECIMAL(10, 6),
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    category VARCHAR(50), -- accuracy, helpfulness, code_quality, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Conversations indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Messages indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Vector similarity indexes (using HNSW for fast approximate nearest neighbor search)
CREATE INDEX idx_messages_embedding ON messages USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_code_artifacts_embedding ON code_artifacts USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_code_examples_embedding ON code_examples USING hnsw (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX idx_messages_content_fts ON messages USING gin(to_tsvector('english', content));
CREATE INDEX idx_documents_content_fts ON documents USING gin(to_tsvector('english', content));
CREATE INDEX idx_code_artifacts_code_fts ON code_artifacts USING gin(to_tsvector('english', code));

-- Agent execution indexes
CREATE INDEX idx_agent_executions_conversation_id ON agent_executions(conversation_id);
CREATE INDEX idx_agent_executions_agent_id ON agent_executions(agent_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_created_at ON agent_executions(created_at DESC);

-- Tasks indexes
CREATE INDEX idx_tasks_conversation_id ON tasks(conversation_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);

-- Trigram indexes for fuzzy search
CREATE INDEX idx_messages_content_trgm ON messages USING gin(content gin_trgm_ops);
CREATE INDEX idx_code_artifacts_code_trgm ON code_artifacts USING gin(code gin_trgm_ops);

-- =====================================================
-- FUNCTIONS FOR RAG QUERIES
-- =====================================================

-- Semantic search for messages
CREATE OR REPLACE FUNCTION search_messages(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        messages.id,
        messages.content,
        1 - (messages.embedding <=> query_embedding) as similarity
    FROM messages
    WHERE 1 - (messages.embedding <=> query_embedding) > match_threshold
    ORDER BY messages.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Semantic search for code artifacts
CREATE OR REPLACE FUNCTION search_code(
    query_embedding vector(1536),
    target_language VARCHAR(50) DEFAULT NULL,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    filename VARCHAR(500),
    language VARCHAR(50),
    code TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        code_artifacts.id,
        code_artifacts.filename,
        code_artifacts.language,
        code_artifacts.code,
        1 - (code_artifacts.embedding <=> query_embedding) as similarity
    FROM code_artifacts
    WHERE 
        (target_language IS NULL OR code_artifacts.language = target_language)
        AND 1 - (code_artifacts.embedding <=> query_embedding) > match_threshold
    ORDER BY code_artifacts.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Hybrid search (semantic + keyword)
CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_text TEXT,
    query_embedding vector(1536),
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    chunk_text TEXT,
    combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT
            document_chunks.id,
            document_chunks.chunk_text,
            1 - (document_chunks.embedding <=> query_embedding) as semantic_score
        FROM document_chunks
        ORDER BY document_chunks.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    keyword_search AS (
        SELECT
            document_chunks.id,
            document_chunks.chunk_text,
            ts_rank(to_tsvector('english', document_chunks.chunk_text), plainto_tsquery('english', query_text)) as keyword_score
        FROM document_chunks
        WHERE to_tsvector('english', document_chunks.chunk_text) @@ plainto_tsquery('english', query_text)
        LIMIT match_count * 2
    )
    SELECT
        COALESCE(s.id, k.id) as id,
        COALESCE(s.chunk_text, k.chunk_text) as chunk_text,
        (COALESCE(s.semantic_score, 0) * 0.7 + COALESCE(k.keyword_score, 0) * 0.3) as combined_score
    FROM semantic_search s
    FULL OUTER JOIN keyword_search k ON s.id = k.id
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Get conversation context with recent messages
CREATE OR REPLACE FUNCTION get_conversation_context(
    conv_id UUID,
    message_limit int DEFAULT 20
)
RETURNS TABLE (
    role VARCHAR(20),
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        messages.role,
        messages.content,
        messages.created_at
    FROM messages
    WHERE messages.conversation_id = conv_id
    ORDER BY messages.created_at DESC
    LIMIT message_limit;
END;
$$;

-- =====================================================
-- TRIGGERS FOR AUTO-UPDATES
-- =====================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subtasks_updated_at BEFORE UPDATE ON subtasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEED DATA - Initialize 3-agent HECTIC SWARM
-- =====================================================

INSERT INTO agents (name, role, description, api_key_index, system_prompt) VALUES
(
    'Agent 1 - Strategic Planner',
    'planner',
    'Orchestrator that creates high-level plans and blueprints for complex tasks',
    1,
    'You are Agent 1, the Strategic Planner in a HECTIC 3-AGENT SWARM. Your role is to create comprehensive execution plans, identify dependencies, and architect solutions. Fire with precision!'
),
(
    'Agent 2 - Code Blaster',
    'coder',
    'Implementation specialist that generates production-ready code and diffs',
    2,
    'You are Agent 2, the Code Blaster in a HECTIC 3-AGENT SWARM. Your role is to generate clean, production-ready code with proper error handling and tests. Blast code like a machine gun!'
),
(
    'Agent 3 - Bug Hunter',
    'reviewer',
    'Quality assurance specialist that reviews, optimizes, and identifies issues',
    3,
    'You are Agent 3, the Bug Hunter in a HECTIC 3-AGENT SWARM. Your role is to review code, identify vulnerabilities, optimize performance, and flag issues for iteration. Hunt bugs ruthlessly!'
);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Recent conversations with message counts
CREATE VIEW conversation_summary AS
SELECT
    c.id,
    c.title,
    c.user_id,
    c.status,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at,
    c.created_at,
    c.updated_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id;

-- Agent performance metrics
CREATE VIEW agent_performance AS
SELECT
    a.id as agent_id,
    a.name,
    a.role,
    COUNT(ae.id) as total_executions,
    AVG(ae.execution_time_ms) as avg_execution_time_ms,
    AVG(ae.tokens_used) as avg_tokens_used,
    COUNT(CASE WHEN ae.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN ae.status = 'failed' THEN 1 END) as failed_executions,
    COUNT(CASE WHEN ae.confidence_level = 'NUCLEAR' THEN 1 END) as nuclear_confidence_count
FROM agents a
LEFT JOIN agent_executions ae ON a.id = ae.agent_id
GROUP BY a.id, a.name, a.role;

-- =====================================================
-- GRANTS (Adjust based on your auth setup)
-- =====================================================

-- Example: Grant permissions to application role
-- CREATE ROLE ai_chat_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_chat_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ai_chat_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_chat_app;

-- =====================================================
-- NOTES & USAGE
-- =====================================================

/*
RAG Query Example:
------------------
SELECT * FROM hybrid_search_documents(
    'How to implement authentication in Next.js',
    '[your_query_embedding_vector]',
    10
);

Context Retrieval Example:
--------------------------
SELECT * FROM get_conversation_context(
    '[conversation_uuid]',
    20
);

Semantic Code Search Example:
-----------------------------
SELECT * FROM search_code(
    '[code_query_embedding]',
    'typescript',
    0.7,
    5
);

Track Agent Execution:
---------------------
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
) VALUES (...);

*/
