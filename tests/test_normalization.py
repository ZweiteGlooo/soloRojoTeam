"""Stage 2 — Test suite for qualification normalization."""

import pytest
from resumelens.normalization import (
    normalize_skill,
    normalize_skills,
    normalize_skills_safe,
    QualificationTransducer,
    NORMALIZATION_MAP,
)


class TestNormalizeSingleSkill:
    """Test normalize_skill(skill: str) → str."""

    def test_programming_languages(self):
        assert normalize_skill("js") == "JAVASCRIPT"
        assert normalize_skill("javascript") == "JAVASCRIPT"
        assert normalize_skill("JavaScript") == "JAVASCRIPT"
        assert normalize_skill("py") == "PYTHON"
        assert normalize_skill("python") == "PYTHON"
        assert normalize_skill("python3") == "PYTHON"
        assert normalize_skill("java") == "JAVA"

    def test_frontend_frameworks(self):
        assert normalize_skill("react") == "REACT"
        assert normalize_skill("React") == "REACT"
        assert normalize_skill("react.js") == "REACT"
        assert normalize_skill("reactjs") == "REACT"
        assert normalize_skill("react js") == "REACT"
        assert normalize_skill("angular") == "ANGULAR"
        assert normalize_skill("vue") == "VUE"

    def test_backend_frameworks(self):
        assert normalize_skill("node") == "NODE_JS"
        assert normalize_skill("node.js") == "NODE_JS"
        assert normalize_skill("nodejs") == "NODE_JS"
        assert normalize_skill("express") == "EXPRESS"
        assert normalize_skill("django") == "DJANGO"
        assert normalize_skill("flask") == "FLASK"

    def test_databases(self):
        assert normalize_skill("postgres") == "POSTGRESQL"
        assert normalize_skill("postgresql") == "POSTGRESQL"
        assert normalize_skill("mysql") == "MYSQL"
        assert normalize_skill("mongo") == "MONGODB"
        assert normalize_skill("redis") == "REDIS"

    def test_tools_platforms(self):
        assert normalize_skill("git") == "GIT"
        assert normalize_skill("github") == "GITHUB"
        assert normalize_skill("docker") == "DOCKER"
        assert normalize_skill("kubernetes") == "KUBERNETES"
        assert normalize_skill("k8s") == "KUBERNETES"
        assert normalize_skill("aws") == "AWS"

    def test_competencies(self):
        assert normalize_skill("ml") == "MACHINE_LEARNING"
        assert normalize_skill("machine learning") == "MACHINE_LEARNING"
        assert normalize_skill("machine-learning") == "MACHINE_LEARNING"
        assert normalize_skill("etl") == "ETL"
        assert normalize_skill("devops") == "DEVOPS"

    def test_case_insensitive(self):
        assert normalize_skill("JAVASCRIPT") == "JAVASCRIPT"
        assert normalize_skill("JaVaScRiPt") == "JAVASCRIPT"
        assert normalize_skill("REACT") == "REACT"
        assert normalize_skill("PyThOn") == "PYTHON"

    def test_unknown_skill_raises_error(self):
        with pytest.raises(ValueError, match="Unknown skill: BadTech"):
            normalize_skill("BadTech")
        with pytest.raises(ValueError, match="Unknown skill: pytohn"):
            normalize_skill("pytohn")
        with pytest.raises(ValueError, match="Unknown skill: nodejs2"):
            normalize_skill("nodejs2")


