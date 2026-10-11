"""Stage 3 — Qualification pattern recognition with finite automata.

Every profile pattern (patterns.py) is turned into an automaton over the
canonical qualifications of that profile. The word read by the automaton is
the candidate's canonical sequence (sorting.canonical_order), so a résumé is
ACCEPTED for a profile when that word belongs to the profile language, e.g.

    Full Stack Developer:  LANGUAGE+ FRONTEND+ BACKEND+ DATABASE+ API* VCS+

Two equivalent machines are built from the same pattern:

  * build_enfa: the direct translation of the pattern, one ε-NFA fragment per
    block (ε lets the machine leave a block or skip an optional one).
  * build_dfa:  a DFA with one state per block, used to run the words. Its
    states have readable names, which is what we draw in docs/05-automata.md.

Both are pyformlang automata and the tests check they accept the same language.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton, Epsilon, EpsilonNFA, State, Symbol)

from resumelens.patterns import PATTERNS, ProfilePattern, get_pattern
from resumelens.sorting import canonical_order

ACCEPTED, REJECTED = "ACCEPTED", "REJECTED"
START = "q0"


@dataclass
class Recognition:
    profile: str
    title: str
    word: List[str]
    accepted: bool
    trace: List[str] = field(default_factory=list)
    missing_blocks: List[str] = field(default_factory=list)

    @property
    def result(self) -> str:
        return ACCEPTED if self.accepted else REJECTED


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def build_enfa(pattern: ProfilePattern) -> EpsilonNFA:
    """
    ε-NFA of a pattern. For block i there is a state p_i (before the block) and
    q_i (inside it):

        p_i --s--> q_i,  q_i --s--> q_i   for every s in block i
        q_i --ε--> p_{i+1}
        p_i --ε--> p_{i+1}                 only if block i is optional

    Start state p_0, accepting state p_n.
    """
    enfa = EpsilonNFA()
    n = len(pattern.blocks)
    enfa.add_start_state(State("p0"))
    enfa.add_final_state(State(f"p{n}"))
    for i, block in enumerate(pattern.blocks):
        before, inside, after = State(f"p{i}"), State(f"q{i}"), State(f"p{i + 1}")
        for skill in block.skills:
            enfa.add_transition(before, Symbol(skill), inside)
            enfa.add_transition(inside, Symbol(skill), inside)
        enfa.add_transition(inside, Epsilon(), after)
        if not block.required:
            enfa.add_transition(before, Epsilon(), after)
    return enfa


def _can_skip(pattern: ProfilePattern, start: int, end: int) -> bool:
    """True when every block strictly between start and end is optional."""
    return all(not b.required for b in pattern.blocks[start + 1:end])


def transition_table(pattern: ProfilePattern) -> Dict[Tuple[str, str], str]:
    """
    δ of the DFA. States are q0 and one state per block meaning "the last
    qualification read belongs to this block". From the block i (q0 is i = -1)
    the machine can read a qualification of block j when j == i (same block
    again) or j > i and all blocks in between are optional. Missing pairs go to
    an implicit trap state.
    """
    names = [START] + [b.name for b in pattern.blocks]
    delta = {}
    for i in range(-1, len(pattern.blocks)):
        for j, block in enumerate(pattern.blocks):
            if j == i or (j > i and _can_skip(pattern, i, j)):
                for skill in block.skills:
                    delta[(names[i + 1], skill)] = names[j + 1]
    return delta


def accepting_states(pattern: ProfilePattern) -> List[str]:
    """Blocks after which every remaining block is optional."""
    n = len(pattern.blocks)
    return [b.name for i, b in enumerate(pattern.blocks) if _can_skip(pattern, i, n)]


def build_dfa(pattern: ProfilePattern) -> DeterministicFiniteAutomaton:
    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(State(START))
    for name in accepting_states(pattern):
        dfa.add_final_state(State(name))
    for (src, skill), dst in transition_table(pattern).items():
        dfa.add_transition(State(src), Symbol(skill), State(dst))
    return dfa


def formal_definition(profile: str) -> Dict:
    """5-tuple M = (Q, Σ, δ, q0, F) of the DFA of a profile."""
    pattern = get_pattern(profile)
    return {
        "Q": [START] + [b.name for b in pattern.blocks],
        "Σ": pattern.alphabet,
        "δ": transition_table(pattern),
        "q0": START,
        "F": accepting_states(pattern),
    }


_DFA_CACHE: Dict[str, DeterministicFiniteAutomaton] = {}


def get_dfa(profile: str) -> DeterministicFiniteAutomaton:
    pattern = get_pattern(profile)
    if pattern.key not in _DFA_CACHE:
        _DFA_CACHE[pattern.key] = build_dfa(pattern)
    return _DFA_CACHE[pattern.key]


# ---------------------------------------------------------------------------
# Recognition
# ---------------------------------------------------------------------------

def _trace(pattern: ProfilePattern, word: List[str]) -> List[str]:
    delta = transition_table(pattern)
    state, visited = START, [START]
    for skill in word:
        state = delta.get((state, skill), "TRAP")
        visited.append(state)
        if state == "TRAP":
            break
    return visited


def recognize(normalized_skills: List[str], profile: str) -> Recognition:
    """Run the profile automaton on the canonical sequence of the candidate."""
    pattern = get_pattern(profile)
    word = canonical_order(normalized_skills, pattern.key)
    accepted = get_dfa(pattern.key).accepts([Symbol(s) for s in word])
    missing = [b.name for b in pattern.blocks
               if b.required and not any(s in b.skills for s in word)]
    return Recognition(pattern.key, pattern.title, word, accepted, _trace(pattern, word), missing)


def recognize_all(normalized_skills: List[str]) -> List[Recognition]:
    """One result per profile, always in the same order (no ranking)."""
    return [recognize(normalized_skills, key) for key in PATTERNS]


def accepted_profiles(normalized_skills: List[str]) -> List[str]:
    return [r.title for r in recognize_all(normalized_skills) if r.accepted]


# ---------------------------------------------------------------------------
# Diagrams
# ---------------------------------------------------------------------------

def to_dot(profile: str) -> str:
    """
    Graphviz source of the DFA. Edges are grouped by block (one arrow labelled
    FRONTEND instead of one arrow per framework), otherwise the drawing is
    unreadable. The trap state is omitted.
    """
    pattern = get_pattern(profile)
    edges = {}
    for (src, skill), dst in transition_table(pattern).items():
        edges.setdefault((src, dst), pattern.blocks[pattern.block_of(skill)].name)
    lines = [f'digraph "{pattern.key}" {{', "  rankdir=LR;", '  node [shape=circle];',
             '  start [shape=point];']
    lines += [f'  "{name}" [shape=doublecircle];' for name in accepting_states(pattern)]
    lines.append(f'  start -> "{START}";')
    lines += [f'  "{src}" -> "{dst}" [label="{label}"];' for (src, dst), label in edges.items()]
    lines.append("}")
    return "\n".join(lines) + "\n"


def export_diagrams(directory: str = "docs/diagrams") -> List[str]:
    """Write one .dot file per profile (render with: dot -Tpng file.dot -o file.png)."""
    from pathlib import Path

    paths = []
    for key in PATTERNS:
        path = Path(directory) / f"automaton_{key.lower()}.dot"
        path.write_text(to_dot(key), encoding="utf-8")
        paths.append(str(path))
    return paths


if __name__ == "__main__":
    for r in recognize_all(["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]):
        print(f"{r.title:28} {r.result:9} {' '.join(r.word)}")
