#"""Stage 2C — Test suite for candidate ranking and tiering."""

import pytest
from resumelens.profiles import Profile, classify_candidate
from resumelens.sorting import (
    Candidate,
    CandidateRanker,
    rank_candidates,
    get_tier_summary,
)


class TestCandidateDataclass:
    """Test Candidate dataclass."""

    def test_candidate_initialization(self):
        profile = Profile(
            name="Test",
            score=0.75,
            matched_skills=["SKILL1"],
            missing_skills=["SKILL2"],
            category_scores={"cat": 1},
        )
        candidate = Candidate(
            name="Alice",
            best_profile=profile,
            all_profiles=[profile],
        )

        assert candidate.name == "Alice"
        assert candidate.best_profile.score == 0.75
        assert candidate.tier == ""
        assert candidate.rank_position == 0

    def test_candidate_with_tier_assignment(self):
        profile = Profile(
            name="Full Stack Developer",
            score=0.85,
            matched_skills=["JAVASCRIPT", "REACT"],
            missing_skills=[],
            category_scores={"programming_language": 1},
        )
        candidate = Candidate(
            name="Bob",
            best_profile=profile,
            all_profiles=[profile],
            tier="TIER_1_STRONG_CANDIDATE",
            rank_position=1,
        )

        assert candidate.tier == "TIER_1_STRONG_CANDIDATE"
        assert candidate.rank_position == 1


class TestCandidateRankerInitialization:
    """Test CandidateRanker initialization."""

    def test_default_tier_thresholds(self):
        ranker = CandidateRanker()

        assert ranker.tier_thresholds["TIER_1_STRONG_CANDIDATE"] == 0.85
        assert ranker.tier_thresholds["TIER_2_MODERATE_CANDIDATE"] == 0.70
        assert ranker.tier_thresholds["TIER_3_WEAK_CANDIDATE"] == 0.55
        assert ranker.tier_thresholds["REJECTED"] == 0.0

    def test_custom_tier_thresholds(self):
        custom = {
            "TIER_1_STRONG_CANDIDATE": 0.90,
            "TIER_2_MODERATE_CANDIDATE": 0.75,
            "TIER_3_WEAK_CANDIDATE": 0.60,
            "REJECTED": 0.0,
        }
        ranker = CandidateRanker(tier_thresholds=custom)

        assert ranker.tier_thresholds["TIER_1_STRONG_CANDIDATE"] == 0.90
        assert ranker.tier_thresholds["TIER_2_MODERATE_CANDIDATE"] == 0.75


class TestTierAssignment:
    """Test _assign_tier() method."""

    def test_tier1_strong_candidate(self):
        ranker = CandidateRanker()

        assert ranker._assign_tier(0.95) == "TIER_1_STRONG_CANDIDATE"
        assert ranker._assign_tier(0.85) == "TIER_1_STRONG_CANDIDATE"
        assert ranker._assign_tier(0.90) == "TIER_1_STRONG_CANDIDATE"

    def test_tier2_moderate_candidate(self):
        ranker = CandidateRanker()

        assert ranker._assign_tier(0.84) == "TIER_2_MODERATE_CANDIDATE"
        assert ranker._assign_tier(0.70) == "TIER_2_MODERATE_CANDIDATE"
        assert ranker._assign_tier(0.75) == "TIER_2_MODERATE_CANDIDATE"

    def test_tier3_weak_candidate(self):
        ranker = CandidateRanker()

        assert ranker._assign_tier(0.69) == "TIER_3_WEAK_CANDIDATE"
        assert ranker._assign_tier(0.55) == "TIER_3_WEAK_CANDIDATE"
        assert ranker._assign_tier(0.60) == "TIER_3_WEAK_CANDIDATE"

    def test_rejected(self):
        ranker = CandidateRanker()

        assert ranker._assign_tier(0.54) == "REJECTED"
        assert ranker._assign_tier(0.20) == "REJECTED"
        assert ranker._assign_tier(0.0) == "REJECTED"


