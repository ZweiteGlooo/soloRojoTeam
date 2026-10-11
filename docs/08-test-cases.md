# Test cases and scenarios

Run everything with `pytest` from the repository root (250 tests). The tables
list the representative cases, and the last column names the test that
implements each one.

| File | Stage | Test functions |
|---|---|---|
| `tests/test_extraction.py` | 1: regular expressions | 15 |
| `tests/test_normalization.py` | 2: transducers | 45 |
| `tests/test_ordering.py` | 2: patterns and canonical order | 16 (some parametrized) |
| `tests/test_profiles.py`, `tests/test_sorting.py` | 2B/2C: scoring and ranking | 38 + 29 |
| `tests/test_recognition.py` | 3: finite automata | 30 (some parametrized) |
| `tests/test_dsl.py` | 4: grammar, generator, render | 35 (some parametrized) |
| `tests/test_pipeline.py` | 1 → 4 integration and CLI | 11 (some parametrized) |

## Scenarios

| ID | Scenario | Description |
|---|---|---|
| S1 | Ideal Full Stack résumé | Statement example (Wednesday Addams): every stage gives the expected output and only Full Stack is accepted |
| S2 | Ideal ML résumé | Statement example (Mary Jane Watson): only ML Engineer is accepted |
| S3 | Candidate that fits two profiles | Peter Parker: Full Stack and Backend Developer |
| S4 | Candidate that fits none | résumé with no technical skills |
| S5 | Variant spellings | `JS`, `Javascript`, `NodeJS`, `Node.js`, `Py Torch`, `Tensor Flow`, `RESTful APIs` reach the same canonical names |
| S6 | Order independence | the same skills written in a different order give the same words and results |
| S7 | Incomplete profile | one required block missing → REJECTED, and the block is reported |
| S8 | Malformed candidate profile | lexical, syntax and semantic errors in `.rlp` files are rejected with line and column |

## Stage 1: Extraction

| ID | Input | Expected output | Test |
|---|---|---|---|
| E1 | `Wednesday Addams` résumé | name, `raw_skills = [JS, React.js, NodeJS, Postgres, Git]` | `test_extraction.py` |
| E2 | `peter.parker@dailybugle.com \| +57 300 123 4567` | email and phone found | `test_extraction.py` |
| E3 | `B.Sc. in Software Engineering` | `{degree: B.Sc., field: Software Engineering}` | `test_extraction.py` |
| E4 | email/URL containing skill names | not reported as skills | `test_extraction.py` |

## Stage 2: Normalization and canonical order

| ID | Input | Expected output | Test |
|---|---|---|---|
| N1 | `["JS", "React.js", "NodeJS", "Postgres", "Git"]` | `[JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]` | `test_normalization.py::test_wednesday_addams_skills` |
| N2 | `["js", "BadTech", "react"]` | normalized `[JAVASCRIPT, REACT]`, unknown `[BadTech]` | `test_normalization.py::test_mixed_known_and_unknown` |
| N3 | `RESTful APIs`, `No SQL` | `REST`, `NOSQL` | `test_ordering.py::test_peter_parker_rest_and_nosql_now_normalized` |
| O1 | `[GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT]`, Full Stack | `[JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT]` | `test_ordering.py::test_example_from_statement` |
| O2 | `[PYTHON, REACT, GIT]`, Full Stack | `[REACT, GIT]` (PYTHON ∉ Σ) | `test_drops_skills_outside_profile` |
| O3 | `[GIT, GIT, JAVASCRIPT]` | `[JAVASCRIPT, GIT]` | `test_removes_duplicates` |
| O4 | any profile | blocks are disjoint (needed for determinism) | `test_blocks_are_disjoint` |

## Stage 3: Recognition

