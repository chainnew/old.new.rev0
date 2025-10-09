-- =====================================================
-- Migration 001: Optimize Vector Indexes for RAG
-- Run this after initial schema setup to optimize performance
-- =====================================================

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- VECTOR INDEX OPTIMIZATION
-- =====================================================

-- Drop old HNSW indexes if they exist (to recreate with better parameters)
DROP INDEX IF EXISTS idx_messages_embedding;
DROP INDEX IF EXISTS idx_document_chunks_embedding;
DROP INDEX IF EXISTS idx_code_artifacts_embedding;
DROP INDEX IF EXISTS idx_code_examples_embedding;

-- Create optimized HNSW indexes for vector similarity
-- HNSW parameters:
--   m = 16 (default, max connections per layer)
--   ef_construction = 64 (higher = better recall, slower build)

CREATE INDEX idx_messages_embedding 
ON messages 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_document_chunks_embedding 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_code_artifacts_embedding 
ON code_artifacts 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_code_examples_embedding 
ON code_examples 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

COMMENT ON INDEX idx_messages_embedding IS 
'Optimized HNSW index for message embeddings (cosine similarity)';

COMMENT ON INDEX idx_code_artifacts_embedding IS 
'Optimized HNSW index for code artifact embeddings (cosine similarity)';

-- Alternative: IVFFlat indexes (faster build, slightly lower recall)
-- Uncomment if you prefer IVFFlat over HNSW:
/*
DROP INDEX IF EXISTS idx_messages_embedding;
DROP INDEX IF EXISTS idx_code_artifacts_embedding;

-- IVFFlat: Divide space into lists (100 lists for ~10k vectors)
CREATE INDEX idx_messages_embedding 
ON messages 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_code_artifacts_embedding 
ON code_artifacts 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
*/

-- =====================================================
-- ADDITIONAL PERFORMANCE INDEXES
-- =====================================================

-- Code artifacts: Composite index for filtered searches
CREATE INDEX IF NOT EXISTS idx_code_artifacts_lang_conv 
ON code_artifacts(language, conversation_id);

-- Code artifacts: B-tree on file path for exact lookups
CREATE INDEX IF NOT EXISTS idx_code_artifacts_filename 
ON code_artifacts(filename);

-- Agent executions: Composite for time-series queries
CREATE INDEX IF NOT EXISTS idx_agent_executions_conv_time 
ON agent_executions(conversation_id, created_at DESC);

-- Tasks: Composite for status + conversation filtering
CREATE INDEX IF NOT EXISTS idx_tasks_status_conv 
ON tasks(status, conversation_id);

-- Messages: Composite for conversation + time
CREATE INDEX IF NOT EXISTS idx_messages_conv_time 
ON messages(conversation_id, created_at DESC);

-- =====================================================
-- PARTIAL INDEXES (Index only relevant rows)
-- =====================================================

-- Only index active conversations
CREATE INDEX IF NOT EXISTS idx_conversations_active 
ON conversations(user_id, created_at DESC) 
WHERE status = 'active';

-- Only index failed agent executions for debugging
CREATE INDEX IF NOT EXISTS idx_agent_executions_failed 
ON agent_executions(agent_id, created_at DESC) 
WHERE status = 'failed';

-- Only index code artifacts with embeddings
CREATE INDEX IF NOT EXISTS idx_code_artifacts_with_embedding 
ON code_artifacts(conversation_id, language) 
WHERE embedding IS NOT NULL;

-- =====================================================
-- STATISTICS & MAINTENANCE
-- =====================================================

-- Update table statistics for query planner
ANALYZE messages;
ANALYZE code_artifacts;
ANALYZE document_chunks;
ANALYZE agent_executions;
ANALYZE tasks;

-- Vacuum tables to reclaim space
VACUUM ANALYZE messages;
VACUUM ANALYZE code_artifacts;
VACUUM ANALYZE document_chunks;

-- =====================================================
-- PERFORMANCE TUNING SETTINGS (optional)
-- =====================================================

-- Increase work_mem for vector operations (per connection)
-- SET work_mem = '256MB';

-- Increase maintenance_work_mem for index builds
-- SET maintenance_work_mem = '1GB';

-- Set effective_cache_size (should be ~75% of system RAM)
-- ALTER SYSTEM SET effective_cache_size = '4GB';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check index usage
/*
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
*/

-- Check table sizes
/*
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
*/

-- Test vector search performance
/*
EXPLAIN ANALYZE
SELECT 
    id,
    filename,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM code_artifacts
WHERE 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) > 0.7
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
*/

COMMIT;
