"""Stage 2 — Qualification normalization with finite-state transducers (pyformlang).

Every equivalence class of spellings is a finite-state transducer
M = (Q, Σ, Γ, δ, ω, q0, F) built with ``pyformlang.fst.FST``:

* Q  — one state per prefix of a spelling (a trie), plus the accepting state.
* Σ  — the characters of the spellings, in lower and upper case
       (the machine itself does the case folding: δ(q, 'j') = δ(q, 'J')).
* Γ  — the canonical tokens (JAVASCRIPT, REACT, ...).
* δ  — reading a character moves to the state of the longer prefix;
       from the state of a complete spelling an ε-move goes to q_accept.
* ω  — every character transition writes ε (nothing); the final ε-move
       writes the canonical token. So "React.js" ↦ REACT.
* q0 — the empty prefix.   F = {q_accept}.

``TRANSDUCERS`` holds one transducer per canonical qualification (these are the
machines documented and drawn in docs/04-transducers.md). ``NORMALIZER`` is
their union, a single deterministic FST used at run time by ``normalize_skill``.
A spelling that the FST does not accept has no translation and is reported
as unknown.
"""
from collections import defaultdict
from typing import Dict, Iterable, List, Set, Tuple

from pyformlang.fst import FST

EPSILON = "epsilon"          # pyformlang's input symbol for ε-moves
START, ACCEPT = "q0", "q_accept"


class QualificationTransducer:
    """Generic FST M = (Q, Σ, Γ, δ, ω, q0, F) given as a transition table.

    ``transitions`` maps (state, input_char) -> (next_state, output_string).
    The table is loaded into a ``pyformlang.fst.FST``; ``process`` runs
    pyformlang's ``translate``.
    """

    def __init__(self, name: str, transitions: Dict[Tuple[str, str], Tuple[str, str]],
                 initial: str = START, accepting: Iterable[str] = (ACCEPT,)):
        self.name = name
        self.transitions = transitions
        self.initial = initial
        self.accepting: Set[str] = set(accepting)

        self.fst = FST()
        self.fst.add_start_state(initial)
        for state in self.accepting:
            self.fst.add_final_state(state)
        for (state, symbol), (next_state, out) in transitions.items():
            self.fst.add_transition(state, symbol, next_state, list(out))

    @property
    def states(self) -> Set[str]:
        return set(self.fst.states)

    @property
    def alphabet_in(self) -> Set[str]:
        return set(self.fst.input_symbols) - {EPSILON}

    @property
    def alphabet_out(self) -> Set[str]:
        return set(self.fst.output_symbols)

    def formal_definition(self) -> Dict:
        """Return the 7-tuple (Q, Σ, Γ, δ, ω, q0, F) read from the pyformlang FST."""
        return _formal_definition(self.name, self.fst)

    def process(self, input_str: str) -> Tuple[bool, str]:
        """Translate ``input_str`` (case-insensitive). Returns (accepted, output)."""
        outputs = list(self.fst.translate(list(input_str.lower())))
        if not outputs:
            return False, ""
        return True, "".join(outputs[0])