class TestCandidateRanking:
    """Test rank_candidates() method."""

    def test_single_candidate(self):
        profile = Profile(
            name="Full Stack Developer",
            score=0.75,
            matched_skills=["JAVASCRIPT"],
            missing_skills=[],
            category_scores={},
        )
        candidate = Candidate(
            name="Alice",
            best_profile=profile,
            all_profiles=[profile],
        )
        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([candidate])

        assert len(ranked) == 1
        assert ranked[0].name == "Alice"
        assert ranked[0].tier == "TIER_2_MODERATE_CANDIDATE"
        assert ranked[0].rank_position == 1

    def test_multiple_candidates_sorted_by_score(self):
        profile1 = Profile(
            name="Full Stack Developer",
            score=0.90,
            matched_skills=[],
            missing_skills=[],
            category_scores={},
        )
        profile2 = Profile(
            name="ML Engineer",
            score=0.72,
            matched_skills=[],
            missing_skills=[],
            category_scores={},
        )
        profile3 = Profile(
            name="Software",
            score=0.60,
            matched_skills=[],
            missing_skills=[],
            category_scores={},
        )

        cand1 = Candidate(name="Alice", best_profile=profile1, all_profiles=[])
        cand2 = Candidate(name="Bob", best_profile=profile2, all_profiles=[])
        cand3 = Candidate(name="Charlie", best_profile=profile3, all_profiles=[])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([cand2, cand3, cand1])

        assert ranked[0].name == "Alice"
        assert ranked[1].name == "Bob"
        assert ranked[2].name == "Charlie"

    def test_rank_positions_assigned(self):
        profiles = [
            Profile("Profile1", 0.85, [], [], {}),
            Profile("Profile2", 0.75, [], [], {}),
            Profile("Profile3", 0.65, [], [], {}),
        ]
        candidates = [
            Candidate(f"Cand{i}", profiles[i], []) for i in range(3)
        ]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates)

        assert ranked[0].rank_position == 1
        assert ranked[1].rank_position == 2
        assert ranked[2].rank_position == 3

    def test_minimum_threshold_filtering(self):
        profile1 = Profile("P1", 0.80, [], [], {})
        profile2 = Profile("P2", 0.50, [], [], {})
        profile3 = Profile("P3", 0.40, [], [], {})

        cand1 = Candidate("Alice", profile1, [])
        cand2 = Candidate("Bob", profile2, [])
        cand3 = Candidate("Charlie", profile3, [])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([cand1, cand2, cand3], min_threshold=0.55)

        assert len(ranked) == 1
        assert ranked[0].name == "Alice"

    def test_all_rejected_below_threshold(self):
        profile1 = Profile("P1", 0.50, [], [], {})
        profile2 = Profile("P2", 0.30, [], [], {})

        cand1 = Candidate("Alice", profile1, [])
        cand2 = Candidate("Bob", profile2, [])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([cand1, cand2], min_threshold=0.55)

        assert len(ranked) == 0


class TestGetCandidatesByTier:
    """Test get_candidates_by_tier() method."""

    def test_get_tier1_candidates(self):
        profiles = [
            Profile("P1", 0.90, [], [], {}),
            Profile("P2", 0.88, [], [], {}),
            Profile("P3", 0.70, [], [], {}),
        ]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(3)]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates)

        tier1 = ranker.get_candidates_by_tier(ranked, "TIER_1_STRONG_CANDIDATE")
        assert len(tier1) == 2
        assert all(c.tier == "TIER_1_STRONG_CANDIDATE" for c in tier1)

    def test_get_tier2_candidates(self):
        profiles = [
            Profile("P1", 0.75, [], [], {}),
            Profile("P2", 0.72, [], [], {}),
            Profile("P3", 0.60, [], [], {}),
        ]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(3)]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates)

        tier2 = ranker.get_candidates_by_tier(ranked, "TIER_2_MODERATE_CANDIDATE")
        assert len(tier2) == 2
        assert all(c.tier == "TIER_2_MODERATE_CANDIDATE" for c in tier2)

    def test_get_empty_tier(self):
        profile = Profile("P1", 0.90, [], [], {})
        candidate = Candidate("Alice", profile, [])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([candidate])

        tier3 = ranker.get_candidates_by_tier(ranked, "TIER_3_WEAK_CANDIDATE")
        assert len(tier3) == 0


