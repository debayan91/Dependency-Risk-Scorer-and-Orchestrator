"""
Typosquatting and Dependency Confusion Analyzer.
Uses Levenshtein distance and Jaro-Winkler similarity to detect brand-jacking and typosquatting attacks.
"""

from dataclasses import dataclass
from typing import Optional

from scds.algorithms.distance import levenshtein_distance, jaro_winkler_similarity
from scds.config import POPULAR_PACKAGES


@dataclass
class TyposquattingResult:
    risk_score: float  # 0.0 to 10.0
    is_typosquat: bool
    target_package: Optional[str] = None
    levenshtein: int = 0
    similarity: float = 0.0
    explanation: str = "No typosquatting detected."


class TyposquattingAnalyzer:
    """
    Evaluates packages against curated catalogs of high-reputation packages
    to detect confusion and typosquatting attacks.
    """

    def __init__(self):
        self.popular = POPULAR_PACKAGES

    def analyze(self, package_name: str, ecosystem: str = "PyPI") -> TyposquattingResult:
        pkg = package_name.lower().strip()
        catalog = self.popular.get(ecosystem, self.popular["PyPI"])

        # Exact match with legitimate popular package -> Safe
        if pkg in catalog:
            return TyposquattingResult(
                risk_score=0.0,
                is_typosquat=False,
                target_package=pkg,
                similarity=1.0,
                explanation=f"Matches recognized popular package '{pkg}'."
            )

        # Check for normalization confusion (e.g. hyphen vs underscore)
        normalized_pkg = pkg.replace("-", "_")

        best_target = None
        best_score = 0.0
        min_lev = 999

        for popular_pkg in catalog:
            pop_lower = popular_pkg.lower()
            normalized_pop = pop_lower.replace("-", "_")

            # Check direct hyphen/underscore confusion
            if normalized_pkg == normalized_pop and pkg != pop_lower:
                return TyposquattingResult(
                    risk_score=9.5,
                    is_typosquat=True,
                    target_package=popular_pkg,
                    levenshtein=1,
                    similarity=0.98,
                    explanation=(
                        f"Potential dependency confusion! Separator variation targeting "
                        f"legitimate package '{popular_pkg}' ('{pkg}' vs '{pop_lower}')."
                    )
                )

            # String distance metrics
            lev = levenshtein_distance(pkg, pop_lower)
            jw = jaro_winkler_similarity(pkg, pop_lower)

            if jw > best_score:
                best_score = jw
                best_target = popular_pkg
                min_lev = lev

        # Evaluation criteria based on empirical thresholds (TypoSmart & SCDS survey)
        if best_target:
            # Critical typosquat: 1 edit distance or extremely high similarity
            if min_lev == 1 and best_score >= 0.88:
                risk = 9.5
                return TyposquattingResult(
                    risk_score=risk,
                    is_typosquat=True,
                    target_package=best_target,
                    levenshtein=min_lev,
                    similarity=round(best_score, 3),
                    explanation=(
                        f"HIGH-CONFIDENCE TYPOSQUATTING: '{pkg}' differs by only 1 character edit "
                        f"from popular package '{best_target}' (similarity: {best_score:.1%})."
                    )
                )
            elif min_lev == 2 and best_score >= 0.85:
                risk = 7.5
                return TyposquattingResult(
                    risk_score=risk,
                    is_typosquat=True,
                    target_package=best_target,
                    levenshtein=min_lev,
                    similarity=round(best_score, 3),
                    explanation=(
                        f"Moderate typosquatting risk: '{pkg}' closely mimics popular package "
                        f"'{best_target}' (Levenshtein: 2, similarity: {best_score:.1%})."
                    )
                )
            elif best_score >= 0.90:
                risk = 6.0
                return TyposquattingResult(
                    risk_score=risk,
                    is_typosquat=True,
                    target_package=best_target,
                    levenshtein=min_lev,
                    similarity=round(best_score, 3),
                    explanation=(
                        f"Potential lexical similarity detected with '{best_target}' "
                        f"(similarity: {best_score:.1%})."
                    )
                )

        return TyposquattingResult(
            risk_score=0.0,
            is_typosquat=False,
            target_package=None,
            levenshtein=min_lev if best_target else 0,
            similarity=round(best_score, 3) if best_target else 0.0,
            explanation="No typosquatting signatures detected."
        )
