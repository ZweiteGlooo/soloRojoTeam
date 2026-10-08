"""Stage 2B — Test suite for candidate profile classification."""

import pytest
from resumelens.profiles import (
    Profile,
    ProfileClassifier,
    classify_candidate,
)


class TestProfileDefinition:
    """Test profile structure and initialization."""

    def test_classifier_initializes_all_four_profiles(self):
        classifier = ProfileClassifier()
        assert len(classifier.profiles) == 4
        assert "Full Stack Developer" in classifier.profiles
        assert "Machine Learning Engineer" in classifier.profiles
        assert "Software profile" in classifier.profiles
        assert "AI/Data profile" in classifier.profiles

    def test_profile_has_required_fields(self):
        profile = Profile(
            name="Test",
            score=0.85,
            matched_skills=["SKILL1"],
            missing_skills=["SKILL2"],
            category_scores={"cat1": 2},
        )
        assert profile.name == "Test"
        assert profile.score == 0.85
        assert len(profile.matched_skills) > 0


class TestSkillCategorization:
    """Test _categorize_skill() method."""

    def test_programming_languages(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("PYTHON") == "programming_language"
        assert classifier._categorize_skill("JAVASCRIPT") == "programming_language"
        assert classifier._categorize_skill("JAVA") == "programming_language"

    def test_frontend_frameworks(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("REACT") == "frontend_framework"
        assert classifier._categorize_skill("ANGULAR") == "frontend_framework"
        assert classifier._categorize_skill("VUE") == "frontend_framework"

    def test_backend_frameworks(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("DJANGO") == "backend_framework"
        assert classifier._categorize_skill("EXPRESS") == "backend_framework"
        assert classifier._categorize_skill("NODE_JS") == "backend_framework"

    def test_databases(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("POSTGRESQL") == "database"
        assert classifier._categorize_skill("MONGODB") == "database"
        assert classifier._categorize_skill("MYSQL") == "database"
        assert classifier._categorize_skill("REDIS") == "database"

    def test_ml_frameworks(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("TENSORFLOW") == "ml_framework"
        assert classifier._categorize_skill("PYTORCH") == "ml_framework"

    def test_data_science_libraries(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("PANDAS") == "data_science_library"
        assert classifier._categorize_skill("NUMPY") == "data_science_library"
        assert classifier._categorize_skill("SCIKIT_LEARN") == "data_science_library"

    def test_tool_technology(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("GIT") == "tool_technology"
        assert classifier._categorize_skill("DOCKER") == "tool_technology"
        assert classifier._categorize_skill("KUBERNETES") == "tool_technology"

    def test_unknown_skill_defaults_to_tool_technology(self):
        classifier = ProfileClassifier()
        assert classifier._categorize_skill("UNKNOWN_SKILL") == "tool_technology"


class TestCategoryMatching:
    """Test _count_category_matches() method."""

    def test_full_stack_skills_categorized(self):
        classifier = ProfileClassifier()
        fs_skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
        counts, matched, missing = classifier._count_category_matches(
            fs_skills, "Full Stack Developer"
        )

        assert counts["programming_language"] >= 1
        assert counts["frontend_framework"] >= 1
        assert counts["backend_framework"] >= 1
        assert counts["database"] >= 1

    def test_empty_skills_list(self):
        classifier = ProfileClassifier()
        counts, matched, missing = classifier._count_category_matches(
            [], "Full Stack Developer"
        )
        assert matched == []

    def test_ml_engineer_skills_categorized(self):
        classifier = ProfileClassifier()
        ml_skills = [
            "PYTHON",
            "TENSORFLOW",
            "PYTORCH",
            "PANDAS",
            "NUMPY",
        ]
        counts, matched, missing = classifier._count_category_matches(
            ml_skills, "Machine Learning Engineer"
        )

        assert counts["programming_language"] >= 1
        assert counts["ml_framework"] >= 2
        assert counts["data_science_library"] >= 2


class TestScoreCalculation:
    """Test _calculate_score() method."""

    def test_perfect_match_scores_high(self):
        classifier = ProfileClassifier()
        fs_skills = [
            "JAVASCRIPT",
            "REACT",
            "NODE_JS",
            "EXPRESS",
            "POSTGRESQL",
            "MONGODB",
        ]
        category_counts = {
            "programming_language": 1,
            "frontend_framework": 1,
            "backend_framework": 2,
            "database": 2,
        }
        score = classifier._calculate_score(fs_skills, category_counts, "Full Stack Developer")
        assert score >= 0.70

    def test_partial_match_scores_lower(self):
        classifier = ProfileClassifier()
        partial_skills = ["JAVASCRIPT", "PYTHON"]
        category_counts = {
            "programming_language": 2,
            "frontend_framework": 0,
            "backend_framework": 0,
            "database": 0,
        }
        score = classifier._calculate_score(
            partial_skills, category_counts, "Full Stack Developer"
        )
        assert score < 0.4

    def test_no_match_scores_zero(self):
        classifier = ProfileClassifier()
        category_counts = {
            "programming_language": 0,
            "frontend_framework": 0,
            "backend_framework": 0,
            "database": 0,
        }
        score = classifier._calculate_score(
            [], category_counts, "Full Stack Developer"
        )
        assert score == 0.0

    def test_score_between_zero_and_one(self):
        classifier = ProfileClassifier()
        for profile_name in classifier.profiles.keys():
            category_counts = {cat: 0 for cat in classifier.profiles[profile_name]["requirements"]}
            score = classifier._calculate_score(
                ["PYTHON"], category_counts, profile_name
            )
            assert 0.0 <= score <= 1.0


class TestProfileClassification:
    """Test classify() method for profiles."""

    def test_classification_returns_best_profile(self):
        classifier = ProfileClassifier()
        skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
        best, all_profiles = classifier.classify(skills)

        assert best is not None
        assert best.score > 0.0
        assert len(all_profiles) == 4

    def test_ml_engineer_scores_high_for_ml_skills(self):
        classifier = ProfileClassifier()
        ml_skills = ["PYTHON", "TENSORFLOW", "PYTORCH", "PANDAS", "NUMPY", "SCIKIT_LEARN"]
        best, all_profiles = classifier.classify(ml_skills)

        assert best.name == "Machine Learning Engineer"
        assert best.score > 0.70

    def test_all_profiles_ranked_by_score(self):
        classifier = ProfileClassifier()
        skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
        best, all_profiles = classifier.classify(skills)

        scores = [p.score for p in all_profiles]
        assert scores == sorted(scores, reverse=True)

    def test_profile_includes_matched_and_missing_skills(self):
        classifier = ProfileClassifier()
        skills = ["JAVASCRIPT", "REACT"]
        best, all_profiles = classifier.classify(skills)

        assert len(best.matched_skills) >= 0
        assert len(best.missing_skills) >= 0


class TestPublicAPI:
    """Test classify_candidate() public API."""

    def test_classify_candidate_with_full_stack_skills(self):
        fs_skills = ["JAVASCRIPT", "REACT", "NODE_JS", "EXPRESS", "POSTGRESQL", "GIT"]
        best, all_profiles = classify_candidate(fs_skills)

        assert best is not None
        assert best.score > 0.60
        assert len(all_profiles) == 4

    def test_classify_candidate_ml_specialist(self):
        ml_skills = ["PYTHON", "TENSORFLOW", "PYTORCH", "PANDAS", "NUMPY", "JUPYTER"]
        best, all_profiles = classify_candidate(ml_skills)

        assert best.name == "Machine Learning Engineer"
        assert best.score > 0.70

    def test_classify_candidate_software_specialist(self):
        software_skills = ["PYTHON", "DJANGO", "FASTAPI", "POSTGRESQL", "REDIS", "DOCKER"]
        best, all_profiles = classify_candidate(software_skills)

        assert best.name in ["Software profile", "Full Stack Developer"]
        assert best.score > 0.60

    def test_classify_candidate_data_specialist(self):
        data_skills = ["PYTHON", "SPARK", "KAFKA", "POSTGRESQL", "MONGODB", "TENSORFLOW"]
        best, all_profiles = classify_candidate(data_skills)

        assert best.name == "AI/Data profile"
        assert best.score > 0.60

    def test_classify_candidate_empty_skills(self):
        best, all_profiles = classify_candidate([])

        assert best.score == 0.0
        assert best.matched_skills == []

    def test_classify_candidate_returns_tuple(self):
        result = classify_candidate(["PYTHON"])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_classify_candidate_best_is_profile(self):
        best, all_profiles = classify_candidate(["JAVASCRIPT"])
        assert isinstance(best, Profile)

    def test_classify_candidate_all_profiles_list(self):
        best, all_profiles = classify_candidate(["PYTHON"])
        assert isinstance(all_profiles, list)
        assert len(all_profiles) == 4


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_skill_input(self):
        best, all_profiles = classify_candidate(["PYTHON"])
        assert best is not None
        assert len(all_profiles) == 4

    def test_many_duplicate_skills(self):
        skills = ["PYTHON", "PYTHON", "TENSORFLOW", "TENSORFLOW"]
        best, all_profiles = classify_candidate(skills)
        assert best is not None

    def test_mixed_skills(self):
        skills = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"]
        best, all_profiles = classify_candidate(skills)
        assert best is not None
        assert best.score > 0.5

    def test_very_long_skills_list(self):
        skills = (
            ["PYTHON", "JAVASCRIPT", "JAVA", "GO"]
            + ["REACT", "ANGULAR", "VUE"]
            + ["DJANGO", "FASTAPI", "EXPRESS"]
            + ["POSTGRESQL", "MONGODB", "MYSQL", "REDIS", "CASSANDRA"]
        )
        best, all_profiles = classify_candidate(skills)

        assert best is not None
        assert best.score > 0.70


class TestIntegrationWithStage2A:
    """Test integration with Stage 2A normalization output."""

    def test_accepts_normalized_skills_from_stage2a(self):
        normalized_from_stage2a = [
            "JAVASCRIPT",
            "REACT",
            "NODE_JS",
            "POSTGRESQL",
            "GIT",
        ]
        best, all_profiles = classify_candidate(normalized_from_stage2a)

        assert best is not None
        assert best.score > 0.60

    def test_handles_uppercase_only_input(self):
        uppercase_skills = ["PYTHON", "TENSORFLOW", "PANDAS"]
        best, all_profiles = classify_candidate(uppercase_skills)

        assert all(skill.isupper() for skill in best.matched_skills)

    def test_full_pipeline_simulation(self):
        normalized_skills = [
            "JAVASCRIPT",
            "REACT",
            "NODE_JS",
            "POSTGRESQL",
            "GIT",
        ]

        best, all_profiles = classify_candidate(normalized_skills)

        assert best is not None
        assert best.score > 0.60


class TestScoreDistribution:
    """Test score behavior across different candidate types."""

    def test_ml_specialist_scores_highest_on_ml_profile(self):
        ml_skills = ["PYTHON", "TENSORFLOW", "PYTORCH", "PANDAS", "NUMPY"]
        best_ml, all_ml = classify_candidate(ml_skills)

        ml_profile_score = [p.score for p in all_ml if p.name == "Machine Learning Engineer"][0]
        assert ml_profile_score >= 0.65

    def test_specialist_has_higher_best_score_than_generalist(self):
        specialist_skills = ["PYTHON", "TENSORFLOW", "PYTORCH", "PANDAS", "NUMPY", "SCIKIT_LEARN"]
        specialist_best, _ = classify_candidate(specialist_skills)

        generalist_skills = ["PYTHON", "JAVASCRIPT", "SQL"]
        generalist_best, _ = classify_candidate(generalist_skills)

        assert specialist_best.score > generalist_best.score