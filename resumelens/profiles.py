from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Profile:
    """Represents a candidate profile classification."""

    name: str
    score: float  # 0.0 to 1.0
    matched_skills: List[str]
    missing_skills: List[str]
    category_scores: Dict[str, int]


class ProfileClassifier:
    """
    Finite automaton for profile recognition.
    
    M = (Q, Σ, δ, q0, F)
    
    Q  = Profile states {full_stack, ml_engineer, software, ai_data}
    Σ  = Normalized skills alphabet {JAVASCRIPT, PYTHON, TENSORFLOW, ...}
    δ  = Transition function: if skill_count[category] >= threshold → profile
    q0 = Initial state (no profile yet)
    F  = Accepting states (any profile matched)
    """

    def __init__(self):
        """Initialize profile definitions with requirements and weights."""
        self.profiles = self._define_profiles()

    def _define_profiles(self) -> Dict[str, Dict]:
        """we define the 4 candidate profiles with category requirements and weights."""
        return {
            "Full Stack Developer": {
                "requirements": {
                    "programming_language": 1,
                    "frontend_framework": 1,
                    "backend_framework": 1,
                    "database": 1,
                },
                "category_weights": {
                    "programming_language": 0.2,
                    "frontend_framework": 0.25,
                    "backend_framework": 0.25,
                    "database": 0.2,
                    "tool_technology": 0.1,
                },
                "skill_weights": {
                    "JAVASCRIPT": 1.0,
                    "TYPESCRIPT": 0.9,
                    "REACT": 1.0,
                    "ANGULAR": 0.9,
                    "VUE": 0.8,
                    "NODE_JS": 1.0,
                    "EXPRESS": 0.95,
                    "DJANGO": 0.9,
                    "FLASK": 0.85,
                    "FASTAPI": 0.85,
                    "POSTGRESQL": 1.0,
                    "MONGODB": 0.9,
                    "REDIS": 0.85,
                    "MYSQL": 0.85,
                    "GIT": 0.9,
                    "DOCKER": 0.85,
                    "REST": 0.8,
                },
            },
            "Machine Learning Engineer": {
                "requirements": {
                    "programming_language": 1,
                    "ml_framework": 2,
                    "data_science_library": 2,
                    "database": 1,
                },
                "category_weights": {
                    "programming_language": 0.15,
                    "ml_framework": 0.35,
                    "data_science_library": 0.35,
                    "database": 0.1,
                    "tool_technology": 0.05,
                },
                "skill_weights": {
                    "PYTHON": 1.0,
                    "R": 0.8,
                    "JULIA": 0.7,
                    "TENSORFLOW": 1.0,
                    "PYTORCH": 1.0,
                    "KERAS": 0.95,
                    "JAX": 0.85,
                    "SCIKIT_LEARN": 0.95,
                    "PANDAS": 0.95,
                    "NUMPY": 0.95,
                    "SCIPY": 0.9,
                    "POSTGRESQL": 0.8,
                    "MONGODB": 0.75,
                    "GIT": 0.7,
                    "JUPYTER": 0.8,
                    "MACHINE_LEARNING": 1.0,
                },
            },
            "Software profile": {
                "requirements": {
                    "programming_language": 1,
                    "backend_framework": 1,
                    "database": 1,
                    "tool_technology": 1,
                },
                "category_weights": {
                    "programming_language": 0.25,
                    "backend_framework": 0.35,
                    "database": 0.25,
                    "tool_technology": 0.15,
                },
                "skill_weights": {
                    "PYTHON": 1.0,
                    "JAVA": 1.0,
                    "GO": 0.95,
                    "JAVASCRIPT": 0.85,
                    "RUST": 0.9,
                    "DJANGO": 1.0,
                    "FASTAPI": 0.95,
                    "SPRING": 0.95,
                    "EXPRESS": 0.85,
                    "FLASK": 0.8,
                    "POSTGRESQL": 1.0,
                    "MONGODB": 0.9,
                    "MYSQL": 0.85,
                    "REDIS": 0.9,
                    "GIT": 0.9,
                    "DOCKER": 0.95,
                    "KUBERNETES": 0.9,
                    "REST": 0.9,
                    "DEVOPS": 0.85,
                    "CI_CD": 0.85,
                },
            },
            "AI/Data profile": {
                "requirements": {
                    "programming_language": 1,
                    "database": 2,
                    "ml_framework": 1,
                    "tool_technology": 1,
                },
                "category_weights": {
                    "programming_language": 0.15,
                    "database": 0.35,
                    "ml_framework": 0.35,
                    "tool_technology": 0.15,
                },
                "skill_weights": {
                    "PYTHON": 1.0,
                    "SCALA": 0.9,
                    "SQL": 1.0,
                    "JAVA": 0.85,
                    "POSTGRESQL": 0.9,
                    "MYSQL": 0.85,
                    "MONGODB": 0.9,
                    "CASSANDRA": 0.95,
                    "HIVE": 0.95,
                    "SPARK": 1.0,
                    "HADOOP": 0.95,
                    "KAFKA": 0.95,
                    "TENSORFLOW": 0.95,
                    "PYTORCH": 0.95,
                    "AIRFLOW": 0.9,
                    "ETL": 0.95,
                    "MACHINE_LEARNING": 1.0,
                    "GIT": 0.8,
                    "DOCKER": 0.85,
                    "AWS": 0.85,
                },
            },
        }

    def _categorize_skill(self, skill: str) -> str:
        """Map normalized skill to its category."""
        categories = {
            "programming_language": [
                "PYTHON",
                "JAVASCRIPT",
                "TYPESCRIPT",
                "JAVA",
                "GO",
                "RUST",
                "R",
                "SCALA",
                "JULIA",
                "SQL",
                "C",
                "CPLUSPLUS",
                "CSHARP",
            ],
            "frontend_framework": [
                "REACT",
                "ANGULAR",
                "VUE",
                "SVELTE",
                "NEXTJS",
                "NUXT",
            ],
            "backend_framework": [
                "NODE_JS",
                "EXPRESS",
                "DJANGO",
                "FLASK",
                "FASTAPI",
                "SPRING",
                "SPRING_BOOT",
                "RAILS",
            ],
            "database": [
                "POSTGRESQL",
                "MYSQL",
                "MONGODB",
                "REDIS",
                "CASSANDRA",
                "ELASTICSEARCH",
                "DYNAMODB",
            ],
            "ml_framework": [
                "TENSORFLOW",
                "PYTORCH",
                "KERAS",
                "JAX",
                "MXNET",
            ],
            "data_science_library": [
                "SCIKIT_LEARN",
                "PANDAS",
                "NUMPY",
                "SCIPY",
                "PLOTLY",
                "MATPLOTLIB",
            ],
            "big_data_tool": [
                "SPARK",
                "HADOOP",
                "KAFKA",
                "AIRFLOW",
                "HIVE",
            ],
            "tool_technology": [
                "GIT",
                "GITHUB",
                "DOCKER",
                "KUBERNETES",
                "AWS",
                "GCP",
                "AZURE",
                "JENKINS",
                "CI_CD",
                "REST",
                "GRAPHQL",
                "JUPYTER",
                "DEVOPS",
                "MACHINE_LEARNING",
                "ETL",
            ],
        }

        for category, skills in categories.items():
            if skill in skills:
                return category
        
        return "tool_technology"

    def _count_category_matches(
        self, normalized_skills: List[str], profile_name: str
    ) -> Tuple[Dict[str, int], List[str], List[str]]:
        """Count how many skills from each category the candidate has."""
        profile = self.profiles[profile_name]
        requirements = profile["requirements"]

        category_counts = {cat: 0 for cat in requirements.keys()}
        matched_skills = []

        for skill in normalized_skills:
            category = self._categorize_skill(skill)
            if category in category_counts:
                category_counts[category] += 1
                matched_skills.append(skill)

        missing = []
        for category, required_count in requirements.items():
            if category_counts.get(category, 0) < required_count:
                missing.append(category)

        return category_counts, matched_skills, missing

    def _calculate_score(
        self,
        normalized_skills: List[str],
        category_counts: Dict[str, int],
        profile_name: str,
    ) -> float:
        """Calculate matching score for profile (0.0 to 1.0)."""
        profile = self.profiles[profile_name]
        requirements = profile["requirements"]
        category_weights = profile["category_weights"]
        skill_weights = profile["skill_weights"]

        category_score = 0.0
        skill_score = 0.0

        for category, required_count in requirements.items():
            actual_count = category_counts.get(category, 0)
            coverage = min(actual_count / required_count, 1.0)
            category_score += coverage * category_weights.get(category, 0)

        matched_weight_sum = 0.0
        max_possible_weight = sum(skill_weights.values())

        for skill in normalized_skills:
            if skill in skill_weights:
                matched_weight_sum += skill_weights[skill]

        if max_possible_weight > 0:
            skill_score = min(matched_weight_sum / max_possible_weight, 1.0)

        final_score = (0.7 * category_score) + (0.3 * skill_score)
        return round(final_score, 2)

    def classify(
        self, normalized_skills: List[str]
    ) -> Tuple[Optional[Profile], List[Profile]]:
        """Classify candidate to best matching profile."""
        all_results = []

        for profile_name in self.profiles.keys():
            category_counts, matched, missing = self._count_category_matches(
                normalized_skills, profile_name
            )

            score = self._calculate_score(
                normalized_skills, category_counts, profile_name
            )

            all_skills_for_profile = set()
            for skill, weight in self.profiles[profile_name]["skill_weights"].items():
                all_skills_for_profile.add(skill)

            missing_skills = sorted(
                list(all_skills_for_profile - set(matched))
            )

            profile = Profile(
                name=profile_name,
                score=score,
                matched_skills=sorted(matched),
                missing_skills=missing_skills,
                category_scores=category_counts,
            )

            all_results.append(profile)

        all_results.sort(key=lambda p: p.score, reverse=True)
        best_profile = all_results[0] if all_results else None

        return best_profile, all_results


def classify_candidate(normalized_skills: List[str]) -> Tuple[Profile, List[Profile]]:
    """
    Classify a candidate based on normalized skills.
    
    This is the public API for Stage 2B classification.
    
    Args:
        normalized_skills: List of normalized skill strings (from Stage 2A)
        
    Returns:
        (best_matching_profile, all_profiles_ranked)
    """
    classifier = ProfileClassifier()
    return classifier.classify(normalized_skills)


# Stage 3 — Pattern recognition with finite automata
# For each profile: M = (Q, Σ, δ, q0, F) matching normalized skills against acceptance criteria.
# Classification: Full Stack Developer, Machine Learning Engineer, Software profile, AI/Data profile.


if __name__ == "__main__":
    wednesday_skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    best, all_profiles = classify_candidate(wednesday_skills)

    print(f"Best Profile: {best.name}")
    print(f"Score: {best.score}")
    print(f"Matched Skills: {best.matched_skills}")
    print(f"Missing Skills: {best.missing_skills}")
    print()
    print("All Profiles:")
    for profile in all_profiles:
        print(f"  {profile.name}: {profile.score}")