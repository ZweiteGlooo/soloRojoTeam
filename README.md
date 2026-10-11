# ResumeLens — Formal Language-Based Resume Screening

**Integrative Task 1** — Computación y Estructuras Discretas III (2026-2)

---

## Team

| Name | Student ID | GitHub user |
|------|-----------|-------------|
| Gloribeth Renteria | A00 | ZweiteGlooo |
| Valentina Tangarife | A00411935 | valentangarife |
| Dayanna Fernández Núñez | A00403756| Dayanna-Fernandez |

---

## Project Overview

ResumeLens is a formal language-based system for automated resume screening and candidate ranking. It implements four computational stages using techniques from formal language theory:

1. **Extraction** — Parse resume text using regular expressions
2. **Normalization** — Canonicalize skills using finite-state transducers (FSTs)
3. **Classification** — Match normalized skills to 4 candidate profiles using weighted scoring
4. **Ranking** — Tier candidates based on classification scores
5. **Recognition** — Validate profiles using finite automata
6. **DSL & Rendering** — Generate structured output using context-free grammar

---

## Pipeline

```
Resume Text (.txt)
        ↓
[Stage 1] Extraction (Regex)
        ↓ extraction.py
Raw Skills, Contact, Experience
        ↓
[Stage 2A] Normalization (FST Transducer)
        ↓ normalization.py
Canonical Skills (e.g., "js" → "JAVASCRIPT")
        ↓
[Stage 2B] Classification (Profile Matching)
        ↓ profiles.py
Candidate Score (0.0 - 1.0) per Profile
        ↓
[Stage 2C] Ranking (Tiering System)
        ↓ sorting.py
Tier Assignment (TIER_1, TIER_2, TIER_3, REJECTED)
        ↓
[Stage 3] Recognition (Finite Automata)
        ↓ recognition.py
Profile Validation (ACCEPTED / REJECTED)
        ↓
[Stage 4] DSL & Rendering (Context-Free Grammar)
        ↓ dsl/parser.py, render.py, pipeline.py
Output: HTML, Markdown, JSON, .rlp (DSL)
```

### Profiles Supported

- **Full Stack Developer** — LANGUAGE + FRONTEND + BACKEND + DATABASE + DEVOPS
- **Machine Learning Engineer** — LANGUAGE + ML_FRAMEWORK + DATA_LIBRARY + PROCESSING
- **Backend Developer** — LANGUAGE + API + DATABASE + BACKEND_FRAMEWORK
- **Data Engineer** — LANGUAGE + PROCESSING + DATABASE + PIPELINE_TOOL

---

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/soloRojoTeam/resumelens.git
cd soloRojoTeam
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Run

### Process Single Resume
```bash
python main.py data/resumes/wednesday_addams.txt
```

### Process All Resumes
```bash
python main.py data/resumes/*.txt
```

### Specify Output Format
```bash
python main.py data/resumes/wednesday_addams.txt --format html
python main.py data/resumes/wednesday_addams.txt --format markdown
python main.py data/resumes/wednesday_addams.txt --format both
```

### Output Files
Generated in `data/output/`:
- `<name>.html` — Interactive HTML report
- `<name>.md` — Markdown report
- `<name>.json` — Structured JSON data
- `<name>.rlp` — DSL representation

---

## Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
# Stage 2A: Normalization
pytest tests/test_normalization.py -v

# Stage 2B: Classification
pytest tests/test_profiles.py -v

# Stage 2C: Ranking
pytest tests/test_sorting.py -v

# Stage 1: Extraction
pytest tests/test_extraction.py -v

# Stage 3: Recognition
pytest tests/test_recognition.py -v

