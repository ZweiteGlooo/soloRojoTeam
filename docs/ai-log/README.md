# AI usage log (IAG level 3 — Collaboration with AI)

The assignment allows using generative AI to complete tasks and asks us to keep a record of
(a) the content of our own authorship that we gave the AI and (b) the prompts we used, and to be able to modify and explain what the AI produced. This file is that record.

---

## Tool: Claude (Anthropic)

## Phase 0 — Understand the problem and plan

1. **Brief.** "I'm building ResumeLens, a résumé-screening pipeline for a Formal Languages course. Stages: (1) regex extraction with Python `re`, (2) normalization with finite-state transducers in pyformlang, (3) profile recognition with DFA/NFA/ε-NFA in pyformlang, (4) a candidate-profile DSL defined as a CFG with textX that outputs HTML/Markdown. Here is the full assignment: [*Assignment*]. Summarize the requirements per stage as a checklist, and list the ambiguities I should ask the professor about."

2. **Mapping.** "For each stage, tell me which learning outcome (RAA1, RAA2, RAA3, RAA6) it covers and what evidence a grader would look for: formal definition, diagram, implementation, tests."

3. **Architecture.** "Propose a module structure for a Python project with these modules: `extraction`, `normalization`, `recognition`, `dsl`, `visualization`, `ui`, `tests`. For each module, give the main functions with their inputs and outputs (types), and the data structure passed between stages. Keep one shared pipeline for all four profiles, not four separate implementations. Here is my first idea: [your sketch]."

---

## Phase 1 — Regular expressions (extraction)

4. **Categories.** "From the four profiles I chose, [list them], define the information categories to extract: contact (email, phone, LinkedIn/GitHub URL), name, years of experience, education/degree, programming languages, frameworks/libraries, databases, tools, others. For each one, tell me whether a regex is enough or whether I need a dictionary-backed regex (alternation of known terms)."

5. **Skill vocabulary regex.** "Design a regex that captures technology mentions including variants like `Javascript`, `React.js`, `C++`, `Node.js`, etc. Handle word boundaries correctly for symbols. Make it case-insensitive, and say how to avoid false positives such as 'Go' in 'go to' or 'R' as a single letter."

6. ⚔️ "Here are my regexes: [paste]. Find inputs that break them: false positives, false negatives, catastrophic backtracking. Propose fixes."

7. **Docs.** "Help me write the `docs/stage1_regex.md` section: for each regex, the pattern, the language it describes in plain words, examples, and known limitations. Here is a draft: [paste]."

---

## Phase 3 — Finite-state transducers (normalization)

8. **Modeling decision.** "For normalizing skill variants to canonical tokens (e.g. `React.js → REACT`), compare two FST designs: (a) character-level, where Σ = characters and Γ = output characters, building a trie-like transducer; (b) token-level, where each input symbol is a whole extracted string. Which one demonstrates FST theory better? Which is more practical in pyformlang? Recommend one and justify it."


9. **Formal 7-tuple.** "For this transducer write the complete formal definition M = (Q, Σ, Γ, δ, ω, q0, F): list Q, Σ, Γ, the transition relation δ, the output relation ω, q0 and F explicitly. Use a notation consistent with Mealy-style output on transitions."

10. **pyformlang implementation.** "Implement that transducer with `pyformlang.fst.FST` (`add_transition`, `add_start_state`, `add_final_state`, `translate`). Show how to normalize one string and a list of strings, and what happens with an input not covered (no translation → keep as `UNKNOWN` or discard?)."

11. "Review my FST definition and code.

---

## Phase 4 — Finite automata (profile recognition)

12. **Alphabet / abstraction level.** "For the automata, should Σ be the canonical tokens themselves (`JAVASCRIPT`, `REACT`, …) or abstract categories (`FE_LANG`, `FE_FRAMEWORK`, `BACKEND`, `DB`, `VCS`)? Explain how each choice affects the size of Q, the readability of the diagram, and the 'design decisions' I must defend in the presentation."

13. **Choosing the automaton type.** "For each profile, propose which type to use (DFA, NFA, ε-NFA) so that across the project I show at least two types. Justify each by its definition: is δ a function Q×Σ→Q, a relation into P(Q), or does it include ε?"

14. **pyformlang implementation.** "Implement the four automata with `pyformlang.finite_automaton` (`DeterministicFiniteAutomaton`, `NondeterministicFiniteAutomaton`, `EpsilonNFA`, `State`, `Symbol`). Write `classify(sorted_tokens) -> dict[profile, ACCEPTED|REJECTED]`, since one résumé can match more than one profile."

---

## Phase 5 — Context-free grammar + textX DSL

15. **Language design.** "Design a DSL to represent a candidate profile with: personal info, contact (email, phone, links), multiple experiences (role, company, years), multiple education records, skills (canonical tokens only), and the classification result per profile. Show me 2–3 alternative syntaxes (block-based, key-value, YAML-like) and recommend one with justification."

16. **Validation.** "Add semantic validation with textX object processors: email format, years ≥ 0, skills must belong to my canonical vocabulary, classification values only ACCEPTED/REJECTED. Show how lexical and syntactic errors are reported (`TextXSyntaxError`) versus semantic errors (`TextXSemanticError`)."

16. **Generator.** "Write the function that takes the output of stages 1–3 and generates a `.rlens` (or my extension: [ext]) file conforming to the grammar, so the DSL is produced by the pipeline and not written by hand."

17. "Check my repo for any missing deliverables or requierements to be completed"

---