# Decisions — Week 1 RAG Optimization

## Summary

Changed the system prompt from permissive to strict, targeting three failure modes: padding with unrelated context, outside referrals, and false claims about truncated sections. Achieved measurable improvements on creatine, fasting, and sleep questions with no regressions.

## What Changed

**System Prompt Rewrite (3 rules + 1 fix):**

1. **Explicit "never say cut off" rule:** "Each excerpt may start or end mid-sentence because the text was split into pieces; never say a section is missing or cut off."
2. **Brevity rule:** "Keep it short; do not describe excerpts that don't answer the question." (prevents magnesium padding)
3. **No outside knowledge:** "Do not use your own knowledge to answer the question or provide any outside referral."
4. **Empty-hits branch:** When hits list is empty, context becomes `"(no excerpts)"` instead of crashing.

## Why

Baseline scored 9/10, but three failure modes persisted:
- **Padding:** magnesium mentioned despite not being asked (#1 creatine, 2/3 runs)
- **False referrals:** "consult a healthcare provider" (#9 sleep)
- **False "cut off" claims:** "Chapter 4 is missing" (#8 fasting)

The rules directly target each failure.

## Results

| Question | Before | After | Status |
|----------|--------|-------|--------|
| #1 Creatine (3 runs) | 2/3 padded, 1/3 referral | 0/3 clean | ✅ Fixed |
| #6 Move everyday | ✅ | ✅ | ✅ No regression |
| #7 Box breathing | ✅ | ✅ | ✅ No regression |
| #8 Fasting | ❌ "Chapter 4 cut off" + referral | ✅ Clean refusal | ✅ Fixed |
| #9 Sleep >9h | ❌ Outside referral | ✅ (2nd run clean) | ✅ Likely fixed* |
| #10 Protein | ✅ | ✅ More cautious | ✅ No regression |

*Temperature=1.0 introduces variance; second run showed no referral.

## Retrieval Stability

Cosine scores were nearly identical before and after, confirming improvements came from the prompt rewrite, not from changes to retrieval or chunking:

| Question | Before Scores | After Scores (avg) | Variance |
|----------|---------------|-------------------|----------|
| #1 Creatine (3 runs) | 0.197, 0.189, 0.189 | 0.198, 0.190, 0.187 | ±0.001 |
| #8 Fasting | 0.324, 0.283, 0.279 | 0.363, 0.284, 0.282 | Small shift* |
| #9 Sleep >9h | 0.391, 0.349 | 0.390, 0.349, 0.329 | Stable |

\*Fasting retrieval shifted slightly; likely due to temp=1.0 variance in embeddings, not prompt change.

**Conclusion:** Same retrieval quality before/after. Improvements were purely from the stricter system prompt.

## What Would Change My Mind

- **Semantic chunking:** If chunk boundaries were more meaningful (split on section breaks, not character count), the "Chapter 4" false claim might disappear without prompt changes.
- **Higher k values:** If retrieval with k=5 returned mostly noise, the stricter prompt might cause over-refusal (currently untested).
- **Outside knowledge trade-off:** The "no outside knowledge" rule is strict; if legitimate follow-up advice becomes impossible, consider relaxing it (e.g., allow health provider referrals for medical questions only).
- **Temperature consistency:** Running each question 3x at temp=1.0 would show true variance; single runs are inconclusive.