class TestTierSummary:
    """Test get_tier_summary() method."""

    def test_summary_with_mixed_tiers(self):
        profiles = [
            Profile("P1", 0.90, [], [], {}),  # TIER_1
            Profile("P2", 0.87, [], [], {}),  # TIER_1
            Profile("P3", 0.75, [], [], {}),  # TIER_2
            Profile("P4", 0.60, [], [], {}),  # TIER_3
            Profile("P5", 0.40, [], [], {}),  # REJECTED
        ]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(5)]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates, min_threshold=0.0)

        summary = ranker.get_tier_summary(ranked)

        assert summary["TIER_1_STRONG_CANDIDATE"] == 2
        assert summary["TIER_2_MODERATE_CANDIDATE"] == 1
        assert summary["TIER_3_WEAK_CANDIDATE"] == 1
        assert summary["REJECTED"] == 1

    def test_summary_all_tier1(self):
        profiles = [Profile(f"P{i}", 0.90 + i * 0.01, [], [], {}) for i in range(3)]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(3)]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates)

        summary = ranker.get_tier_summary(ranked)

        assert summary["TIER_1_STRONG_CANDIDATE"] == 3
        assert summary["TIER_2_MODERATE_CANDIDATE"] == 0
        assert summary["TIER_3_WEAK_CANDIDATE"] == 0
        assert summary["REJECTED"] == 0

    def test_summary_all_rejected(self):
        profiles = [Profile(f"P{i}", 0.40, [], [], {}) for i in range(2)]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(2)]

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates(candidates, min_threshold=0.0)

        summary = ranker.get_tier_summary(ranked)

        assert summary["TIER_1_STRONG_CANDIDATE"] == 0
        assert summary["TIER_2_MODERATE_CANDIDATE"] == 0
        assert summary["TIER_3_WEAK_CANDIDATE"] == 0
        assert summary["REJECTED"] == 2


class TestPublicAPI:
    """Test rank_candidates() public API."""

    def test_public_rank_candidates_returns_ranked_list(self):
        profile1 = Profile("P1", 0.80, [], [], {})
        profile2 = Profile("P2", 0.70, [], [], {})

        cand1 = Candidate("Alice", profile1, [])
        cand2 = Candidate("Bob", profile2, [])

        ranked = rank_candidates([cand1, cand2])

        assert len(ranked) == 2
        assert ranked[0].rank_position == 1
        assert ranked[1].rank_position == 2

    def test_public_get_tier_summary(self):
        profile1 = Profile("P1", 0.90, [], [], {})
        profile2 = Profile("P2", 0.50, [], [], {})

        cand1 = Candidate("Alice", profile1, [])
        cand2 = Candidate("Bob", profile2, [])

        ranked = rank_candidates([cand1, cand2], min_threshold=0.0)
        summary = get_tier_summary(ranked)

        assert summary["TIER_1_STRONG_CANDIDATE"] == 1
        assert summary["REJECTED"] == 1


