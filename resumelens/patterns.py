"""Qualification patterns of the four professional profiles.

A pattern is an ordered list of blocks. Each block groups canonical
qualifications (Stage 2 output) that play the same role in the profile and
says whether the block is required ("+": one or more) or optional ("*": zero
or more). The same definition drives two things:

  * the canonical order used to sort a candidate's qualifications (sorting.py)
  * the finite automaton that recognizes the profile (recognition.py)

so the four profiles go through exactly the same code.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

REQUIRED, OPTIONAL = "+", "*"


@dataclass(frozen=True)
class Block:
    name: str
    skills: Tuple[str, ...]
    mode: str = REQUIRED

    @property
    def required(self) -> bool:
        return self.mode == REQUIRED


@dataclass(frozen=True)
class ProfilePattern:
    key: str
    title: str
    blocks: Tuple[Block, ...]

    @property
    def alphabet(self) -> List[str]:
        """Σ of the profile automaton, already in canonical order."""
        return [s for b in self.blocks for s in b.skills]

    def block_of(self, skill: str) -> Optional[int]:
        for i, b in enumerate(self.blocks):
            if skill in b.skills:
                return i
        return None

    def regex(self) -> str:
        """Block-level regular expression, e.g. LANGUAGE+ FRONTEND+ ... API* VCS+."""
        return " ".join(f"{b.name}{b.mode}" for b in self.blocks)


# Blocks shared by several profiles.
VCS = Block("VCS", ("GIT", "GITHUB", "GITLAB"))
SQL_DATABASES = ("POSTGRESQL", "MYSQL", "SQL_SERVER", "SQLITE", "ORACLE", "SQL")
NOSQL_DATABASES = ("MONGODB", "REDIS", "CASSANDRA", "ELASTICSEARCH", "NOSQL")
BACKEND_FRAMEWORKS = ("NODE_JS", "EXPRESS", "DJANGO", "FLASK", "FAST_API", "SPRING_BOOT", "RAILS")
CLOUD = ("DOCKER", "KUBERNETES", "AWS", "AZURE", "GCP")

FULL_STACK = ProfilePattern(
    "FULL_STACK_DEVELOPER", "Full Stack Developer", (
        Block("LANGUAGE", ("JAVASCRIPT", "TYPESCRIPT")),
        Block("FRONTEND", ("REACT", "ANGULAR", "VUE", "SVELTE", "NEXT_JS")),
        Block("BACKEND", BACKEND_FRAMEWORKS),
        Block("DATABASE", SQL_DATABASES + NOSQL_DATABASES),
        Block("API", ("REST", "GRAPHQL"), OPTIONAL),
        VCS,
    ))

ML_ENGINEER = ProfilePattern(
    "MACHINE_LEARNING_ENGINEER", "Machine Learning Engineer", (
        Block("LANGUAGE", ("PYTHON",)),
        Block("DATA_LIBRARY", ("PANDAS", "NUMPY")),
        Block("ML_LIBRARY", ("SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS")),
        Block("ML_PRACTICE", ("MACHINE_LEARNING", "DEEP_LEARNING", "PREDICTIVE_MODELS"), OPTIONAL),
        Block("DATABASE", SQL_DATABASES),
        VCS,
    ))

# Team-defined profile (software engineering).
BACKEND = ProfilePattern(
    "BACKEND_DEVELOPER", "Backend Developer", (
        Block("LANGUAGE", ("JAVA", "KOTLIN", "PYTHON", "GOLANG", "CSHARP", "RUST",
                           "JAVASCRIPT", "TYPESCRIPT")),
        Block("FRAMEWORK", BACKEND_FRAMEWORKS),
        Block("API", ("REST", "GRAPHQL", "GRPC", "SOAP")),
        Block("DATABASE", SQL_DATABASES + NOSQL_DATABASES),
        Block("DEVOPS", CLOUD + ("CI_CD", "JENKINS", "DEVOPS"), OPTIONAL),
        VCS,
    ))

# Team-defined profile (AI / data).
DATA_ENGINEER = ProfilePattern(
    "DATA_ENGINEER", "Data Engineer", (
        Block("LANGUAGE", ("PYTHON", "SCALA", "JAVA")),
        Block("PROCESSING", ("SPARK", "PYSPARK", "KAFKA", "AIRFLOW")),
        Block("PIPELINES", ("ETL", "DATA_PROCESSING"), OPTIONAL),
        Block("DATABASE", SQL_DATABASES + NOSQL_DATABASES),
        Block("CLOUD", CLOUD, OPTIONAL),
        VCS,
    ))

PATTERNS: Dict[str, ProfilePattern] = {p.key: p for p in (FULL_STACK, ML_ENGINEER, BACKEND, DATA_ENGINEER)}


def get_pattern(profile: str) -> ProfilePattern:
    """Accepts the key (FULL_STACK_DEVELOPER) or the title (Full Stack Developer)."""
    for p in PATTERNS.values():
        if profile in (p.key, p.title):
            return p
    raise KeyError(f"Unknown profile: {profile}")
