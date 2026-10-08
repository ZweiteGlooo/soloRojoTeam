# Stage 2B — Candidate profile classification with weighted skill matching

Module: `resumelens/profiles.py` · Tests: `tests/test_profiles.py`

---

## Professional profiles

---

## Full Stack Developer

**Requirements:**
- 1× programming language
- 1× frontend framework
- 1× backend framework
- 1× database

**Category Weights:**
| Category | Weight |
|----------|--------|
| Programming Language | 0.20 |
| Frontend Framework | 0.25 |
| Backend Framework | 0.25 |
| Database | 0.20 |
| Tool/Technology | 0.10 |

**Top Skills:**

| Skill | Weight | Category |
|-------|--------|----------|
| JAVASCRIPT | 1.0 | Programming Language |
| REACT | 1.0 | Frontend Framework |
| NODE_JS | 1.0 | Backend Framework |
| POSTGRESQL | 1.0 | Database |
| EXPRESS | 0.95 | Backend Framework |
| TYPESCRIPT | 0.9 | Programming Language |
| ANGULAR | 0.9 | Frontend Framework |
| DJANGO | 0.9 | Backend Framework |
| MONGODB | 0.9 | Database |
| GIT | 0.9 | Tool/Technology |

**Example Skillset:**
`[JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT, DOCKER, REST]`

---

## Machine Learning Engineer

**Requirements:**
- 1× programming language
- 2× ML framework
- 2× data science library
- 1× database

**Category Weights:**
| Category | Weight |
|----------|--------|
| Programming Language | 0.15 |
| ML Framework | 0.35 |
| Data Science Library | 0.35 |
| Database | 0.10 |
| Tool/Technology | 0.05 |

**Top Skills:**

| Skill | Weight | Category |
|-------|--------|----------|
| PYTHON | 1.0 | Programming Language |
| TENSORFLOW | 1.0 | ML Framework |
| PYTORCH | 1.0 | ML Framework |
| SCIKIT_LEARN | 0.95 | Data Science Library |
| PANDAS | 0.95 | Data Science Library |
| NUMPY | 0.95 | Data Science Library |
| KERAS | 0.95 | ML Framework |
| JUPYTER | 0.8 | Tool/Technology |
| R | 0.8 | Programming Language |
| SCIPY | 0.9 | Data Science Library |

**Example Skillset:**
`[PYTHON, TENSORFLOW, PYTORCH, PANDAS, NUMPY, SCIKIT_LEARN, JUPYTER]`

---

## Software profile

**Requirements:**
- 1× programming language
- 1× backend framework
- 1× database
- 1× tool/technology

**Category Weights:**
| Category | Weight |
|----------|--------|
| Programming Language | 0.25 |
| Backend Framework | 0.35 |
| Database | 0.25 |
| Tool/Technology | 0.15 |

**Top Skills:**

| Skill | Weight | Category |
|-------|--------|----------|
| PYTHON | 1.0 | Programming Language |
| JAVA | 1.0 | Programming Language |
| DJANGO | 1.0 | Backend Framework |
| POSTGRESQL | 1.0 | Database |
| FASTAPI | 0.95 | Backend Framework |
| SPRING | 0.95 | Backend Framework |
| DOCKER | 0.95 | Tool/Technology |
| KUBERNETES | 0.9 | Tool/Technology |
| MONGODB | 0.9 | Database |
| REDIS | 0.9 | Database |

**Example Skillset:**
`[PYTHON, DJANGO, POSTGRESQL, DOCKER, GIT, KUBERNETES, REST]`

---

## AI/Data profile

**Requirements:**
- 1× programming language
- 2× database
- 1× ML framework
- 1× tool/technology

**Category Weights:**
| Category | Weight |
|----------|--------|
| Programming Language | 0.15 |
| Database | 0.35 |
| ML Framework | 0.35 |
| Tool/Technology | 0.15 |

**Top Skills:**

| Skill | Weight | Category |
|-------|--------|----------|
| PYTHON | 1.0 | Programming Language |
| SPARK | 1.0 | Big Data Tool |
| SQL | 1.0 | Programming Language |
| TENSORFLOW | 0.95 | ML Framework |
| PYTORCH | 0.95 | ML Framework |
| POSTGRESQL | 0.9 | Database |
| CASSANDRA | 0.95 | Database |
| KAFKA | 0.95 | Big Data Tool |
| AIRFLOW | 0.9 | Big Data Tool |
| MACHINE_LEARNING | 1.0 | Competency |

**Example Skillset:**
`[PYTHON, SPARK, KAFKA, POSTGRESQL, MONGODB, TENSORFLOW, AIRFLOW, ETL]`

---

## Scope

**Input:** Normalized skills list from Stage 2A (`["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]`)

**Output:** Best matching profile with score, matched skills, and recommendations for Stage 3 (Recognition)

**API:**

| Function | Signature | Returns |
|----------|-----------|---------|
| `classify_candidate()` | `classify_candidate(normalized_skills: List[str])` | `(best_profile: Profile, all_profiles: List[Profile])` |
| `ProfileClassifier()` | Constructor for FST recognizer | Instance of classifier |
| `classify()` | `classifier.classify(skills)` | Same as above |

---

## Notation

**Finite Automaton for Profile Recognition:**

| Component | Symbol | Definition |
|-----------|--------|-----------|
| **States** | Q | {Full Stack Developer, Machine Learning Engineer, Software profile, AI/Data profile, initial} |
| **Input Alphabet** | Σ | Normalized skills {JAVASCRIPT, PYTHON, REACT, TENSORFLOW, ...} |
| **Transition Function** | δ | `if skill_count[category] >= requirement then → profile_state` |
| **Initial State** | q0 | No profile matched yet |
| **Accepting States** | F | Any of {Full Stack Developer, Machine Learning Engineer, Software profile, AI/Data profile} |

