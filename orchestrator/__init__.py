"""Repository-level automation for the Supply Chain Dependency Risk Scorer.

This package discovers dependency manifests and delegates all dependency analysis
to the existing :mod:`scds` package.  It intentionally does not contain a
second implementation of the security checks.
"""

from orchestrator.policy import Policy, PolicyDecision
from orchestrator.service import RepositoryScanResult, RepositoryScanner

__all__ = ["Policy", "PolicyDecision", "RepositoryScanResult", "RepositoryScanner"]
