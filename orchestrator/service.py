"""Repository scan workflow that delegates analysis to the SCDS core."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from scds.engine import RiskEngine, ScanReport
from scds.parsers import parse_manifest

from orchestrator.discovery import changed_manifests, discover_manifests
from orchestrator.policy import Policy, PolicyDecision, evaluate_policy


@dataclass
class ManifestScanResult:
    """A successful or failed attempt to scan one dependency manifest."""

    path: str
    report: Optional[ScanReport] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "error": self.error,
            "report": self.report.to_dict() if self.report else None,
        }


@dataclass
class RepositoryScanResult:
    """The result suitable for a CI status check or a webhook response."""

    repository: str
    manifests: List[ManifestScanResult] = field(default_factory=list)
    decision: PolicyDecision = field(
        default_factory=lambda: PolicyDecision("PASS", "SAFE", "No manifests were scanned.")
    )

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "decision": {
                "status": self.decision.status,
                "highest_level": self.decision.highest_level,
                "message": self.decision.message,
            },
            "manifests": [manifest.to_dict() for manifest in self.manifests],
        }


class RepositoryScanner:
    """Coordinate manifest discovery, SCDS execution, and policy evaluation."""

    def __init__(self, policy: Optional[Policy] = None, cache_enabled: bool = True):
        self.policy = policy or Policy()
        self.engine = RiskEngine(cache_enabled=cache_enabled)

    def scan_repository(self, repository: str | Path) -> RepositoryScanResult:
        """Scan every supported manifest in a repository."""
        return self._scan_paths(Path(repository), discover_manifests(repository))

    def scan_changed_files(
        self, repository: str | Path, changed_paths: Iterable[str | Path]
    ) -> RepositoryScanResult:
        """Scan only supported manifests listed in a source-control event."""
        return self._scan_paths(Path(repository), changed_manifests(repository, changed_paths))

    def _scan_paths(self, repository: Path, paths: Iterable[Path]) -> RepositoryScanResult:
        root = repository.resolve()
        manifest_results: List[ManifestScanResult] = []
        levels: List[str] = []

        for path in paths:
            relative_path = str(path.relative_to(root))
            try:
                dependencies = parse_manifest(str(path))
                report = self.engine.scan_dependencies(dependencies, manifest_name=relative_path)
                manifest_results.append(ManifestScanResult(path=relative_path, report=report))
                levels.extend(result.risk_level for result in report.results)
            except Exception as exc:
                manifest_results.append(ManifestScanResult(path=relative_path, error=str(exc)))

        decision = evaluate_policy(levels, self.policy)
        if any(result.error for result in manifest_results):
            decision = PolicyDecision("BLOCK", decision.highest_level, "Blocked: one or more manifests could not be scanned.")

        return RepositoryScanResult(str(root), manifest_results, decision)
