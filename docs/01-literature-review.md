# Literature review

## Sources

| # | Reference | Topic |
|---|---|---|
| [1] | J. E. Hopcroft, R. Motwani, J. D. Ullman. *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. Pearson, 2006. | regular expressions, DFA/NFA/ε-NFA, subset construction, CFGs, Chomsky normal form |
| [2] | M. Sipser. *Introduction to the Theory of Computation*, 3rd ed. Cengage, 2012. | equivalence of NFA and DFA, closure properties, CFG simplification |
| [3] | K. Thompson. "Regular expression search algorithm." *Communications of the ACM* 11(6), 419–422, 1968. | compiling regular expressions into ε-NFAs |
| [4] | J. E. F. Friedl. *Mastering Regular Expressions*, 3rd ed. O'Reilly, 2006. | practical regex engines, alternation order, lookarounds |
| [5] | M. Mohri. "Finite-state transducers in language and speech processing." *Computational Linguistics* 23(2), 269–311, 1997. | formal definition and use of FSTs for normalization |
| [6] | E. Roche, Y. Schabes (eds.). *Finite-State Language Processing*. MIT Press, 1997. | finite-state methods for text processing |
| [7] | K. R. Beesley, L. Karttunen. *Finite State Morphology*. CSLI Publications, 2003. | lexical transducers that map surface forms to canonical forms |
| [8] | K. Yu, G. Guan, M. Zhou. "Resume information extraction with cascaded hybrid model." *Proc. ACL*, 499–506, 2005. | résumé parsing as a staged (cascaded) pipeline |
| [9] | M. Raghavan, S. Barocas, J. Kleinberg, K. Levy. "Mitigating bias in algorithmic hiring: evaluating claims and practices." *Proc. FAT\* '20*, 469–481, 2020. | risks of automated candidate scoring and ranking |
| [10] | I. Dejanović, R. Vaderna, G. Milosavljević, Ž. Vuković. "TextX: A Python tool for Domain-Specific Languages implementation." *Knowledge-Based Systems* 115, 1–4, 2017. | textX grammar language and meta-models |
| [11] | B. Ford. "Parsing expression grammars: a recognition-based syntactic foundation." *Proc. POPL*, 111–122, 2004. | PEG, the parsing formalism used by textX/Arpeggio |
| [12] | M. Fowler. *Domain-Specific Languages*. Addison-Wesley, 2010. | design of external DSLs, semantic model, validation |
| [13] | J. Romero. "Pyformlang: An educational library for formal language manipulation." *Proc. SIGCSE '21*, 576–582, 2021. | the library used for automata and transducers |

## Key findings

**Résumé processing is a cascade.** Yu et al. [8] split résumé extraction into
stages: first segment the text into blocks, then extract detailed fields inside
each block. Each stage is simpler because the previous one has already reduced
the problem. Our four stages follow the same idea. Each stage has a narrow job
and a different formal model.

**Regular expressions are enough to locate the data.** Contact data, degrees
and technology names follow local, non-nested patterns, which is exactly what
regular languages describe [1], [2]. Thompson's construction [3] shows that
every regex is an ε-NFA, so Stage 1 is itself a finite-automaton stage.
Friedl [4] explains why alternations must list longer spellings first
(`postgresql` before `postgres`) and why boundaries (lookarounds) are needed
to avoid matching `Java` inside `JavaScript`.

**Normalization is a transduction.** Mohri [5] and Beesley & Karttunen [7]
model the mapping from many surface forms to one canonical form with
finite-state transducers. A finite table of spellings is a finite relation,
and every finite relation is regular, so it can be implemented by an FST [6].
This is the role of Stage 2 (`JS → JAVASCRIPT`).

**Patterns over symbols are regular languages.** Once the qualifications are
canonical symbols, a profile ("a language, then one or more frontend
frameworks, then …") is a regular expression over that alphabet. By Kleene's
theorem it is recognized by a finite automaton [1]. ε-NFAs are the natural
translation of `+` and `*`, and the subset construction guarantees an
equivalent DFA [2]. pyformlang [13] implements these constructions and the
equivalence test we use to validate our DFAs.

**A DSL needs a grammar plus semantic checks.** Fowler [12] separates the
syntax of an external DSL from its semantic model and recommends validating
the model after parsing. textX [10] generates the parser and the meta-model
(Python classes) from one grammar, and it allows object processors for checks
that the grammar cannot express. textX parses with PEG [11]: ordered choice,
no ambiguity, unlimited lookahead, so the grammar works as written without
being converted to CNF or LL(1). The CNF transformation [1] remains useful to
reason about the grammar (RAA3) and to apply CYK.

**Automated ranking of candidates is risky.** Raghavan et al. [9] review
commercial hiring tools and show that scores and rankings can encode bias and
are hard to audit. The project statement also asks ResumeLens *not* to rank or
make hiring decisions.

## How they inform our design

| Finding | Decision in ResumeLens |
|---|---|
| Cascaded extraction [8] | 4 independent stages with explicit data contracts (`docs/02-module-design.md`) |
| Regex alternation order and boundaries [4] | longest-first alternations and `(?<![\w#+.])…(?![\w#+])` boundaries in `extraction.py` |
| Finite relations are regular, FSTs normalize [5], [7] | `NORMALIZATION_MAP` + `QualificationTransducer` (Stage 2) |
| Profiles are regular languages over canonical symbols [1] | each profile is a block pattern `B1+ B2+ … Bk*`; one ε-NFA per profile built mechanically (Thompson-style) |
| ε-NFA ≡ DFA [2], pyformlang [13] | run a readable DFA, prove with `is_equivalent_to` that it matches the ε-NFA |
| Sorting removes order as a source of variation | canonical order before recognition, so the automata stay linear (one state per block) |
| DSL = grammar + semantic model [10], [12] | `candidate.tx` for lexical/syntax rules, object processors for consistency rules |
| PEG parsing [11] vs. CNF [1] | readable `.tx` grammar in the code, CNF derivation shown in `docs/06-grammar.md` |
| Ranking risks [9] | the pipeline outputs ACCEPTED/REJECTED per profile with the reason (word or missing blocks), never a ranking |
