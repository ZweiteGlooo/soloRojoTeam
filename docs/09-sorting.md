# Stage 2C — Candidate ranking and tiering

Module: `resumelens/sorting.py` · Tests: `tests/test_sorting.py`

---

## Scope

**Input:** List of candidates with `best_profile` from Stage 2B

**Output:** Ranked list with tiers assigned for Stage 3 (Recognition)

**API:**

| Function | Signature | Returns |
|----------|-----------|---------|
| `rank_candidates()` | `rank_candidates(candidates, min_threshold=0.55)` | `List[Candidate]` (ranked, tiers assigned) |
| `get_tier_summary()` | `get_tier_summary(candidates)` | `Dict[str, int]` (count per tier) |
| `CandidateRanker()` | Constructor for ranker | Instance of ranker |

---

## Tiers

Candidates are classified into 4 tiers based on profile score:

| Tier | Score Range | Decision | Recommendation |
|------|-------------|----------|-----------------|
| **TIER_1_STRONG_CANDIDATE** | >= 0.85 | ACCEPT | Fast-track for interview |
| **TIER_2_MODERATE_CANDIDATE** | 0.70 - 0.84 | CONSIDER | Standard interview process |
| **TIER_3_WEAK_CANDIDATE** | 0.55 - 0.69 | REVIEW | Additional assessment needed |
| **REJECTED** | < 0.55 | REJECT | Does not meet minimum requirements |

---

## Tier Thresholds

### Why These Numbers?

**TIER_1 (>= 0.85):**
- Has all required categories + many high-weight skills
- Example: Full Stack with [JS, React, Node, Express, PostgreSQL, MongoDB, Docker, Git]
- Confidence: Very high — candidate is strong match

**TIER_2 (>= 0.70):**
- Has all required categories + some high-weight skills
- Example: Full Stack with [JS, React, Node, PostgreSQL]
- Confidence: Good — candidate is decent match

**TIER_3 (>= 0.55):**
- Has most required categories + basic skills
- Example: Full Stack with [JS, React, PostgreSQL] (missing backend framework)
- Confidence: Marginal — candidate needs evaluation

**REJECTED (< 0.55):**
- Missing critical requirements or weak match
- Example: Full Stack with only [Python, GIT]
- Confidence: Low — candidate unlikely to perform

---

## Notation

**Formal Definition:**