NORMALIZATION_MAP: Dict[str, str] = {
    # Programming languages
    "js": "JAVASCRIPT",
    "javascript": "JAVASCRIPT",
    "ts": "TYPESCRIPT",
    "typescript": "TYPESCRIPT",
    "py": "PYTHON",
    "python": "PYTHON",
    "python3": "PYTHON",
    "python 3": "PYTHON",
    "java": "JAVA",
    "c#": "CSHARP",
    "c++": "CPLUSPLUS",
    "go": "GOLANG",
    "kotlin": "KOTLIN",
    "rust": "RUST",
    "scala": "SCALA",
    "sql": "SQL",

    # Frontend frameworks
    "react": "REACT",
    "react.js": "REACT",
    "reactjs": "REACT",
    "react js": "REACT",
    "angular": "ANGULAR",
    "angular.js": "ANGULAR",
    "angularjs": "ANGULAR",
    "vue": "VUE",
    "vue.js": "VUE",
    "vuejs": "VUE",
    "next": "NEXT_JS",
    "next.js": "NEXT_JS",
    "nextjs": "NEXT_JS",
    "svelte": "SVELTE",

    # Backend frameworks
    "node": "NODE_JS",
    "node.js": "NODE_JS",
    "nodejs": "NODE_JS",
    "node js": "NODE_JS",
    "express": "EXPRESS",
    "express.js": "EXPRESS",
    "django": "DJANGO",
    "flask": "FLASK",
    "spring": "SPRING_BOOT",
    "spring boot": "SPRING_BOOT",
    "spring-boot": "SPRING_BOOT",
    "fastapi": "FAST_API",
    "fast-api": "FAST_API",
    "fast api": "FAST_API",
    "rails": "RAILS",

    # Data science & ML
    "pandas": "PANDAS",
    "numpy": "NUMPY",
    "num py": "NUMPY",
    "num-py": "NUMPY",
    "scikit-learn": "SCIKIT_LEARN",
    "scikit learn": "SCIKIT_LEARN",
    "sklearn": "SCIKIT_LEARN",
    "sk-learn": "SCIKIT_LEARN",
    "tensorflow": "TENSORFLOW",
    "tensor-flow": "TENSORFLOW",
    "tensor flow": "TENSORFLOW",
    "pytorch": "PYTORCH",
    "py torch": "PYTORCH",
    "py-torch": "PYTORCH",
    "keras": "KERAS",
    "matplotlib": "MATPLOTLIB",
    "pyspark": "PYSPARK",
    "py-spark": "PYSPARK",
    "spark": "SPARK",

    # Databases
    "postgres": "POSTGRESQL",
    "postgresql": "POSTGRESQL",
    "mysql": "MYSQL",
    "my-sql": "MYSQL",
    "my sql": "MYSQL",
    "mongodb": "MONGODB",
    "mongo": "MONGODB",
    "redis": "REDIS",
    "sqlite": "SQLITE",
    "sql server": "SQL_SERVER",
    "sqlserver": "SQL_SERVER",
    "oracle": "ORACLE",
    "cassandra": "CASSANDRA",
    "elasticsearch": "ELASTICSEARCH",
    "elastic-search": "ELASTICSEARCH",
    "nosql": "NOSQL",
    "no sql": "NOSQL",
    "no-sql": "NOSQL",

    # Tools & platforms
    "git": "GIT",
    "github": "GITHUB",
    "git-hub": "GITHUB",
    "gitlab": "GITLAB",
    "git-lab": "GITLAB",
    "docker": "DOCKER",
    "kubernetes": "KUBERNETES",
    "k8s": "KUBERNETES",
    "aws": "AWS",
    "azure": "AZURE",
    "gcp": "GCP",
    "google cloud": "GCP",
    "jenkins": "JENKINS",
    "airflow": "AIRFLOW",
    "kafka": "KAFKA",

    # API & protocols
    "rest": "REST",
    "restful": "REST",
    "rest api": "REST",
    "rest apis": "REST",
    "restful api": "REST",
    "restful apis": "REST",
    "graphql": "GRAPHQL",
    "graph-ql": "GRAPHQL",
    "grpc": "GRPC",
    "soap": "SOAP",

    # Competencies
    "machine learning": "MACHINE_LEARNING",
    "machine-learning": "MACHINE_LEARNING",
    "ml": "MACHINE_LEARNING",
    "deep learning": "DEEP_LEARNING",
    "deep-learning": "DEEP_LEARNING",
    "predictive models": "PREDICTIVE_MODELS",
    "predictive modeling": "PREDICTIVE_MODELS",
    "data processing": "DATA_PROCESSING",
    "data-processing": "DATA_PROCESSING",
    "etl": "ETL",
    "ci cd": "CI_CD",
    "ci/cd": "CI_CD",
    "devops": "DEVOPS",
    "dev-ops": "DEVOPS",
}


def _formal_definition(name: str, fst: FST) -> Dict:
    delta, omega = {}, {}
    for (state, symbol), moves in fst.transitions.items():
        for next_state, out in moves:
            key = (state, "ε" if symbol == EPSILON else symbol)
            delta[key] = next_state
            omega[key] = "".join(out) or "ε"
    return {
        "name": name,
        "Q": set(fst.states),
        "Σ": set(fst.input_symbols) - {EPSILON},
        "Γ": set(fst.output_symbols),
        "δ": delta,
        "ω": omega,
        "q0": next(iter(fst.start_states)),
        "F": set(fst.final_states),
    }


def _state(prefix: str) -> str:
    return START if prefix == "" else f"q[{prefix}]"