# Stage 4: DSL & Rendering
pytest tests/test_dsl.py -v
pytest tests/test_pipeline.py -v
```

### Test Coverage
- **Total Tests:** 250+
- **Extraction:** 4 tests
- **Normalization:** 45 tests 
- **Classification:** 38 tests 
- **Ranking:** 29 tests
- **Recognition:** 30+ tests
- **DSL/Rendering:** 40+ tests
- **Pipeline Integration:** 20+ tests

---

## Project Structure

```
soloRojoTeam/
├── resumelens/
│   ├── __init__.py
│   ├── extraction.py           # Stage 1: Regex extraction
│   ├── normalization.py        # Stage 2A: FST normalization
│   ├── profiles.py             # Stage 2B: Profile classification
│   ├── sorting.py              # Stage 2C: Candidate ranking & tiering
│   ├── recognition.py          # Stage 3: Finite automata validation
│   ├── patterns.py             # Profile patterns for automata
│   ├── render.py               # Stage 4: Output rendering
│   ├── pipeline.py             # Full pipeline orchestration
│   └── dsl/
│       ├── parser.py           # textX DSL parser
│       ├── generator.py        # DSL output generator
│       ├── candidate.tx        # EBNF grammar definition
│       └── examples/
│           ├── valid/          # Valid .rlp examples
│           └── invalid/        # Invalid .rlp examples
├── tests/
│   ├── test_extraction.py
│   ├── test_normalization.py
│   ├── test_profiles.py
│   ├── test_sorting.py
│   ├── test_recognition.py
│   ├── test_dsl.py
│   ├── test_ordering.py
│   ├── test_pipeline.py
│   └── __init__.py
├── data/
│   ├── resumes/                # Input resume files (.txt)
│   │   ├── wednesday_addams.txt
│   │   ├── peter_parker.txt
│   │   └── mary_jane_watson.txt
│   └── output/                 # Generated reports (.html, .md, .json, .rlp)
├── docs/
│   ├── 01-literature-review.md
│   ├── 02-module-design.md
│   ├── 03-regex.md
│   ├── 04-transducers.md       # Stage 2A documentation
│   ├── 05-automata.md
│   ├── 06-grammar.md
│   ├── 07-profiles.md          # Stage 2B documentation
│   ├── 08-test-cases.md
│   ├── 09-sorting.md           # Stage 2C documentation
│   ├── diagrams/               # Automata visualizations (.dot)
│   └── samples/                # Example outputs
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore
```

---

## Environment

- **Python version:** 3.14.2
- **IDE:** [Visual Studio Code / IntelliJ IDEA]
- **OS:** [macOS / Windows]

### Dependencies
- `pyformlang` — Finite automata, FSTs, CFGs
- `textX` — DSL parsing and generation
- `pytest` — Testing framework
- `Jinja2` — HTML template rendering

See `requirements.txt` for complete dependency list.

---
## Example Run

```bash
$ python main.py data/resumes/wednesday_addams.txt

=== wednesday_addams.txt ===
Candidate: Wednesday Addams

[1] extracted  : JS, React.js, NodeJS, Postgres, Git
[2] normalized : JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
[3] recognition:
    Full Stack Developer      ACCEPTED  JAVASCRIPT REACT NODE_JS POSTGRESQL GIT
    Machine Learning Engineer REJECTED  missing LANGUAGE, DATA_LIBRARY, ML_LIBRARY
    Backend Developer         REJECTED  missing API
    Data Engineer             REJECTED  missing LANGUAGE, PROCESSING
[4] profile    : valid
    written    : data/output/wednesday_addams.html
                data/output/wednesday_addams.md
                data/output/wednesday_addams.json
                data/output/wednesday_addams.rlp
```

---

## Documentation

Comprehensive documentation available in [`docs/`](docs/):

- **01-literature-review.md** — Formal language theory background
- **02-module-design.md** — System architecture and design decisions
- **03-regex.md** — Regular expressions (Stage 1)
- **04-transducers.md** — Finite-state transducers (Stage 2A)
- **05-automata.md** — Finite automata (Stage 3)
- **06-grammar.md** — Context-free grammars (Stage 4)
- **07-profiles.md** — Profile classification algorithm (Stage 2B)
- **08-test-cases.md** — Test design and strategy
- **09-sorting.md** — Ranking and tiering system (Stage 2C)

---

## References

- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation*.
- Sipser, M. (2012). *Introduction to the Theory of Computation*.
- pyformlang documentation: https://github.com/eurecom-s3/pyformlang
- textX documentation: http://textx.github.io/textX/

---

## License

This project is part of the Computación y Estructuras Discretas III course at Icesi University, semester 2026-2.