---

## Skill Categorization

Skills are mapped to categories for requirement matching:

| Category | Skills | Examples |
|----------|--------|----------|
| `programming_language` | Core languages | PYTHON, JAVASCRIPT, JAVA, GO, RUST, R, SCALA, C, C++, C# |
| `frontend_framework` | Frontend libraries | REACT, ANGULAR, VUE, SVELTE, NEXTJS, NUXT |
| `backend_framework` | Server frameworks | NODE_JS, DJANGO, FASTAPI, SPRING, FLASK, EXPRESS, RAILS |
| `database` | Data storage | POSTGRESQL, MONGODB, MYSQL, REDIS, CASSANDRA, ELASTICSEARCH |
| `ml_framework` | Machine learning | TENSORFLOW, PYTORCH, KERAS, JAX, MXNET |
| `data_science_library` | Data processing | PANDAS, NUMPY, SCIKIT_LEARN, SCIPY, MATPLOTLIB, PLOTLY |
| `big_data_tool` | Large-scale data | SPARK, HADOOP, KAFKA, AIRFLOW, HIVE |
| `tool_technology` | Infrastructure & tools | GIT, DOCKER, KUBERNETES, AWS, REST, JUPYTER, DEVOPS, ETL |

---

## Scoring Algorithm

### Overall Score Calculation

```
Score = (0.7 × category_coverage_score) + (0.3 × skill_specificity_score)
```

**Range:** 0.0 (no match) to 1.0 (perfect match)

### Category Coverage Score

For each required category:
```
category_coverage = min(actual_count / required_count, 1.0)
category_score += coverage × category_weight
```

### Skill Specificity Score

```
matched_weight = sum(weight of each skill candidate has)
max_possible_weight = sum(weight of all skills in profile)

skill_score = min(matched_weight / max_possible_weight, 1.0)
```

---

## Public API

### `classify_candidate(normalized_skills: List[str]) → (Profile, List[Profile])`

**Purpose:** Main entry point for candidate classification

**Parameters:**
- `normalized_skills`: List of skill strings in canonical form

**Returns:**
- `best_profile`: Profile object with highest score
- `all_profiles`: List of all 4 profiles ranked by score

**Example:**
```python
from resumelens.profiles import classify_candidate

skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT", "DOCKER"]
best_profile, all_profiles = classify_candidate(skills)

print(f"Best Match: {best_profile.name}")
print(f"Score: {best_profile.score}")
```

**Output:**
```
Best Match: Full Stack Developer
Score: 0.89
```

### `class Profile`

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | str | Profile name |
| `score` | float | Matching score (0.0 to 1.0) |
| `matched_skills` | List[str] | Skills candidate has |
| `missing_skills` | List[str] | Skills not in candidate's list |
| `category_scores` | Dict[str, int] | Count of skills per category |

---

## Design Decisions

1. **Weighted skill matching:** Different skills have different importance per profile
2. **Category-based requirements:** Flexibility in which specific skills matter
3. **Dual scoring (70/30 split):** Balance between breadth and depth
4. **Capped coverage:** Multiple skills in one category don't compound
5. **Default fallback:** Unknown skills default to "tool_technology"
6. **All profiles ranked:** Even weak matches are scored and ranked

---

## Limitations

1. **No skill combination patterns:** Skills counted independently
2. **No experience level detection:** Cannot distinguish beginner vs expert
3. **No temporal recency:** All skills treated equally regardless of age
4. **Fixed profile definitions:** Cannot modify without code changes
5. **No soft skill recognition:** Only technical skills detected
6. **No industry/domain context:** Same weights for all contexts

---

## Relationship to Other Stages

```
[STAGE 2A] NORMALIZATION
    Output: normalized_skills = ["JAVASCRIPT", "REACT", ...]
    ↓
[STAGE 2B] CLASSIFICATION (this stage)
    classify_candidate(normalized_skills)
    ↓
    Output: best_profile = Profile(name="Full Stack", score=0.89, ...)
    ↓
[STAGE 3] RECOGNITION
    Input: best_profile + all_profiles
    Output: ACCEPTED | REJECTED | TIER_1 | TIER_2 | TIER_3
```

---

## Example: Full Pipeline (Stage 1 → Stage 2B)

**Resume Text (Input to Stage 1):**
```
Valentina Rodríguez
Email: vale@gmail.com
Skills: JavaScript, React.js, Node.js, PostgreSQL, Git, Docker, AWS

Experience: 3 years as Full Stack Developer at TechCo
```

**Stage 1 Output (Extraction):**
```python
{
    "name": "Valentina Rodríguez",
    "email": "vale@gmail.com",
    "raw_skills": ["JavaScript", "React.js", "Node.js", "PostgreSQL", "Git", "Docker", "AWS"]
}
```

**Stage 2A Output (Normalization):**
```python
{
    "normalized_skills": ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT", "DOCKER", "AWS"]
}
```

**Stage 2B Output (Classification):**
```python
best_profile = Profile(
    name="Full Stack Developer",
    score=0.89,
    matched_skills=["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT", "DOCKER"],
    missing_skills=["ANGULAR", "EXPRESS", "MYSQL", ...],
    category_scores={
        "programming_language": 1,
        "frontend_framework": 1,
        "backend_framework": 1,
        "database": 1
    }
)
```

**All Profiles (Ranked):**
```python
1. Full Stack Developer: 0.89
2. Software profile: 0.71
3. AI/Data profile: 0.52
4. Machine Learning Engineer: 0.33
```

