# RAG Pipeline — Week 1

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT: User Question                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  1. LOAD & CHUNK                        │
        │  - Load corpus (.txt)                   │
        │  - Split: 1000 chars, 200 overlap       │
        │  - Result: 21 chunks                    │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  2. EMBED                               │
        │  - Embed all chunks (Cohere embed-v4)   │
        │  - Store: numpy array (21 × 1024)       │
        │  - Embed query with same model          │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  3. SEARCH                              │
        │  - Cosine similarity: query vs all      │
        │  - Sort descending, take top-k (k=3)    │
        │  - Return: chunk_id, text, score        │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  4. ANSWER (Step 4: Prompt Rewrite)     │
        │  - System prompt (strict rules)         │
        │  - Context: [chunk N] text...           │
        │  - Query: question                      │
        │  - Model: Claude Haiku, temp=1.0        │
        │  - Output: LLM response                 │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  5. CITE & EVALUATE                     │
        │  - Print answer + sources               │
        │  - Human review: correct? faithful?     │
        │  - Repeat 2–3x (temperature variance)   │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │  6. ITERATE (if needed)                 │
        │  - Adjust: k, prompt, chunk size        │
        │  - Rerun tests                          │
        │  - Record improvements                  │
        └─────────────────────────────────────────┘
```

**Key Changes (Week 1, Step 4):**
- System prompt now enforces: no outside knowledge, no referrals, no "cut off" claims, keep it short
- Citations now include chunk ID for traceability
- Empty hits handled gracefully 