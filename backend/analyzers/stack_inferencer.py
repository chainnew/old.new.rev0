"""
Stack Inference Engine: Automatic technology stack selection via pgvector similarity.

Phase 1C: Implements A2 (Stack Inference) with:
- OpenAI embeddings for scope → stack matching
- PostgreSQL + pgvector for similarity search
- Confidence scoring + fallback to Grok-4-Fast
- Integration with PlannerAI for auto-fill

Usage:
    # Seed embeddings (one-time setup)
    python stack_inferencer.py --seed-embeddings

    # Infer stack from scope
    from stack_inferencer import infer_stack
    result = infer_stack("Build a todo app with Python backend")
    # => {'backend': 'Python/FastAPI', 'confidence': 0.85, ...}
"""
import os
import numpy as np
import psycopg
from psycopg.rows import dict_row
from openai import OpenAI
from typing import Dict, List, Any, Optional
from telemetry import get_tracer
from dotenv import load_dotenv
import json
import argparse

load_dotenv()

# OpenRouter client for embeddings (via OpenAI-compatible API)
OPENROUTER_KEY = (
    os.getenv('OPENROUTER_API_KEY') or
    os.getenv('OPENROUTER_API_KEY1') or
    os.getenv('OPENROUTER_API_KEY2')
)

if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment")

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# PostgreSQL connection (assumes PG16 with pgvector installed)
PG_CONNECTION = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/hive_mind'
)

# Inference config
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI (via OpenRouter)
SIMILARITY_THRESHOLD = 0.7  # Min cosine similarity for auto-select
TOP_K = 3  # Number of similar templates to retrieve

tracer = get_tracer()


