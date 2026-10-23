"""Policy decisions for automated repository scans."""

from dataclasses import dataclass
from typing import Iterable, Optional


LEVEL_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


@dataclass(frozen=True)
class Policy:
    """Define when automation should warn or block a repository change.

    ``block_on`` defaults to ``CRITICAL`` so a new installation can report
    findings safely before adopting a stricter merge policy.
    """

    warn_on: str = "MEDIUM"
    block_on: Optional[str] = "CRITICAL"

    def __post_init__(self) -> None:
        for name, level in (("warn_on", self.warn_on), ("block_on", self.block_on)):
            if level is not None and level.upper() not in LEVEL_ORDER:
                raise ValueError(f"{name} must be one of: {', '.join(LEVEL_ORDER)}")


@dataclass(frozen=True)
class PolicyDecision:
    status: str  # PASS, WARN, or BLOCK
    highest_level: str
    message: str


def evaluate_policy(levels: Iterable[str], policy: Policy) -> PolicyDecision:
    """Evaluate aggregate risk levels against a repository policy."""
    normalized = [level.upper() for level in levels if level.upper() in LEVEL_ORDER]
    highest = max(normalized, key=LEVEL_ORDER.get) if normalized else "SAFE"
    highest_rank = LEVEL_ORDER[highest]

    if policy.block_on and highest_rank >= LEVEL_ORDER[policy.block_on.upper()]:
        return PolicyDecision("BLOCK", highest, f"Blocked: highest dependency risk is {highest}.")
    if highest_rank >= LEVEL_ORDER[policy.warn_on.upper()]:
        return PolicyDecision("WARN", highest, f"Warning: highest dependency risk is {highest}.")
    return PolicyDecision("PASS", highest, "Passed: no dependency risk meets the warning threshold.")
