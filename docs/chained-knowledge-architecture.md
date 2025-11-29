# Chained Knowledge Architecture

> Drop this file into your repo or hand it directly to Copilot. It explains how the Chained learning system works, how embeddings and (optionally) a vector database power retrieval, and how to wire the pieces into base instructions, agents, and tools.

## 1. Overview

The Chained repository uses long-term "learning" files to capture persistent knowledge: durable ideas, world-model updates, article notes, experiments, workflows, and architecture insights. Each learning is a single JSON document stored under `/learning`, giving agents and workflows a structured, evolvable memory layer.

This document covers:

- The Learning JSON format
- How embeddings represent and index knowledge
- How to connect this memory to Copilot base instructions
- How agents query the memory via a tool
- An optional vector database upgrade for scalable semantic search

## 2. Learning JSON Files

All learnings live at `/learning/*.json`, with one conceptual unit per file using a consistent schema:

```json
{
  "id": "2025-11-25-hackernews-llm-routing",
  "title": "LLM Routing with Specialized Agents",
  "source": "https://news.ycombinator.com/item?id=12345",
  "type": "article | idea | experiment | workflow | concept",
  "summary": "Short accessible explanation of the learning.",
  "raw_notes": "Longer thoughts, interpretations, implications...",
  "embedding": {
    "model": "openai/text-embedding-3-small",
    "vector": [/* dense numeric vector */]
  }
}
```

Rules and conventions:

- `id` must be stable and unique.
- `summary` and `raw_notes` should be self-contained and canonical.
- `embedding` can be missing for new files; a workflow will generate it.

## 3. Embedding Generation (Semantic Fingerprinting)

Each learning is represented by a semantic embedding—a dense vector fingerprint—generated from the combined `title`, `summary`, and `raw_notes` fields. These embeddings enable semantic search, clustering, duplicate detection, agent mission alignment, and retrieval-augmented generation (RAG).

**Workflow outline**

1. Detect new or changed learning JSON files.
2. Call the GitHub Models `/embeddings` API (e.g., `openai/text-embedding-3-small`).
3. Compute or refresh the embedding.
4. Write the vector back to the file or to an index alongside the repo.

## 4. Copilot Base Instructions Integration

Add the following behaviors to Copilot's repo-level base instructions:

- Treat `/learning/*.json` as the canonical world model for this repository.
- When answering architecture, workflow, agent, or design questions, consult relevant learnings using `summary` and `raw_notes` as authoritative context.
- When new concepts appear, propose creating new learning JSON files that follow the schema.
- Prefer reusing existing learnings instead of inventing new concepts.

**Copilot should *not*:**

- Generate embeddings itself.
- Persist embeddings outside the established workflow.
- Invent or hallucinate new learnings.

## 5. Copilot Agent Integration

Agents rely on tools to make the knowledge system actionable.

**Tool: `search_learnings(query)`**

- Embed the query.
- Compare the query embedding with stored learning embeddings (local files or vector DB).
- Return the top relevant learnings (IDs and key fields).

**Agent behavior rules**

- Before answering complex questions about world models, architecture, workflows, agent systems, or the evolution of "Chained," the agent must call `search_learnings(query)`.
- Use `summary` and `raw_notes` from returned learnings as context and cite learnings by `id` in reasoning.
- Suggest creating new learnings when novel ideas surface, avoiding duplication when related learnings already exist.

## 6. Optional Vector Database Layer (Recommended)

For more than ~200 learnings—or multi-repo knowledge—add a vector database to accelerate and scale semantic search.

**Why add a vector DB?**

- Fast similarity search without scanning JSON files.
- Scalability to thousands or millions of learnings.
- Metadata filtering (e.g., by `type`, date, tags).
- Private, persistent storage even for public or ephemeral repos.
- Cross-repo and time-aware retrieval to enrich RAG pipelines.

**Options:** pgvector (Postgres), Qdrant, Pinecone, Weaviate, or ChromaDB.

**Reference architecture**

```
User → Agent → search_learnings(query)
      → embed → vector DB similarity search
      → return top-K learnings (IDs + summaries)
      → Agent uses them as context
```

Store the embedding in the repo for transparency; keep the index in the vector DB for speed and scale.

## 7. Putting It All Together

- 🟦 **Base instructions:** Tell Copilot, "This repo has a knowledge system in `/learning`. Use it when reasoning."
- 🟧 **Agent instructions:** Tell agents, "Use the `search_learnings` tool to retrieve context via embeddings."
- 🟩 **Embedding workflow:** A GitHub Action maintains embeddings automatically.
- 🟪 **Optional vector DB:** Scales and accelerates semantic retrieval across time and repos.

Result: Chained gains a persistent, evolving world model that combines local JSON knowledge, semantic embeddings, vector search, and agent-aware RAG. Hand this file to Copilot and prompt: "Generate a full document, workflows, code, and agents based on this."
