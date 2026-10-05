---
name: agent-memory
description: "When the user asks to 'agent memory', 'persist context', 'cross-session learning', 'memory system', 'agent recall', 'long-term memory', 'short-term memory', 'vector store integration', 'session persistence', 'conversation memory', 'knowledge retention', 'semantic memory', 'episodic memory', 'memory retrieval', 'cross-conversation context', 'agent knowledge base', 'memory architecture', 'context window management', 'w"
license: MIT
metadata:
  version: 1.0.0
  author: ZestStream.ai <josh@zeststream.ai>
  domains: [memory-systems, vector-stores, session-persistence, knowledge-retention, context-management, semantic-search, episodic-memory]
distribution: subscribers
---

# Agent Memory

Design and implement memory systems that give AI agents persistent, searchable, and contextually relevant recall across sessions, tasks, and conversations. Memory is what transforms a stateless LLM into a learning system. Without memory, every agent interaction starts from zero. With memory, agents accumulate expertise.

## Core Principle

**Memory is not storage -- it is retrieval under constraint.** Storing everything is trivial. Retrieving the right 5 facts from 50,000 stored memories within a 128K context window, ranked by relevance to the current task, with recency and importance weighting -- that is the hard problem. Design memory systems for retrieval quality, not storage volume.

## When to Use

- When agents need to remember decisions from previous sessions
- When agents should learn from past successes and failures
- When context windows are insufficient for task complexity
- When multiple agents need shared knowledge
- When agents interact with the same customers/systems repeatedly
- When building agent expertise over time
- When implementing RAG pipelines for agent context
- When optimizing context window usage for cost and quality
- When agents need to remember user preferences or project conventions

## Memory Architecture

```
                    [Agent]
                      |
            [Working Memory (context window)]
              /         |         \
    [Short-term]   [Episodic]   [Semantic]
    (session)      (experiences) (facts/knowledge)
        |              |              |
    [Session DB]  [Vector Store]  [Knowledge Graph]
        |              |              |
    TTL: hours    TTL: weeks     TTL: permanent
```

### Memory Types

| Type | Duration | Content | Retrieval | Technology |
|------|----------|---------|-----------|------------|
| **Working** | Current context | Active task state | Direct (in prompt) | Context window |
| **Short-term** | Session (hours) | Conversation history, temp state | Recency-based | Redis, SQLite |
| **Episodic** | Medium (weeks) | Task outcomes, decisions, errors | Similarity search | Qdrant, Pinecone |
| **Semantic** | Long-term (permanent) | Facts, patterns, domain knowledge | Hybrid BM25+vector | Qdrant + SQLite FTS |
| **Procedural** | Permanent | How-to knowledge, workflows | Pattern matching | Structured YAML/JSON |

Run the memory system manager:
```bash
python3 ~/.claude/skills/agent-memory/scripts/memory_manager.py \
  --config /path/to/memory-config.yaml

# Store a memory
python3 ~/.claude/skills/agent-memory/scripts/memory_manager.py \
  --store --agent-id agent-007 --type episodic \
  --content "Deploying to staging requires VPN access" --json

# Retrieve relevant memories for a task
python3 ~/.claude/skills/agent-memory/scripts/memory_manager.py \
  --retrieve --agent-id agent-007 --query "deploy to staging" --top-k 5

# Consolidate and prune memories
python3 ~/.claude/skills/agent-memory/scripts/memory_manager.py \
  --consolidate --agent-id agent-007 --strategy importance-weighted
```

## Memory Storage Strategies

### 1. Raw Storage (Append-Only)

```python
# Every interaction stored verbatim
memory_entry = {
    "timestamp": "2026-03-19T14:30:00Z",
    "agent_id": "agent-007",
    "session_id": "sess-123",
    "type": "episodic",
    "content": "Customer prefers email over Slack for updates",
    "embedding": [0.12, -0.34, ...],  # 256d or 1024d
    "metadata": {
        "task_id": "bd-456",
        "confidence": 0.92,
        "source": "customer_interaction"
    }
}
```

### 2. Summarized Storage (Consolidated)

```python
# Periodic consolidation of raw memories into summaries
consolidation_entry = {
    "timestamp": "2026-03-19T00:00:00Z",
    "agent_id": "agent-007",
    "type": "semantic",
    "content": "Customer X: prefers email, budget-conscious, technical background",
    "source_count": 15,  # Consolidated from 15 raw memories
    "confidence": 0.88,  # Average confidence of sources
    "last_updated": "2026-03-18T16:00:00Z"
}
```

### 3. Structured Knowledge (Graph)

```python
# Entities and relationships
knowledge_triple = {
    "subject": "customer:X",
    "predicate": "prefers_channel",
    "object": "email",
    "confidence": 0.92,
    "evidence": ["mem-001", "mem-015", "mem-023"]
}
```

## Retrieval Strategies

| Strategy | When | How |
|----------|------|-----|
| **Recency** | Recent context matters most | Sort by timestamp, return N most recent |
| **Similarity** | Semantic relevance to current task | Vector similarity search (cosine/dot product) |
| **Hybrid** | Balance recency and relevance | BM25 + vector similarity, weighted combination |
| **Importance** | Critical facts regardless of recency | Importance score (manual or frequency-based) |
| **Contextual** | Task-type specific recall | Filter by metadata (task_type, domain, project) |
| **Associative** | Related memories through connections | Graph traversal from seed memory |

