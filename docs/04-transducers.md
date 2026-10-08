# Stage 2 — Qualification normalization with finite-state transducers

Module: `resumelens/normalization.py` · Tests: `tests/test_normalization.py`

## Scope

Stage 2 **transforms** raw skill strings (received from Stage 1, kept exactly as written) into
canonical form (uppercase, standardized). It does not decide whether a profile is satisfied (Stage 3).

**Input:** `raw_skills` list from Stage 1  
Example: `["JS", "React.js", "node.js", "Postgres", "py torch"]`

**Output** (`normalize_skills(raw_skills)` → `list[str]`):

| Key | Content |
|---|---|
| normalized skills | Canonical uppercase forms → **input to Stage 3** |

**API:**

| Function | Signature | Returns | Example |
|---|---|---|---|
| `normalize_skill(skill)` | `str → str` | Canonical form or raises `ValueError` | `"React.js"` → `"REACT"` |
| `normalize_skills(raw_skills)` | `list[str] → list[str]` | Normalized list or raises on first unknown | `["JS", "React.js"]` → `["JAVASCRIPT", "REACT"]` |
| `normalize_skills_safe(raw_skills)` | `list[str] → (list[str], list[str])` | `(normalized, unknown)`, no errors | `["JS", "BadTech"]` → `(["JAVASCRIPT"], ["BadTech"])` |

## Notation

A **finite-state transducer** (FST) is a 7-tuple `M = (Q, Σ, Γ, δ, ω, q0, F)`:

| Component | Meaning | Example |
|---|---|---|
| `Q` | Set of states | `{q0, q1, q_accept}` |
| `Σ` | Input alphabet (characters read) | `{a, b, ..., z}` |
| `Γ` | Output alphabet (characters emitted) | `{A, B, ..., Z, _}` |
| `δ` | Transition: `(state, input_char) → next_state` | `δ(q0, 'j') = q1` |
| `ω` | Output: `(state, input_char) → output_string` | `ω(q1, 's') = "AVASCRIPT"` |
| `q0` | Initial state | `q0` |
| `F` | Accepting states | `{q_accept}` |

**Execution:** Reads input character by character left-to-right. At each state and character,
follows the transition, emits output. Accepts (returns `True`) only if input is fully consumed
and machine is in an accepting state.

## Formal model

### `QualificationTransducer` class

```python
class QualificationTransducer:
    def __init__(self, name: str, transitions: Dict[Tuple[str, str], Tuple[str, str]])
    def formal_definition(self) -> Dict
    def process(self, input_str: str) -> Tuple[bool, str]
```

| Method | Purpose | Returns |
|---|---|---|
| `__init__` | Initialize FST with name and transition table. Infers `Q`, `Σ`, `Γ` from transitions. | — |
| `formal_definition()` | Return the complete 7-tuple `(Q, Σ, Γ, δ, ω, q0, F)` | `dict` |
| `process(input)` | Read input through FST state-by-state. | `(accepted: bool, output: str)` |

**Example:** JavaScript transducer processing `"javascript"`:

```
Input:   j a v a s c r i p t
State:   q0→q1→q2→...→q_accept
Output:  J A V A S C R I P T
Result:  (True, "JAVASCRIPT")
```

**Design note:** The `QualificationTransducer` class is provided for formal documentation and
future visualization with `pyformlang.Automaton`. In production, the hash table `NORMALIZATION_MAP`
provides O(1) lookup and is preferred over character-by-character FST simulation.

## Normalization mapping

### `NORMALIZATION_MAP` — Pre-computed lookup table

A dictionary with ~120 entries, mapping raw skill variations to their canonical forms:

```python
NORMALIZATION_MAP: Dict[str, str] = {
    "js": "JAVASCRIPT",
    "javascript": "JAVASCRIPT",
    "react": "REACT",
    "react.js": "REACT",
    "postgres": "POSTGRESQL",
    ...
}
```

**Coverage** (~120 entries across categories):

| Category | Count | Examples (normalized form) |
|---|---|---|
| Programming languages | 8 | `JAVASCRIPT`, `PYTHON`, `JAVA`, `GOLANG`, `RUST`, `KOTLIN`, `SCALA`, `SQL` |
| Frontend frameworks | 7 | `REACT`, `ANGULAR`, `VUE`, `NEXT_JS`, `SVELTE`, `EMBER` |
| Backend frameworks | 6 | `NODE_JS`, `EXPRESS`, `DJANGO`, `FLASK`, `SPRING_BOOT`, `FAST_API` |
| Data science & ML | 11 | `PANDAS`, `NUMPY`, `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH`, `KERAS`, `MATPLOTLIB`, `PYSPARK`, `SPARK` |
| Databases | 9 | `POSTGRESQL`, `MYSQL`, `MONGODB`, `REDIS`, `SQLITE`, `SQL_SERVER`, `ORACLE`, `CASSANDRA`, `ELASTICSEARCH` |
| Tools & platforms | 8 | `GIT`, `GITHUB`, `GITLAB`, `DOCKER`, `KUBERNETES`, `AWS`, `AZURE`, `GCP`, `JENKINS`, `AIRFLOW`, `KAFKA` |
| API & protocols | 4 | `REST`, `GRAPHQL`, `GRPC`, `SOAP` |
| Competencies | 8 | `MACHINE_LEARNING`, `DEEP_LEARNING`, `PREDICTIVE_MODELS`, `DATA_PROCESSING`, `ETL`, `CI_CD`, `DEVOPS` |

**Example alternations:**

