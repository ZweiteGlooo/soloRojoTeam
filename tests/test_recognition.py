"""Tests for the recognition stage."""
import pytest
from pyformlang.finite_automaton import Symbol

from resumelens.extraction import extract_file
from resumelens.normalization import normalize_skills_safe
from resumelens.patterns import PATTERNS, get_pattern
from resumelens.recognition import (
    ACCEPTED, REJECTED, START, accepted_profiles, accepting_states, build_dfa,
    build_enfa, formal_definition, recognize, recognize_all, transition_table)

FULL_STACK = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
ML = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]


def words(*skills):
    return [Symbol(s) for s in skills]


class TestConstruction:
    @pytest.mark.parametrize("key", PATTERNS)
    def test_dfa_is_deterministic(self, key):
        assert build_dfa(PATTERNS[key]).is_deterministic()

    @pytest.mark.parametrize("key", PATTERNS)
    def test_enfa_is_not_deterministic(self, key):
        assert not build_enfa(PATTERNS[key]).is_deterministic()

    @pytest.mark.parametrize("key", PATTERNS)
    def test_dfa_and_enfa_recognize_same_language(self, key):
        pattern = PATTERNS[key]
        assert build_dfa(pattern).is_equivalent_to(build_enfa(pattern))

    @pytest.mark.parametrize("key", PATTERNS)
    def test_formal_definition_is_a_5_tuple(self, key):
        m = formal_definition(key)
        assert set(m) == {"Q", "Σ", "δ", "q0", "F"}
        assert m["q0"] == START and START in m["Q"]
        assert set(m["F"]) <= set(m["Q"])
        for (src, skill), dst in m["δ"].items():
            assert src in m["Q"] and dst in m["Q"] and skill in m["Σ"]

    def test_full_stack_states(self):
        assert formal_definition("FULL_STACK_DEVELOPER")["Q"] == \
            ["q0", "LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "API", "VCS"]

    def test_only_vcs_is_final_when_it_is_last_and_required(self):
        for pattern in PATTERNS.values():
            assert accepting_states(pattern) == ["VCS"]

    def test_optional_block_can_be_skipped(self):
        delta = transition_table(get_pattern("FULL_STACK_DEVELOPER"))
        assert delta[("DATABASE", "REST")] == "API"
        assert delta[("DATABASE", "GIT")] == "VCS"

    def test_required_block_cannot_be_skipped(self):
        delta = transition_table(get_pattern("FULL_STACK_DEVELOPER"))
        assert ("LANGUAGE", "NODE_JS") not in delta
        assert ("q0", "REACT") not in delta

    def test_blocks_loop_on_themselves(self):
        delta = transition_table(get_pattern("FULL_STACK_DEVELOPER"))
        assert delta[("LANGUAGE", "TYPESCRIPT")] == "LANGUAGE"


class TestFullStackAutomaton:
    dfa = build_dfa(get_pattern("FULL_STACK_DEVELOPER"))

    def test_minimal_word(self):
        assert self.dfa.accepts(words(*FULL_STACK))

    def test_with_optional_api_and_repeated_blocks(self):
        assert self.dfa.accepts(words("JAVASCRIPT", "TYPESCRIPT", "ANGULAR", "NODE_JS",
                                      "MYSQL", "MONGODB", "REST", "GIT", "GITHUB"))

    def test_missing_frontend(self):
        assert not self.dfa.accepts(words("JAVASCRIPT", "NODE_JS", "POSTGRESQL", "GIT"))

    def test_wrong_order(self):
        assert not self.dfa.accepts(words("REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "GIT"))

    def test_empty_word(self):
        assert not self.dfa.accepts([])


class TestRecognize:
    def test_statement_example_ml(self):
        r = recognize(ML, "MACHINE_LEARNING_ENGINEER")
        assert r.result == ACCEPTED
        assert r.trace == ["q0", "LANGUAGE", "DATA_LIBRARY", "ML_LIBRARY", "DATABASE", "VCS"]

    def test_input_order_does_not_matter(self):
        assert recognize(list(reversed(FULL_STACK)), "Full Stack Developer").accepted

    def test_rejected_reports_missing_blocks(self):
        r = recognize(["JAVASCRIPT", "NODE_JS", "GIT"], "FULL_STACK_DEVELOPER")
        assert r.result == REJECTED
        assert r.missing_blocks == ["FRONTEND", "DATABASE"]
        assert r.trace[-1] == "TRAP"

    def test_ml_needs_python(self):
        r = recognize(["PANDAS", "TENSORFLOW", "SQL", "GIT"], "MACHINE_LEARNING_ENGINEER")
        assert not r.accepted and r.missing_blocks == ["LANGUAGE"]

    def test_backend(self):
        assert recognize(["JAVA", "SPRING_BOOT", "REST", "POSTGRESQL", "DOCKER", "GIT"],
                         "BACKEND_DEVELOPER").accepted

    def test_backend_requires_api(self):
        assert not recognize(["JAVA", "SPRING_BOOT", "POSTGRESQL", "GIT"], "BACKEND_DEVELOPER").accepted

    def test_data_engineer(self):
        assert recognize(["PYTHON", "SPARK", "AIRFLOW", "ETL", "POSTGRESQL", "AWS", "GIT"],
                         "DATA_ENGINEER").accepted

    def test_data_engineer_requires_processing_tool(self):
        assert not recognize(["PYTHON", "ETL", "POSTGRESQL", "GIT"], "DATA_ENGINEER").accepted

    def test_recognize_all_returns_four_results_in_fixed_order(self):
        results = recognize_all(FULL_STACK)
        assert [r.profile for r in results] == list(PATTERNS)

    def test_a_candidate_can_match_several_profiles(self):
        skills = FULL_STACK + ["REST"]
        assert accepted_profiles(skills) == ["Full Stack Developer", "Backend Developer"]

    def test_no_profile(self):
        assert accepted_profiles(["EXCEL"]) == []


class TestSampleResumes:
    """Stage 1 -> Stage 2 -> Stage 3 on the résumés in data/resumes."""

    @staticmethod
    def profiles_of(name):
        raw = extract_file(f"data/resumes/{name}.txt")["raw_skills"]
        normalized, _ = normalize_skills_safe(raw)
        return accepted_profiles(normalized)

    def test_wednesday_addams(self):
        assert self.profiles_of("wednesday_addams") == ["Full Stack Developer"]

    def test_mary_jane_watson(self):
        assert self.profiles_of("mary_jane_watson") == ["Machine Learning Engineer"]

    def test_peter_parker(self):
        # no Python, so the ML libraries he lists are not enough for ML Engineer
        assert self.profiles_of("peter_parker") == ["Full Stack Developer", "Backend Developer"]