| ID | Profile | Word | Expected | Test |
|---|---|---|---|---|
| R1 | Full Stack | `JAVASCRIPT REACT NODE_JS POSTGRESQL GIT` | ACCEPTED | `test_minimal_word` |
| R2 | Full Stack | `… MYSQL MONGODB REST GIT GITHUB` (repeated blocks + optional API) | ACCEPTED | `test_with_optional_api_and_repeated_blocks` |
| R3 | Full Stack | `JAVASCRIPT NODE_JS POSTGRESQL GIT` | REJECTED, missing FRONTEND | `test_missing_frontend` |
| R4 | Full Stack | `REACT JAVASCRIPT …` (unsorted) | REJECTED | `test_wrong_order` |
| R5 | Full Stack | ε (empty word) | REJECTED | `test_empty_word` |
| R6 | ML Engineer | `PYTHON PANDAS TENSORFLOW POSTGRESQL GIT` | ACCEPTED, trace q0→LANGUAGE→DATA_LIBRARY→ML_LIBRARY→DATABASE→VCS | `test_statement_example_ml` |
| R7 | ML Engineer | `PANDAS TENSORFLOW SQL GIT` | REJECTED, missing LANGUAGE | `test_ml_needs_python` |
| R8 | Backend | `JAVA SPRING_BOOT REST POSTGRESQL DOCKER GIT` | ACCEPTED | `test_backend` |
| R9 | Backend | without REST | REJECTED | `test_backend_requires_api` |
| R10 | Data Engineer | `PYTHON SPARK AIRFLOW ETL POSTGRESQL AWS GIT` | ACCEPTED | `test_data_engineer` |
| R11 | Data Engineer | without Spark/Kafka/Airflow | REJECTED | `test_data_engineer_requires_processing_tool` |
| R12 | all | DFA deterministic, ε-NFA not, DFA ≡ ε-NFA | true | `TestConstruction` |
| R13 | all | `formal_definition` is a valid 5-tuple | true | `test_formal_definition_is_a_5_tuple` |

## Stage 4: Candidate profile language

| ID | Input | Expected | Test |
|---|---|---|---|
| D1 | minimal profile (skills + profiles) | valid, optional sections are `None` | `test_minimal` |
| D2 | profile with all sections and repeated entries | valid, model has every value | `test_full_profile_structure` |
| D3 | `skills { }` | valid | `test_empty_skills_section_is_allowed` |
| D4 | `email wednesday@` | lexical error | `test_bad_email` |
| D5 | `react` in skills | lexical error | `test_lowercase_skill` |
| D6 | no `skills` section | syntax error | `test_missing_skills` |
| D7 | `WEB_DESIGNER:` | syntax error | `test_unknown_profile` |
| D8 | `ACCEPTED` without word | syntax error | `test_accepted_without_word` |
| D9 | `profiles` before `skills` | syntax error | `test_profiles_before_skills` |
| D10 | profile reported twice | semantic error | `test_duplicate_profile` |
| D11 | accepted word with a skill not listed | semantic error | `test_word_not_in_skills` |
| D12 | `0 years` | semantic error | `test_zero_years` |
| D13 | every file in `examples/invalid/` | error of the kind in its file name | `test_invalid_examples_fail_with_the_kind_in_their_name` |
| D14 | generated profile for each sample résumé | valid | `test_generated_profiles_are_valid` |
| V1 | valid profile → HTML | document with name, links, badges; text escaped | `test_html_document`, `test_html_escapes_text` |
| V2 | valid profile → Markdown | sections and results table | `test_markdown` |
| V3 | invalid profile → render | `ProfileError`, nothing generated | `test_invalid_profile_is_not_rendered` |

## Integration (Stage 1 → 4)

| ID | Input | Expected | Test |
|---|---|---|---|
| I1 | the three sample résumés | valid profiles, accepted profiles as in S1–S3 | `test_sample_resumes` |
| I2 | ML résumé written in another order | statement word `PYTHON PANDAS TENSORFLOW POSTGRESQL GIT`, ML accepted | `test_statement_ml_example` |
| I3 | same skills, two orders | same result | `test_order_in_resume_does_not_change_the_result` |
| I4 | Data Engineer résumé | only Data Engineer accepted, 5 years parsed | `test_data_engineer_resume` |
| I5 | résumé without skills | valid profile, no profile accepted | `test_resume_without_skills_is_still_a_valid_profile` |
| I6 | `main.py --validate` valid + invalid | report per file, exit code 1 | `test_validate_mode` |