class TestIntegrationWithStage2B:
    """Test integration with Stage 2B classification output."""

    def test_rank_full_stack_developer(self):
        fs_skills = ["JAVASCRIPT", "REACT", "NODE_JS", "EXPRESS", "POSTGRESQL"]
        best, all_profiles = classify_candidate(fs_skills)

        candidate = Candidate(name="Alice", best_profile=best, all_profiles=all_profiles)
        ranked = rank_candidates([candidate])

        assert len(ranked) == 1
        assert ranked[0].best_profile.name in ["Full Stack Developer", "Software profile"]
        assert ranked[0].tier in ["TIER_1_STRONG_CANDIDATE", "TIER_2_MODERATE_CANDIDATE"]

    def test_rank_ml_engineer(self):
        ml_skills = ["PYTHON", "TENSORFLOW", "PYTORCH", "PANDAS", "NUMPY"]
        best, all_profiles = classify_candidate(ml_skills)

        candidate = Candidate(name="Bob", best_profile=best, all_profiles=all_profiles)
        ranked = rank_candidates([candidate])

        assert len(ranked) == 1
        assert ranked[0].best_profile.name == "Machine Learning Engineer"
        assert ranked[0].tier in ["TIER_1_STRONG_CANDIDATE", "TIER_2_MODERATE_CANDIDATE"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_candidate_list(self):
        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([])

        assert len(ranked) == 0

    def test_single_candidate_boundary_scores(self):
        # Exactly at boundary
        profile_boundary_85 = Profile("P", 0.85, [], [], {})
        candidate = Candidate("Alice", profile_boundary_85, [])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([candidate])

        assert ranked[0].tier == "TIER_1_STRONG_CANDIDATE"

    def test_candidates_with_identical_scores(self):
        profile1 = Profile("P1", 0.75, [], [], {})
        profile2 = Profile("P2", 0.75, [], [], {})
        profile3 = Profile("P3", 0.75, [], [], {})

        cand1 = Candidate("Alice", profile1, [])
        cand2 = Candidate("Bob", profile2, [])
        cand3 = Candidate("Charlie", profile3, [])

        ranker = CandidateRanker()
        ranked = ranker.rank_candidates([cand1, cand2, cand3])

        # All should be ranked, order stable from input
        assert len(ranked) == 3
        assert all(c.tier == "TIER_2_MODERATE_CANDIDATE" for c in ranked)

    def test_many_candidates(self):
        profiles = [Profile(f"P{i}", 0.55 + (i * 0.01), [], [], {}) for i in range(100)]
        candidates = [Candidate(f"Cand{i}", profiles[i], []) for i in range(100)]

        ranked = rank_candidates(candidates)

        assert len(ranked) == 100
        # Check sorted descending
        for i in range(len(ranked) - 1):
            assert ranked[i].best_profile.score >= ranked[i + 1].best_profile.score


class TestTierDefinitions:
    """Test tier definitions and boundaries."""

    def test_all_tier_names_present_in_summary(self):
        profile = Profile("P", 0.75, [], [], {})
        candidate = Candidate("Alice", profile, [])

        ranked = rank_candidates([candidate])
        summary = get_tier_summary(ranked)

        assert "TIER_1_STRONG_CANDIDATE" in summary
        assert "TIER_2_MODERATE_CANDIDATE" in summary
        assert "TIER_3_WEAK_CANDIDATE" in summary
        assert "REJECTED" in summary

    def test_tier_score_consistency(self):
        """Verify tier assignment matches score ranges."""
        ranker = CandidateRanker()

        test_cases = [
            (0.95, "TIER_1_STRONG_CANDIDATE"),
            (0.85, "TIER_1_STRONG_CANDIDATE"),
            (0.80, "TIER_2_MODERATE_CANDIDATE"),
            (0.70, "TIER_2_MODERATE_CANDIDATE"),
            (0.65, "TIER_3_WEAK_CANDIDATE"),
            (0.55, "TIER_3_WEAK_CANDIDATE"),
            (0.50, "REJECTED"),
            (0.00, "REJECTED"),
        ]

        for score, expected_tier in test_cases:
            tier = ranker._assign_tier(score)
            assert tier == expected_tier, f"Score {score} should be {expected_tier}, got {tier}"