"""Stage 2C — Candidate ranking and tiering based on profile scores."""
from typing import List, Tuple, Dict, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from resumelens.profiles import Profile


@dataclass
class Candidate:
    """Represents a candidate with their classification."""

    name: str
    best_profile: "Profile"
    all_profiles: List["Profile"]
    tier: str = ""
    rank_position: int = 0


class CandidateRanker:
    """
    Ranker for candidate selection based on profile matching scores.
    
    Assigns candidates to tiers based on score thresholds:
    - TIER_1: score >= 0.85 (STRONG_CANDIDATE)
    - TIER_2: score >= 0.70 (MODERATE_CANDIDATE)
    - TIER_3: score >= 0.55 (WEAK_CANDIDATE)
    - REJECTED: score < 0.55
    """

    def __init__(self, tier_thresholds: Dict[str, float] = None):
        """
        Initialize ranker with tier thresholds.
        
        Args:
            tier_thresholds: Dict mapping tier names to score thresholds
                Default: {
                    "TIER_1_STRONG_CANDIDATE": 0.85,
                    "TIER_2_MODERATE_CANDIDATE": 0.70,
                    "TIER_3_WEAK_CANDIDATE": 0.55,
                    "REJECTED": 0.0
                }
        """
        self.tier_thresholds = tier_thresholds or {
            "TIER_1_STRONG_CANDIDATE": 0.85,
            "TIER_2_MODERATE_CANDIDATE": 0.70,
            "TIER_3_WEAK_CANDIDATE": 0.55,
            "REJECTED": 0.0,
        }

    def _assign_tier(self, score: float) -> str:
        """Assign tier based on score thresholds."""
        if score >= self.tier_thresholds["TIER_1_STRONG_CANDIDATE"]:
            return "TIER_1_STRONG_CANDIDATE"
        elif score >= self.tier_thresholds["TIER_2_MODERATE_CANDIDATE"]:
            return "TIER_2_MODERATE_CANDIDATE"
        elif score >= self.tier_thresholds["TIER_3_WEAK_CANDIDATE"]:
            return "TIER_3_WEAK_CANDIDATE"
        else:
            return "REJECTED"

    def rank_candidates(
        self, candidates: List[Candidate], min_threshold: float = 0.55
    ) -> List[Candidate]:
        """
        Rank candidates by score and assign tiers.
        
        Args:
            candidates: List of Candidate objects with best_profile set
            min_threshold: Minimum score to include in ranking (default 0.55)
            
        Returns:
            List of candidates sorted by score (descending), tiers assigned
        """
        # Assign tiers
        for candidate in candidates:
            candidate.tier = self._assign_tier(candidate.best_profile.score)

        # Filter by minimum threshold
        filtered = [c for c in candidates if c.best_profile.score >= min_threshold]

        # Sort by score (descending)
        sorted_candidates = sorted(
            filtered, key=lambda c: c.best_profile.score, reverse=True
        )

        # Assign rank positions
        for position, candidate in enumerate(sorted_candidates, start=1):
            candidate.rank_position = position

        return sorted_candidates

    def get_candidates_by_tier(
        self, candidates: List[Candidate], tier: str
    ) -> List[Candidate]:
        """
        Get all candidates in a specific tier.
        
        Args:
            candidates: List of ranked candidates
            tier: Tier name (e.g., "TIER_1_STRONG_CANDIDATE")
            
        Returns:
            Filtered list of candidates in that tier
        """
        return [c for c in candidates if c.tier == tier]

    def get_tier_summary(self, candidates: List[Candidate]) -> Dict[str, int]:
        """
        Get count of candidates per tier.
        
        Returns:
            Dict mapping tier names to candidate counts
        """
        summary = {
            "TIER_1_STRONG_CANDIDATE": 0,
            "TIER_2_MODERATE_CANDIDATE": 0,
            "TIER_3_WEAK_CANDIDATE": 0,
            "REJECTED": 0,
        }

        for candidate in candidates:
            summary[candidate.tier] += 1

        return summary


def rank_candidates(
    candidates: List[Candidate], min_threshold: float = 0.55
) -> List[Candidate]:
    """
    Rank candidates by profile score.
    
    Public API for Stage 2C ranking.
    
    Args:
        candidates: List of Candidate objects
        min_threshold: Minimum score to include
        
    Returns:
        Ranked candidates with tiers assigned
    """
    ranker = CandidateRanker()
    return ranker.rank_candidates(candidates, min_threshold)


def get_tier_summary(candidates: List[Candidate]) -> Dict[str, int]:
    """
    Get summary of candidates by tier.
    
    Args:
        candidates: List of Candidate objects
        
    Returns:
        Count per tier
    """
    ranker = CandidateRanker()
    return ranker.get_tier_summary(candidates)

