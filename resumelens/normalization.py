#2A
from typing import List, Tuple, Dict, Set


class QualificationTransducer:
    """Finite-state transducer M = (Q, Σ, Γ, δ, ω, q0, F) for skill normalization."""

    def __init__(self, name: str, transitions: Dict[Tuple[str, str], Tuple[str, str]]):
        """Initialize FST with name and transition table."""
        self.name = name
        self.transitions = transitions
        self.states: Set[str] = set()
        self.alphabet_in: Set[str] = set()
        self.alphabet_out: Set[str] = set()
        self.initial = "q0"
        self.accepting = {"q_accept"}

        for (state, inp), (next_state, out) in transitions.items():
            self.states.add(state)
            self.states.add(next_state)
            self.alphabet_in.add(inp)
            for char in out:
                self.alphabet_out.add(char)

    def formal_definition(self) -> Dict:
        """Return 7-tuple formal definition (Q, Σ, Γ, δ, ω, q0, F)."""
        return {
            "name": self.name,
            "Q": self.states,
            "Σ": self.alphabet_in,
            "Γ": self.alphabet_out,
            "δ": {k: v[0] for k, v in self.transitions.items()},
            "ω": {k: v[1] for k, v in self.transitions.items()},
            "q0": self.initial,
            "F": self.accepting,
        }

    def process(self, input_str: str) -> Tuple[bool, str]:
        """Process input string through FST. Returns (accepted: bool, output: str)."""
        current_state = self.initial
        output = ""
        for char in input_str.lower():
            key = (current_state, char)
            if key not in self.transitions:
                return False, ""
            next_state, out_chars = self.transitions[key]
            current_state = next_state
            output += out_chars
        return (current_state in self.accepting, output)

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


def normalize_skill(skill: str) -> str:
    """Normalize single skill to canonical form. Raises ValueError if unknown."""
    normalized = NORMALIZATION_MAP.get(skill.lower())
    if normalized is None:
        raise ValueError(f"Unknown skill: {skill}")
    return normalized


def normalize_skills(raw_skills: List[str]) -> List[str]:
    """Normalize list of skills, preserving order. Raises on first unknown."""
    return [normalize_skill(skill) for skill in raw_skills]


def normalize_skills_safe(raw_skills: List[str]) -> Tuple[List[str], List[str]]:
    """Normalize skills gracefully. Returns (normalized, unknown)."""
    normalized = []
    unknown = []
    for skill in raw_skills:
        try:
            normalized.append(normalize_skill(skill))
        except ValueError:
            unknown.append(skill)
    return normalized, unknown


# Stage 3 — Pattern recognition with finite automata
# For each profile: M = (Q, Σ, δ, q0, F) matching normalized skills against acceptance criteria.
# Classification: Full Stack Developer, ML Engineer, Backend Engineer, Data Engineer.


if __name__ == "__main__":
    raw = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    normalized = normalize_skills(raw)
    print(f"Raw:        {raw}")
    print(f"Normalized: {normalized}")