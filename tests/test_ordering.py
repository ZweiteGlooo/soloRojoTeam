"""Tests for the profile patterns and the canonical ordering of qualifications."""
import pytest

from resumelens.normalization import normalize_skills_safe
from resumelens.patterns import PATTERNS, get_pattern
from resumelens.sorting import canonical_order, canonical_orders


class TestPatterns:
    def test_four_profiles(self):
        assert set(PATTERNS) == {
            "FULL_STACK_DEVELOPER", "MACHINE_LEARNING_ENGINEER", "BACKEND_DEVELOPER", "DATA_ENGINEER"}

    @pytest.mark.parametrize("key", PATTERNS)
    def test_blocks_are_disjoint(self, key):
        # a qualification in two blocks would make the automaton nondeterministic
        alphabet = PATTERNS[key].alphabet
        assert len(alphabet) == len(set(alphabet))

    @pytest.mark.parametrize("key", PATTERNS)
    def test_every_profile_requires_something(self, key):
        assert any(b.required for b in PATTERNS[key].blocks)

    def test_get_pattern_by_key_or_title(self):
        assert get_pattern("Full Stack Developer") is get_pattern("FULL_STACK_DEVELOPER")

    def test_unknown_profile(self):
        with pytest.raises(KeyError):
            get_pattern("Astronaut")

    def test_regex(self):
        assert get_pattern("FULL_STACK_DEVELOPER").regex() == \
            "LANGUAGE+ FRONTEND+ BACKEND+ DATABASE+ API* VCS+"


class TestCanonicalOrder:
    def test_example_from_statement(self):
        skills = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
        assert canonical_order(skills, "FULL_STACK_DEVELOPER") == \
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]

    def test_order_does_not_depend_on_input_order(self):
        a = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
        assert canonical_order(a, "MACHINE_LEARNING_ENGINEER") == \
            canonical_order(list(reversed(a)), "MACHINE_LEARNING_ENGINEER")

    def test_drops_skills_outside_profile(self):
        assert canonical_order(["PYTHON", "REACT", "GIT"], "FULL_STACK_DEVELOPER") == ["REACT", "GIT"]

    def test_removes_duplicates(self):
        assert canonical_order(["GIT", "GIT", "JAVASCRIPT"], "FULL_STACK_DEVELOPER") == ["JAVASCRIPT", "GIT"]

    def test_empty(self):
        assert canonical_order([], "DATA_ENGINEER") == []

    def test_same_skill_different_place_per_profile(self):
        # PYTHON is the language block in ML but does not exist in Full Stack
        assert canonical_order(["GIT", "PYTHON"], "MACHINE_LEARNING_ENGINEER") == ["PYTHON", "GIT"]
        assert canonical_order(["GIT", "PYTHON"], "FULL_STACK_DEVELOPER") == ["GIT"]

    def test_canonical_orders_covers_all_profiles(self):
        orders = canonical_orders(["JAVASCRIPT", "GIT"])
        assert set(orders) == set(PATTERNS)
        assert orders["DATA_ENGINEER"] == ["GIT"]


class TestWithStage2Output:
    def test_wednesday_addams(self):
        norm, unknown = normalize_skills_safe(["JS", "React.js", "NodeJS", "Postgres", "Git"])
        assert unknown == []
        assert canonical_order(norm, "Full Stack Developer") == \
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]

    def test_mary_jane_watson(self):
        norm, _ = normalize_skills_safe(["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"])
        assert canonical_order(norm, "Machine Learning Engineer") == \
            ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]

    def test_peter_parker_rest_and_nosql_now_normalized(self):
        norm, unknown = normalize_skills_safe(["RESTful APIs", "No SQL", "Spring Boot"])
        assert unknown == []
        assert canonical_order(norm, "BACKEND_DEVELOPER") == ["SPRING_BOOT", "REST", "NOSQL"]