class TestNormalizeSkills:
    """Test normalize_skills(raw_skills: List[str]) → List[str]."""

    def test_wednesday_addams_skills(self):
        raw = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
        expected = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
        assert normalize_skills(raw) == expected

    def test_mary_jane_watson_skills(self):
        raw = ["Python", "Django", "PostgreSQL", "Redis", "Docker"]
        expected = ["PYTHON", "DJANGO", "POSTGRESQL", "REDIS", "DOCKER"]
        assert normalize_skills(raw) == expected

    def test_ml_engineer_skills(self):
        raw = ["python", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"]
        expected = [
            "PYTHON",
            "PANDAS",
            "NUMPY",
            "SCIKIT_LEARN",
            "TENSORFLOW",
            "PYTORCH",
        ]
        assert normalize_skills(raw) == expected

    def test_preserves_order(self):
        raw = ["react", "js", "node", "postgres"]
        result = normalize_skills(raw)
        assert result == ["REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL"]
        assert result[0] == "REACT"
        assert result[-1] == "POSTGRESQL"

    def test_empty_list(self):
        assert normalize_skills([]) == []

    def test_single_skill(self):
        assert normalize_skills(["js"]) == ["JAVASCRIPT"]

    def test_duplicate_skills_preserved(self):
        raw = ["js", "python", "js"]
        assert normalize_skills(raw) == ["JAVASCRIPT", "PYTHON", "JAVASCRIPT"]

    def test_raises_on_first_unknown(self):
        with pytest.raises(ValueError, match="Unknown skill: BadTech"):
            normalize_skills(["js", "react", "BadTech", "python"])

    def test_stops_at_first_unknown(self):
        with pytest.raises(ValueError):
            normalize_skills(["js", "UnknownSkill1", "UnknownSkill2"])


class TestNormalizeSkillsSafe:
    """Test normalize_skills_safe(raw_skills) → (normalized, unknown)."""

    def test_all_known_skills(self):
        raw = ["js", "react", "docker"]
        norm, unknown = normalize_skills_safe(raw)
        assert norm == ["JAVASCRIPT", "REACT", "DOCKER"]
        assert unknown == []

    def test_mixed_known_and_unknown(self):
        raw = ["js", "BadTech", "react"]
        norm, unknown = normalize_skills_safe(raw)
        assert norm == ["JAVASCRIPT", "REACT"]
        assert unknown == ["BadTech"]

    def test_all_unknown_skills(self):
        raw = ["UnknownSkill1", "UnknownSkill2"]
        norm, unknown = normalize_skills_safe(raw)
        assert norm == []
        assert unknown == ["UnknownSkill1", "UnknownSkill2"]

    def test_empty_list(self):
        norm, unknown = normalize_skills_safe([])
        assert norm == []
        assert unknown == []

    def test_preserves_order_of_unknowns(self):
        raw = ["BadTech1", "js", "BadTech2", "react"]
        norm, unknown = normalize_skills_safe(raw)
        assert norm == ["JAVASCRIPT", "REACT"]
        assert unknown == ["BadTech1", "BadTech2"]

    def test_wednesday_addams_with_one_unknown(self):
        raw = ["JS", "React.js", "UnknownLib", "Postgres", "Git"]
        norm, unknown = normalize_skills_safe(raw)
        assert norm == ["JAVASCRIPT", "REACT", "POSTGRESQL", "GIT"]
        assert unknown == ["UnknownLib"]

    def test_returns_tuple(self):
        result = normalize_skills_safe(["js"])
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestQualificationTransducer:
    """Test QualificationTransducer class."""

    def test_formal_definition_returns_7tuple(self):
        transitions = {("q0", "a"): ("q1", "A"), ("q1", "b"): ("q_accept", "B")}
        transducer = QualificationTransducer("test", transitions)
        defn = transducer.formal_definition()

        assert "Q" in defn
        assert "Σ" in defn
        assert "Γ" in defn
        assert "δ" in defn
        assert "ω" in defn
        assert "q0" in defn
        assert "F" in defn
        assert defn["name"] == "test"

    def test_formal_definition_components(self):
        transitions = {("q0", "a"): ("q1", "A"), ("q1", "b"): ("q_accept", "B")}
        transducer = QualificationTransducer("ab_upper", transitions)
        defn = transducer.formal_definition()

        assert transducer.initial in defn["Q"]
        assert transducer.accepting.issubset(defn["F"])
        assert "a" in defn["Σ"]
        assert "A" in defn["Γ"]

    def test_process_accepted_input(self):
        transitions = {
            ("q0", "j"): ("q1", "J"),
            ("q1", "s"): ("q_accept", "S"),
        }
        transducer = QualificationTransducer("JS", transitions)
        accepted, output = transducer.process("js")
        assert accepted is True
        assert output == "JS"

    def test_process_case_insensitive(self):
        transitions = {
            ("q0", "j"): ("q1", "J"),
            ("q1", "s"): ("q_accept", "S"),
        }
        transducer = QualificationTransducer("JS", transitions)
        accepted, output = transducer.process("JS")
        assert accepted is True
        assert output == "JS"

    def test_process_rejected_input(self):
        transitions = {
            ("q0", "j"): ("q1", "J"),
            ("q1", "s"): ("q_accept", "S"),
        }
        transducer = QualificationTransducer("JS", transitions)
        accepted, output = transducer.process("java")
        assert accepted is False
        assert output == ""

    def test_process_partial_match_rejected(self):
        transitions = {
            ("q0", "j"): ("q1", "J"),
            ("q1", "s"): ("q_accept", "S"),
        }
        transducer = QualificationTransducer("JS", transitions)
        accepted, output = transducer.process("j")
        assert accepted is False


class TestNormalizationMapConsistency:
    """Test consistency and coverage of NORMALIZATION_MAP."""

    def test_all_keys_are_lowercase(self):
        for key in NORMALIZATION_MAP.keys():
            assert key == key.lower(), f"Key {key} is not lowercase"

    def test_all_values_are_uppercase(self):
        for value in NORMALIZATION_MAP.values():
            assert value == value.upper(), f"Value {value} is not uppercase"

    def test_multiple_keys_same_value_allowed(self):
        """Multiple variations can map to the same canonical form."""
        assert len(NORMALIZATION_MAP) > 100

    def test_table_has_minimum_coverage(self):
        """Ensure table has ~120 entries (within 10% tolerance)."""
        assert 100 < len(NORMALIZATION_MAP) < 140

    def test_categories_present(self):
        """Verify each major category has representatives."""
        categories = {
            "programming_languages": ["js", "python", "java", "go"],
            "frontend_frameworks": ["react", "angular", "vue"],
            "backend_frameworks": ["node", "django", "flask"],
            "databases": ["postgres", "mysql", "mongodb"],
            "tools": ["git", "docker", "kubernetes"],
            "competencies": ["ml", "etl", "devops"],
        }

        for category, examples in categories.items():
            for example in examples:
                assert (
                    example in NORMALIZATION_MAP
                ), f"Missing {example} in {category}"


class TestEdgeCases:
    """Test edge cases and special input."""

    def test_whitespace_variations(self):
        assert normalize_skill("machine learning") == "MACHINE_LEARNING"
        assert normalize_skill("machine-learning") == "MACHINE_LEARNING"
        assert normalize_skill("py torch") == "PYTORCH"
        assert normalize_skill("py-torch") == "PYTORCH"

    def test_punctuation_variations(self):
        assert normalize_skill("react.js") == "REACT"
        assert normalize_skill("reactjs") == "REACT"
        assert normalize_skill("node.js") == "NODE_JS"
        assert normalize_skill("nodejs") == "NODE_JS"

    def test_abbreviations(self):
        assert normalize_skill("py") == "PYTHON"
        assert normalize_skill("js") == "JAVASCRIPT"
        assert normalize_skill("ts") == "TYPESCRIPT"
        assert normalize_skill("ml") == "MACHINE_LEARNING"
        assert normalize_skill("k8s") == "KUBERNETES"

    def test_multiple_dots_slashes(self):
        assert normalize_skill("c++") == "CPLUSPLUS"
        assert normalize_skill("c#") == "CSHARP"
        assert normalize_skill("rest api") == "REST"
        assert normalize_skill("ci/cd") == "CI_CD"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            normalize_skill("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            normalize_skill("   ")

    def test_version_numbers_not_recognized(self):
        """Skills with version numbers are treated as unknown."""
        with pytest.raises(ValueError):
            normalize_skill("python3.9")
        with pytest.raises(ValueError):
            normalize_skill("react18")


class TestIntegrationWithStage1:
    """Test integration with Stage 1 extraction output."""

    def test_wednesday_addams_full_pipeline(self):
        """Wednesday Addams from Stage 1 test fixtures."""
        raw_from_stage1 = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
        normalized = normalize_skills(raw_from_stage1)
        expected = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
        assert normalized == expected

    def test_mary_jane_watson_full_pipeline(self):
        """Mary Jane Watson from Stage 1 test fixtures."""
        raw_from_stage1 = ["Python", "Django", "PostgreSQL", "Redis", "Docker"]
        normalized = normalize_skills(raw_from_stage1)
        expected = ["PYTHON", "DJANGO", "POSTGRESQL", "REDIS", "DOCKER"]
        assert normalized == expected

    def test_stage1_output_is_stage2_input(self):
        """Verify Stage 1 raw_skills format matches Stage 2 expectations."""
        raw_skills = [
            "JavaScript",
            "react.js",
            "node.js",
            "PostgreSQL",
            "Git",
        ]
        normalized = normalize_skills(raw_skills)
        assert len(normalized) == len(raw_skills)
        assert all(
            isinstance(skill, str) and skill == skill.upper() for skill in normalized
        )