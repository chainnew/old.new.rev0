"""
RAG Engine with Vector Embeddings
Supports hybrid search (semantic + keyword) with PostgreSQL + pgvector
"""
import os
from typing import List, Dict, Any, Optional
import tiktoken

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import pgvector
    from pgvector.psycopg2 import register_vector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ psycopg2/pgvector not installed - RAG unavailable")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class RAGEngine:
    """
    Retrieval-Augmented Generation engine
    - Generate embeddings via OpenAI
    - Store in PostgreSQL with pgvector
    - Hybrid search (vector + full-text)
    """
    
    def __init__(self, embedding_model: str = "text-embedding-ada-002"):
        if not DB_AVAILABLE:
            raise ImportError("psycopg2 and pgvector required for RAG")
        
        self.embedding_model = embedding_model
        self.embedding_dim = 1536  # OpenAI ada-002
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # OpenAI client (for embeddings)
        if OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else:
            self.openai_client = None
            print("⚠️ OpenAI client not available - embeddings disabled")
        
        print(f"🔍 RAG Engine initialized (model: {embedding_model})")
    
    def _get_connection(self):
        """Get database connection"""
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        register_vector(conn)  # Register pgvector types
        return conn
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (1536 dimensions)
        """
        if not self.openai_client:
            # Return dummy embedding for testing
            return [0.0] * self.embedding_dim
        
        try:
            # Truncate to token limit (8191 for ada-002)
            tokens = self.tokenizer.encode(text)[:8000]
            text = self.tokenizer.decode(tokens)
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return [0.0] * self.embedding_dim
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    async def store_document_chunks(
        self, 
        document_id: str,
        content: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> int:
        """
        Chunk document and store with embeddings
        
        Args:
            document_id: Document UUID
            content: Full document text
            chunk_size: Tokens per chunk
            overlap: Token overlap between chunks
            
        Returns:
            Number of chunks created
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Tokenize
            tokens = self.tokenizer.encode(content)
            
            # Chunk with overlap
            chunks = []
            for i in range(0, len(tokens), chunk_size - overlap):
                chunk_tokens = tokens[i:i + chunk_size]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                chunks.append((chunk_text, len(chunk_tokens), i // (chunk_size - overlap)))
            
            # Store chunks with embeddings
            for chunk_text, token_count, chunk_idx in chunks:
                embedding = self.generate_embedding(chunk_text)
                
                cur.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, tokens, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                """, (document_id, chunk_text, chunk_idx, token_count, embedding))
            
            conn.commit()
            print(f"✅ Stored {len(chunks)} chunks for document {document_id}")
            return len(chunks)
            
        finally:
            cur.close()
            conn.close()
    
    async def store_code_artifact(
        self,
        conversation_id: str,
        filename: str,
        language: str,
        code: str,
        description: str = ""
    ) -> str:
        """
        Store code artifact with embedding
        
        Args:
            conversation_id: Conversation UUID
            filename: File name
            language: Programming language
            code: Source code
            description: Optional description
            
        Returns:
            Artifact ID
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Generate embedding
            # Combine filename + description + code for better semantic search
            embed_text = f"{filename}\n{description}\n{code[:5000]}"
            embedding = self.generate_embedding(embed_text)
            
            line_count = code.count('\n') + 1
            
            cur.execute("""
                INSERT INTO code_artifacts 
                (conversation_id, filename, language, code, description, line_count, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (conversation_id, filename, language, code, description, line_count, embedding))
            
            artifact_id = cur.fetchone()[0]
            conn.commit()
            
            print(f"✅ Stored code artifact: {filename} ({line_count} lines)")
            return str(artifact_id)
            
        finally:
            cur.close()
            conn.close()
    
    async def semantic_search_code(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for code artifacts
        
        Args:
            query: Search query
            language: Filter by language (optional)
            limit: Max results
            min_similarity: Minimum cosine similarity
            
        Returns:
            List of matching code artifacts
        """
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Use pgvector cosine similarity
            if language:
                cur.execute("""
                    SELECT 
                        id,
                        filename,
                        language,
                        code,
                        description,
                        line_count,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM code_artifacts
                    WHERE language = %s
                        AND 1 - (embedding <=> %s::vector) > %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, language, query_embedding, min_similarity, query_embedding, limit))
            else:
                cur.execute("""
                    SELECT 
                        id,
                        filename,
                        language,
                        code,
                        description,
                        line_count,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM code_artifacts
                    WHERE 1 - (embedding <=> %s::vector) > %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, min_similarity, query_embedding, limit))
            
            results = cur.fetchall()
            return [dict(row) for row in results]
            
        finally:
            cur.close()
            conn.close()
    
    async def hybrid_search_documents(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search (semantic + keyword)
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            Ranked chunks
        """
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query_embedding = self.generate_embedding(query)
            
            # Use PostgreSQL hybrid_search_documents function
            cur.execute("""
                SELECT * FROM hybrid_search_documents(%s, %s::vector, %s)
            """, (query, query_embedding, limit))
            
            results = cur.fetchall()
            return [dict(row) for row in results]
            
        finally:
            cur.close()
            conn.close()
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation messages
        
        Args:
            conversation_id: Conversation UUID
            limit: Max messages
            
        Returns:
            Recent messages
        """
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT * FROM get_conversation_context(%s, %s)
            """, (conversation_id, limit))
            
            results = cur.fetchall()
            return [dict(row) for row in results]
            
        finally:
            cur.close()
            conn.close()
    
    async def store_architecture_doc(
        self,
        title: str,
        content: str,
        source: str,
        doc_type: str = "architecture"
    ) -> str:
        """
        Store architecture documentation (e.g., ARCHITECTURE_MAP.md)
        
        Args:
            title: Document title
            content: Full content
            source: Source path
            doc_type: Document type
            
        Returns:
            Document ID
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Store document
            cur.execute("""
                INSERT INTO documents (title, content, source, doc_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (title, content, source, doc_type))
            
            doc_id = cur.fetchone()[0]
            conn.commit()
            
            # Chunk and store
            await self.store_document_chunks(str(doc_id), content)
            
            print(f"✅ Stored architecture doc: {title}")
            return str(doc_id)
            
        finally:
            cur.close()
            conn.close()


# ============================================
# Utility Functions
# ============================================

async def index_architecture_map(rag_engine: RAGEngine, arch_map_path: str):
    """Index ARCHITECTURE_MAP.md for RAG"""
    with open(arch_map_path, 'r') as f:
        content = f.read()
    
    await rag_engine.store_architecture_doc(
        title="ETERNA x86 Architecture Mapping",
        content=content,
        source=arch_map_path,
        doc_type="architecture"
    )


async def index_eterna_source(rag_engine: RAGEngine, eterna_path: str):
    """Index key ETERNA source files"""
    import glob
    
    rust_files = glob.glob(f"{eterna_path}/src/**/*.rs", recursive=True)
    
    for file_path in rust_files[:50]:  # Limit for demo
        with open(file_path, 'r') as f:
            code = f.read()
        
        filename = file_path.split('/')[-1]
        
        await rag_engine.store_code_artifact(
            conversation_id="system",
            filename=filename,
            language="rust",
            code=code,
            description=f"ETERNA ARM64 source: {file_path}"
        )
    
    print(f"✅ Indexed {len(rust_files[:50])} Rust files")


if __name__ == "__main__":
    # Test
    import asyncio
    
    async def test_rag():
        rag = RAGEngine()
        
        # Test embedding
        embedding = rag.generate_embedding("Test ARM64 hypervisor code")
        print(f"Embedding dimension: {len(embedding)}")
        
        # Test semantic search
        results = await rag.semantic_search_code("VMCS implementation", language="rust")
        print(f"Found {len(results)} code artifacts")
    
    asyncio.run(test_rag())