### Hybrid Retrieval (Recommended)

```python
def retrieve_memories(query: str, agent_id: str, top_k: int = 5):
    # 1. Vector similarity (semantic relevance)
    vector_results = vector_store.search(
        query_embedding=embed(query),
        filter={"agent_id": agent_id},
        top_k=top_k * 3  # Over-fetch for reranking
    )

    # 2. BM25 keyword match (exact term relevance)
    bm25_results = fts_store.search(
        query=query,
        filter={"agent_id": agent_id},
        top_k=top_k * 3
    )

    # 3. Reciprocal Rank Fusion
    fused = reciprocal_rank_fusion(vector_results, bm25_results, k=60)

    # 4. Recency boost (exponential decay)
    for result in fused:
        age_days = (now() - result.timestamp).days
        result.score *= exp(-0.01 * age_days)

    # 5. Return top-k
    return sorted(fused, key=lambda r: r.score, reverse=True)[:top_k]
```

## Context Window Optimization

| Technique | Savings | Quality Impact |
|-----------|---------|----------------|
| **Summarize old messages** | 60-80% | Minimal if done well |
| **Retrieve relevant memories only** | 70-90% | Better than full history |
| **Compress code blocks** | 30-50% | Lossy for implementation details |
| **Prune irrelevant context** | 40-60% | Risk of dropping needed info |
| **Hierarchical summarization** | 80-95% | Best for long conversations |

## Memory Lifecycle

```
CREATE -> STORE -> INDEX -> RETRIEVE -> USE -> CONSOLIDATE -> ARCHIVE/PRUNE
  |         |        |         |         |         |              |
  v         v        v         v         v         v              v
Generate  Persist  Embed+   Query    Inject    Merge         TTL expiry
memory    to DB    BM25     match    into      duplicates    or manual
                   index    + rank   prompt    + summarize   removal
```

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Storing everything verbatim | Memory store grows unbounded, retrieval degrades | Consolidation strategy with TTL and importance scoring |
| No retrieval filtering | Irrelevant memories injected into context | Filter by agent_id, task_type, project, recency |
| Treating all memories equally | Critical facts buried under trivial observations | Importance scoring with manual boost for key memories |
| No memory validation | Hallucinated or incorrect memories persist | Confidence scoring, periodic human review, contradiction detection |
| Embedding-only retrieval | Misses keyword-relevant results | Hybrid retrieval (BM25 + vector + recency) |
| No memory isolation between agents | Agent A sees Agent B's private context | Strict agent_id filtering, tenant isolation |
| Context window stuffing | Entire memory store dumped into prompt | Retrieve top-k relevant memories, respect token budget |
| No consolidation | 1000 memories saying the same thing | Periodic deduplication and summarization |
| Ignoring memory freshness | Stale information overrides current context | Recency weighting, explicit invalidation on updates |
| No memory provenance | Cannot trace where a memory came from | Source tracking (session_id, task_id, timestamp) |

## Implementation Checklist

- [ ] Memory types defined (working, short-term, episodic, semantic, procedural)
- [ ] Vector store selected and deployed (Qdrant recommended for self-hosted)
- [ ] Embedding model selected (256d minimum for agent memory)
- [ ] Hybrid retrieval implemented (BM25 + vector + recency weighting)
- [ ] Memory isolation enforced per agent and per tenant
- [ ] Consolidation strategy defined (dedup, summarize, prune schedule)
- [ ] Context window budget allocated (reserve tokens for memory injection)
- [ ] Memory provenance tracked (source session, task, timestamp, confidence)
- [ ] TTL configured per memory type (hours for short-term, weeks for episodic)
- [ ] Importance scoring implemented for critical fact prioritization

## Decision Framework: Memory System Selection

```
What does the agent need to remember?
  |
  +-> Current conversation context?
  |     -> Working memory (context window)
  |     -> Summarize if conversation exceeds 50% of window
  |
  +-> Facts about entities (customers, systems)?
  |     -> Semantic memory (knowledge graph + vector store)
  |     -> Long TTL, high importance
  |
  +-> Past task outcomes and decisions?
  |     -> Episodic memory (vector store)
  |     -> Medium TTL, similarity retrieval
  |
  +-> How to perform specific procedures?
  |     -> Procedural memory (structured YAML)
  |     -> Permanent, pattern-matched
  |
  +-> Temporary session state?
        -> Short-term memory (Redis/SQLite)
        -> Auto-expire after session
```

## Key References

Consult these for implementation details:

- **`references/sources.md`** -- Memory system research, vector store benchmarks, retrieval strategy papers
- **`references/vector-store-comparison.md`** -- Detailed comparison of Qdrant, Pinecone, Weaviate, ChromaDB with benchmarks
- **`examples/memory-config.yaml`** -- Complete memory system configuration with all memory types

## Related Skills

- **agent-orchestration** -- For shared memory across orchestrated agent workflows
- **agent-evaluation** -- For measuring memory retrieval quality
- **information-retrieval** -- For advanced retrieval strategies and RAG patterns
- **multi-document-rag** -- For document-based memory and retrieval