def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI.

    Args:
        text: Input text to embed (e.g., project scope description)

    Returns:
        1536-dimensional embedding vector
    """
    with tracer.start_as_current_span("stack_inference.embed_text") as span:
        span.set_attribute("text.length", len(text))

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )

        embedding = response.data[0].embedding
        span.set_attribute("embedding.dims", len(embedding))

        return embedding


def infer_stack(scope: str, user_hints: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Infer technology stack from project scope using pgvector similarity search.

    Args:
        scope: Project description/scope (e.g., "Build e-commerce site with Python")
        user_hints: Optional constraints (e.g., {"backend": "Python", "frontend": "React"})

    Returns:
        {
            "backend": "Python/FastAPI",
            "frontend": "React + Vite",
            "database": "PostgreSQL",
            "auth": "Clerk",
            "deployment": "Railway + Vercel",
            "rationale": "Matched 'FastAPI + React' (0.85 similarity): ...",
            "confidence": 0.85,
            "template_title": "FastAPI + React"
        }
    """
    with tracer.start_as_current_span("stack_inference.infer") as span:
        span.set_attribute("scope.length", len(scope))
        span.set_attribute("has_hints", bool(user_hints))

        # Step 1: Embed the scope
        scope_embedding = embed_text(scope)

        # Step 2: Query pgvector for similar stacks
        with psycopg.connect(PG_CONNECTION, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Cosine similarity search (1 - cosine_distance = similarity)
                cur.execute("""
                    SELECT
                        title,
                        kind,
                        stack,
                        rationale,
                        tags,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM stack_templates
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (scope_embedding, scope_embedding, TOP_K))

                results = cur.fetchall()

        span.set_attribute("results.count", len(results))

        if not results:
            # Fallback: No templates found (shouldn't happen with seed data)
            return _fallback_to_grok(scope, user_hints)

        # Step 3: Check top match confidence
        top_match = results[0]
        similarity = top_match['similarity']

        span.set_attribute("top_match.title", top_match['title'])
        span.set_attribute("top_match.similarity", similarity)

        if similarity >= SIMILARITY_THRESHOLD:
            # High confidence match - use template
            stack = top_match['stack']
            rationale = (
                f"Matched '{top_match['title']}' ({similarity:.2f} similarity): "
                f"{top_match['rationale']}"
            )

            # Apply user hints (override template)
            if user_hints:
                stack.update(user_hints)
                rationale += f" | Overridden with user hints: {user_hints}"

            span.set_attribute("inference.method", "template")
            span.set_attribute("inference.confidence", similarity)

            return {
                **stack,
                "rationale": rationale,
                "confidence": float(similarity),
                "template_title": top_match['title'],
                "template_kind": top_match['kind'],
                "template_tags": top_match['tags']
            }

        else:
            # Low confidence - fallback to Grok-4-Fast for custom inference
            span.set_attribute("inference.method", "grok_fallback")
            return _fallback_to_grok(scope, user_hints, low_match=top_match)


def _fallback_to_grok(
    scope: str,
    user_hints: Optional[Dict] = None,
    low_match: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Fallback to Grok-4-Fast for custom stack inference when templates don't match.

    Args:
        scope: Project scope
        user_hints: User constraints
        low_match: Best template match (if any, for context)

    Returns:
        Inferred stack dict
    """
    prompt = f"""You are a technology stack expert. Infer the best production-ready stack for this project:

Scope: "{scope}"

User Constraints: {json.dumps(user_hints) if user_hints else 'None'}

{f"Reference (low similarity): {low_match['title']} - {low_match['stack']}" if low_match else ""}

**Output JSON** with these fields:
{{
  "backend": "Framework (e.g., FastAPI, Node/Express)",
  "frontend": "Framework (e.g., Next.js, React + Vite)",
  "database": "Database (e.g., PostgreSQL, MongoDB)",
  "auth": "Auth service (e.g., Clerk, NextAuth)" (optional),
  "deployment": "Hosting (e.g., Vercel, Railway)" (optional),
  "rationale": "Why this stack fits the scope (1-2 sentences)"
}}

Return ONLY valid JSON, no markdown."""

    response = client.chat.completions.create(
        model="x-ai/grok-4-fast",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    try:
        content = response.choices[0].message.content.strip()

        # Clean markdown if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        stack = json.loads(content)
        stack['confidence'] = 0.6  # Default for Grok fallback
        stack['template_title'] = 'Custom (Grok-4-Fast)'
        stack['template_kind'] = 'custom'

        return stack

    except json.JSONDecodeError as e:
        # Last resort fallback
        print(f"⚠️ JSON parse error in Grok fallback: {e}")
        return {
            "backend": "Node/Express",
            "frontend": "React",
            "database": "PostgreSQL",
            "rationale": "Default stack (Grok inference failed)",
            "confidence": 0.5,
            "template_title": "Default Fallback"
        }


def seed_embeddings():
    """
    Generate and update embeddings for all stack templates (one-time setup).

    Run: python stack_inferencer.py --seed-embeddings
    """
    print("🌱 Seeding embeddings for stack templates...")

    with psycopg.connect(PG_CONNECTION, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Get all templates without real embeddings
            cur.execute("SELECT id, title, rationale, tags FROM stack_templates")
            templates = cur.fetchall()

            print(f"   Found {len(templates)} templates\n")

            for i, template in enumerate(templates, 1):
                # Combine title + rationale + tags for richer embedding
                text = (
                    f"{template['title']}. {template['rationale']}. "
                    f"Tags: {', '.join(template['tags']) if template['tags'] else 'None'}"
                )

                print(f"   [{i}/{len(templates)}] Embedding: {template['title']}")
                embedding = embed_text(text)

                # Update DB
                cur.execute("""
                    UPDATE stack_templates
                    SET embedding = %s::vector
                    WHERE id = %s
                """, (embedding, template['id']))

                conn.commit()

    print("\n✅ Embeddings seeded successfully!")
    print("   Test with: python stack_inferencer.py --test\n")


def test_inference():
    """Test stack inference with sample scopes."""
    test_scopes = [
        "Build a todo app with Python backend and modern UI",
        "E-commerce store with real-time inventory and Stripe payments",
        "Serverless blog with user authentication",
        "Task management dashboard like Trello with Next.js"
    ]

    print("🧪 Testing stack inference...\n")

    for i, scope in enumerate(test_scopes, 1):
        print(f"[{i}] Scope: {scope}")
        result = infer_stack(scope)
        print(f"    Backend: {result.get('backend')}")
        print(f"    Frontend: {result.get('frontend')}")
        print(f"    Confidence: {result.get('confidence', 0):.2f}")
        print(f"    Matched: {result.get('template_title')}")
        print(f"    Rationale: {result.get('rationale', 'N/A')[:80]}...\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Stack Inference Engine")
    parser.add_argument('--seed-embeddings', action='store_true', help='Generate embeddings for templates')
    parser.add_argument('--test', action='store_true', help='Run test inferences')

    args = parser.parse_args()

    if args.seed_embeddings:
        seed_embeddings()
    elif args.test:
        test_inference()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
