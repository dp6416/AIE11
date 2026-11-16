# Test Questions — Week 1 RAG Challenge

| # | Question | Kind | Purpose |
|---|----------|------|---------|
| 1 | Does creatine help deliver a better performance? | Decline, far miss | Test refusal on out-of-corpus topics |
| 2 | How many repetitions of chin tucks should I do, and for how long? | Lookup | Single-chunk exact answer |
| 3 | When is the latest time I should drink caffeine? | Lookup | Single-chunk exact answer |
| 4 | What is a good grounding technique? | Lookup (duplicated) | Fact appears in multiple chunks |
| 5 | What is essential for good immune function? | Needs 2 chunks | Answer split across non-adjacent chunks |
| 6 | Should I move every day? | Needs 2 chunks (conflict) | Two chunks give conflicting signals |
| 7 | Should I breathe fast or box-breathe before bed? | Needs 2 chunks + decline | Partial answer; must decline one part |
| 8 | Do you recommend fasting or intermittent fasting? | Near-miss decline | Similar topic, in-domain noise |
| 9 | Should I sleep longer than 9 hours? | Near-miss edge | Edge case: answer threshold question |
| 10 | How many grams of protein should I eat per day? | Near-miss decline | Related fact exists but not exact answer |
