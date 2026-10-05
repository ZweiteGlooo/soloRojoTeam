# ResumeLens — Formal Language-Based Resume Screening

Integrative Task 1 — Computación y Estructuras Discretas III (2026-2)

## Team
| Name | Student ID | GitHub user |
|------|-----------|-------------|
|      |           |             |

## Pipeline
1. **Extraction** — regular expressions (`re`) → `resumelens/extraction.py`
2. **Normalization** — finite-state transducers (`pyformlang`) → `resumelens/normalization.py`, `resumelens/sorting.py`
3. **Recognition** — finite automata (`pyformlang`) → `resumelens/recognition.py`
4. **Candidate profile DSL** — context-free grammar (`textX`) → `resumelens/dsl/`, `resumelens/render.py`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
python main.py data/resumes/<file>.txt
```

## Tests
```bash
pytest
```

## Environment
- Python version:
- IDE:

## Documentation
See [`docs/`](docs/).