| Input variations | Normalized output |
|---|---|
| `js`, `javascript`, `JavaScript`, `JAVASCRIPT` | `JAVASCRIPT` |
| `react`, `react.js`, `reactjs`, `react js` | `REACT` |
| `python`, `py`, `python3`, `python 3` | `PYTHON` |
| `postgres`, `postgresql` | `POSTGRESQL` |
| `py torch`, `pytorch`, `py-torch` | `PYTORCH` |
| `machine learning`, `machine-learning`, `ml` | `MACHINE_LEARNING` |

**Matching rules:**

1. **Case-insensitive:** All input is lowercased before lookup. `"JavaScript"`, `"javascript"`, `"JAVASCRIPT"` all match the key `"javascript"` and return `"JAVASCRIPT"`.
2. **Exact key match:** The lookup is direct dictionary access (no regex, no partial matching). Unknown skills are rejected.
3. **Closed vocabulary:** Only skills in the table are recognized. Unknown technologies (e.g., `"ZephirLang"`) cause an error or are skipped depending on the API.

## Public API

### `normalize_skill(skill: str) → str`

Normalize a single raw skill to its canonical form.

```python
normalize_skill("React.js")        # → "REACT"
normalize_skill("tensorflow")      # → "TENSORFLOW"
normalize_skill("UnknownTech")     # → ValueError: Unknown skill: UnknownTech
```

**Behavior:** Case-insensitive lookup in `NORMALIZATION_MAP`. Raises `ValueError` if the skill is not found.

---

### `normalize_skills(raw_skills: List[str]) → List[str]`

Normalize a list of raw skills to canonical form, preserving order.

```python
normalize_skills(["JS", "React.js", "Postgres", "py torch"])
# → ["JAVASCRIPT", "REACT", "POSTGRESQL", "PYTORCH"]
```

**Behavior:** Applies `normalize_skill()` to each item in order. Raises `ValueError` on the first
unknown skill (all preceding skills are lost).

---

### `normalize_skills_safe(raw_skills: List[str]) → Tuple[List[str], List[str]]`

Normalize a list gracefully, collecting unknown skills separately instead of failing.

```python
norm, unknown = normalize_skills_safe(["JS", "BadTech", "Docker"])
# norm = ["JAVASCRIPT", "DOCKER"]
# unknown = ["BadTech"]
```

**Behavior:** Returns a tuple `(normalized, unknown)`. Unknown skills are skipped and reported,
not errors. All skills are attempted.

---

## Design decisions

1. **FST class for formality, hash table for efficiency.**  
   The `QualificationTransducer` class demonstrates theoretical knowledge (formal model) required
   by the course. The `NORMALIZATION_MAP` provides O(1) lookup in practice. Both coexist: theory
   is documented, performance is practical.

2. **Case-insensitive, exact-match lookup.**  
   All input is lowercased. Matching is direct dictionary access, not regex. This avoids the
   complexity of fuzzy matching or misspelling tolerance at this stage.

3. **Whitespace and punctuation are part of the key.**  
   Entries like `"react.js"`, `"react-js"`, and `"react js"` are separate keys in the table,
   all mapping to `"REACT"`. This is simpler than writing a regex for each technology.

4. **Closed vocabulary enforces consistency.**  
   Only ~120 pre-approved skills are recognized. Unknown technologies are rejected or collected.
   This prevents the pipeline from silently accepting misspellings or new technologies without
   updating the mapping.

5. **Order of appearance is preserved.**  
   `normalize_skills()` maintains the order of skills as they appear in `raw_skills`. Canonical
   ordering (by category or profile relevance) happens in later stages.

6. **Stage 1 → Stage 2 boundary is clean.**  
   Stage 1 keeps surface form; Stage 2 produces canonical form. Each stage has one responsibility.
   No normalization happens in Stage 1; no matching happens in Stage 2.

## Limitations

- **No contextual intelligence.** `"python"` always → `"PYTHON"`, even if the context suggests
  `"PYTHON_WEB"` vs. `"PYTHON_DATA"`. Disambiguation requires semantic analysis, not available here.

- **No fuzzy matching or spell-check.** `"pytohn"`, `"java scirpt"`, or `"nodee"` are rejected.
  Typo correction is not implemented.

- **Acronym ambiguity.** `"ML"` → `"MACHINE_LEARNING"` by default. If someone means `"Markup Language"`
  or `"Middle Layer"`, there is no way to tell.

- **No transducer visualization (yet).** The `formal_definition()` method returns the 7-tuple,
  but integration with `pyformlang.Automaton` for visual output is marked TODO.

- **Immutable and hardcoded mapping.** The table cannot grow or change at runtime. New technologies
  require code changes and redeployment.

- **No abbreviation expansion.** `"CICD"` and `"CI/CD"` are different keys; both must be listed
  if both spellings appear in résumés.

## Relationship to other stages

```
Stage 1: Extraction (Regex)
    Raw résumé text → ["JS", "React.js", "Postgres", ...]

Stage 2: Normalization (FST / Hash table)
    Raw skills → ["JAVASCRIPT", "REACT", "POSTGRESQL", ...]
    
Stage 3: Pattern Recognition (Finite automata)
    Normalized skills → Match against profiles
    → "Full Stack? Backend? ML Engineer?" → Accept/Reject

Stage 4: DSL Output (Context-free grammar)
    Accept/Reject → Validated candidate profile (textX)
```

**Input from Stage 1:** `raw_skills` (order preserved, surface form)  
**Output to Stage 3:** Normalized list (canonical form, order preserved)