def build_transducer(spellings: Iterable[str], canonical_of) -> FST:
    """Trie-shaped FST that reads any of ``spellings`` and writes its canonical token.

    ``canonical_of(spelling)`` gives the token written by the final ε-move.
    Upper- and lower-case versions of every letter share the same transition.
    """
    fst = FST()
    fst.add_start_state(START)
    fst.add_final_state(ACCEPT)
    added = set()                                   # shared prefixes add each move once
    for spelling in spellings:
        for i, char in enumerate(spelling):
            source, target = _state(spelling[:i]), _state(spelling[:i + 1])
            for symbol in {char, char.upper()}:
                if (source, symbol) not in added:
                    added.add((source, symbol))
                    fst.add_transition(source, symbol, target, [])
        fst.add_transition(_state(spelling), EPSILON, ACCEPT, [canonical_of(spelling)])
    return fst


def _group_by_canonical(table: Dict[str, str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = defaultdict(list)
    for spelling, canonical in table.items():
        groups[canonical].append(spelling)
    return dict(groups)


# One transducer per canonical qualification (documented and drawn) ...
TRANSDUCERS: Dict[str, FST] = {
    canonical: build_transducer(spellings, lambda s, c=canonical: c)
    for canonical, spellings in _group_by_canonical(NORMALIZATION_MAP).items()
}

# ... and their union, the deterministic FST used at run time.
NORMALIZER: FST = build_transducer(NORMALIZATION_MAP, NORMALIZATION_MAP.__getitem__)


def formal_definition(canonical: str) -> Dict:
    """7-tuple of the transducer that writes ``canonical``."""
    return _formal_definition(canonical, TRANSDUCERS[canonical])


def translate(skill: str, fst: FST = NORMALIZER) -> List[str]:
    """All outputs of ``fst`` for ``skill`` (empty list = not accepted)."""
    return ["".join(out) for out in fst.translate(list(skill))]


def to_mermaid(canonical: str) -> str:
    """Mermaid state diagram of a transducer (labels are input : output)."""
    fst = TRANSDUCERS[canonical]
    edges: Dict[Tuple[str, str], Tuple[List[str], str]] = {}
    for (state, symbol), moves in fst.transitions.items():
        for next_state, out in moves:
            if symbol != EPSILON and symbol != symbol.lower():
                continue                      # drawn together with its lower-case twin
            shown = "␣" if symbol == " " else symbol
            label = "ε" if symbol == EPSILON else (
                f"{shown}|{symbol.upper()}" if symbol.upper() != symbol else shown)
            edges[(state, next_state)] = (edges.get((state, next_state), ([], ""))[0] + [label],
                                          "".join(out) or "ε")
    ids = {s: f"s{i}" for i, s in enumerate(sorted(fst.states, key=lambda s: (s != START, len(s), s)))}
    lines = ["stateDiagram-v2", "    direction LR"]
    for state, sid in ids.items():
        lines.append(f'    state "{state}" as {sid}')
    lines.append(f"    [*] --> {ids[START]}")
    for (src, dst), (labels, out) in edges.items():
        text = ", ".join(labels).replace(":", "#58;")
        lines.append(f"    {ids[src]} --> {ids[dst]} : {text} / {out}")
    lines.append(f"    {ids[ACCEPT]} --> [*]")
    return "\n".join(lines)


def write_dot(canonical: str, path) -> None:
    """Graphviz file of a transducer (pyformlang ``write_as_dot``)."""
    TRANSDUCERS[canonical].write_as_dot(str(path))


def normalize_skill(skill: str) -> str:
    """Canonical form of ``skill`` computed by the FST. Raises ValueError if unknown."""
    outputs = translate(skill)
    if not outputs:
        raise ValueError(f"Unknown skill: {skill}")
    return outputs[0]


def normalize_skills(raw_skills: List[str]) -> List[str]:
    """Normalize a list of skills, preserving order. Raises on the first unknown."""
    return [normalize_skill(skill) for skill in raw_skills]


def normalize_skills_safe(raw_skills: List[str]) -> Tuple[List[str], List[str]]:
    """Normalize skills without raising. Returns (normalized, unknown)."""
    normalized, unknown = [], []
    for skill in raw_skills:
        try:
            normalized.append(normalize_skill(skill))
        except ValueError:
            unknown.append(skill)
    return normalized, unknown


if __name__ == "__main__":
    raw = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    print(f"Raw:        {raw}")
    print(f"Normalized: {normalize_skills(raw)}")
