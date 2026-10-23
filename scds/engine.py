"""
Deterministic and Explainable Risk Engine for SCDS.
Aggregates Vulnerability, Typosquatting, and Maintainer Trust scores using weighted mathematical models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from scds.analyzers import (
    MaintainerTrustAnalyzer,
    MaintainerTrustResult,
    TyposquattingAnalyzer,
    TyposquattingResult,
    VulnerabilityAnalyzer,
    VulnerabilityResult,
)
from scds.config import (
    THRESHOLD_HIGH,
    THRESHOLD_LOW,
    THRESHOLD_MEDIUM,
    THRESHOLD_SAFE,
    WEIGHT_MAINTAINER,
    WEIGHT_TYPOSQUATTING,
    WEIGHT_VULNERABILITY,
)
from scds.parsers import Dependency


@dataclass
class DependencyRiskReport:
    dependency: Dependency
    total_risk_score: float  # 0.0 to 10.0
    risk_level: str  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    vulnerability: VulnerabilityResult
    typosquatting: TyposquattingResult
    maintainer: MaintainerTrustResult
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.dependency.name,
            "version": self.dependency.version or "unspecified",
            "ecosystem": self.dependency.ecosystem,
            "is_dev": self.dependency.is_dev,
            "total_risk_score": self.total_risk_score,
            "risk_level": self.risk_level,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "breakdown": {
                "vulnerability_score": self.vulnerability.risk_score,
                "typosquatting_score": self.typosquatting.risk_score,
                "maintainer_score": self.maintainer.risk_score,
            },
            "vulnerabilities": [
                {
                    "id": v.id,
                    "aliases": v.aliases,
                    "summary": v.summary,
                    "severity": v.severity,
                    "cvss_score": v.cvss_score,
                }
                for v in self.vulnerability.vulnerabilities
            ],
            "typosquatting_info": {
                "is_typosquat": self.typosquatting.is_typosquat,
                "target_package": self.typosquatting.target_package,
                "levenshtein": self.typosquatting.levenshtein,
                "similarity": self.typosquatting.similarity,
            },
            "maintainer_info": {
                "flags": self.maintainer.flags,
                "age_days": self.maintainer.age_days,
                "last_release_days": self.maintainer.last_release_days,
                "has_repository": self.maintainer.has_repository,
                "is_unpinned": self.maintainer.is_unpinned,
            }
        }


@dataclass
class ScanReport:
    target_manifest: str
    ecosystem: str
    scan_timestamp: str
    dependencies_scanned: int
    risk_summary: Dict[str, int]
    max_risk_score: float
    avg_risk_score: float
    results: List[DependencyRiskReport] = field(default_factory=list)
    failed_ci: bool = False
    fail_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_manifest": self.target_manifest,
            "ecosystem": self.ecosystem,
            "scan_timestamp": self.scan_timestamp,
            "dependencies_scanned": self.dependencies_scanned,
            "risk_summary": self.risk_summary,
            "max_risk_score": self.max_risk_score,
            "avg_risk_score": self.avg_risk_score,
            "failed_ci": self.failed_ci,
            "fail_reason": self.fail_reason,
            "results": [r.to_dict() for r in self.results]
        }


class RiskEngine:
    """
    Central Risk Engine orchestrating all analyzers and computing
    transparent, deterministic supply chain risk scores.
    """

    def __init__(self, cache_enabled: bool = True):
        self.typo_analyzer = TyposquattingAnalyzer()
        self.vuln_analyzer = VulnerabilityAnalyzer(cache_enabled=cache_enabled)
        self.maintainer_analyzer = MaintainerTrustAnalyzer(cache_enabled=cache_enabled)

    def calculate_risk_level(self, score: float) -> str:
        if score <= THRESHOLD_SAFE:
            return "SAFE"
        elif score <= THRESHOLD_LOW:
            return "LOW"
        elif score <= THRESHOLD_MEDIUM:
            return "MEDIUM"
        elif score <= THRESHOLD_HIGH:
            return "HIGH"
        return "CRITICAL"

    def evaluate_dependency(self, dep: Dependency) -> DependencyRiskReport:
        # Run individual analyzers
        typo_res = self.typo_analyzer.analyze(dep.name, dep.ecosystem)
        vuln_res = self.vuln_analyzer.query_single(dep.name, dep.version, dep.ecosystem)
        maint_res = self.maintainer_analyzer.analyze(dep.name, dep.version, dep.ecosystem)

        # Weighted calculation
        raw_weighted_score = (
            (WEIGHT_VULNERABILITY * vuln_res.risk_score) +
            (WEIGHT_TYPOSQUATTING * typo_res.risk_score) +
            (WEIGHT_MAINTAINER * maint_res.risk_score)
        )

        # Security override rule: A confirmed high-confidence attack vector (e.g. Typosquatting or Critical CVE)
        # must never be diluted down into a "Low" score by good maintainer metadata
        max_vector = max(vuln_res.risk_score, typo_res.risk_score)
        if max_vector >= 9.0:
            final_score = max(raw_weighted_score, max_vector * 0.95)
        elif max_vector >= 7.5:
            final_score = max(raw_weighted_score, max_vector * 0.90)
        else:
            final_score = raw_weighted_score

        final_score = round(min(10.0, max(0.0, final_score)), 1)
        risk_level = self.calculate_risk_level(final_score)

        # Build explainable findings and actionable remediation recommendations
        findings: List[str] = []
        recommendations: List[str] = []

        if typo_res.is_typosquat:
            findings.append(f"[TYPOSQUATTING] {typo_res.explanation}")
            if typo_res.target_package:
                recommendations.append(
                    f"Replace '{dep.name}' with verified legitimate package '{typo_res.target_package}'."
                )

        if vuln_res.vuln_count > 0:
            findings.append(f"[VULNERABILITY] {vuln_res.explanation}")
            recommendations.append("Upgrade dependency to a patched non-vulnerable release.")

        if maint_res.flags:
            for flag in maint_res.flags:
                findings.append(f"[MAINTAINER] {flag}")

        if maint_res.is_unpinned:
            recommendations.append("Pin exact dependency version (e.g., '==1.2.3') in your manifest.")

        if not findings:
            findings.append("No active supply chain risk indicators found. Dependency is verified.")

        return DependencyRiskReport(
            dependency=dep,
            total_risk_score=final_score,
            risk_level=risk_level,
            vulnerability=vuln_res,
            typosquatting=typo_res,
            maintainer=maint_res,
            findings=findings,
            recommendations=recommendations
        )

    def scan_dependencies(
        self,
        dependencies: List[Dependency],
        manifest_name: str = "manifest",
        fail_on_level: Optional[str] = None,
        fail_threshold: Optional[float] = None
    ) -> ScanReport:
        """
        Scans a collection of dependencies, computes aggregations, and determines CI/CD status.
        """
        results: List[DependencyRiskReport] = []
        summary = {"SAFE": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        max_score = 0.0
        total_score = 0.0

        for dep in dependencies:
            rep = self.evaluate_dependency(dep)
            results.append(rep)
            summary[rep.risk_level] = summary.get(rep.risk_level, 0) + 1
            if rep.total_risk_score > max_score:
                max_score = rep.total_risk_score
            total_score += rep.total_risk_score

        avg_score = round(total_score / len(results), 1) if results else 0.0
        ecosystem = dependencies[0].ecosystem if dependencies else "Unknown"

        # Determine CI/CD gate status
        failed_ci = False
        fail_reason = None

        level_order = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        if fail_threshold is not None and max_score >= fail_threshold:
            failed_ci = True
            fail_reason = f"Maximum risk score {max_score} exceeds threshold {fail_threshold}."
        elif fail_on_level:
            target_level = fail_on_level.upper()
            target_rank = level_order.get(target_level, 3)
            for r in results:
                if level_order.get(r.risk_level, 0) >= target_rank:
                    failed_ci = True
                    fail_reason = f"Found {r.risk_level} risk package '{r.dependency.name}' (breaches policy: fail on {target_level})."
                    break

        return ScanReport(
            target_manifest=manifest_name,
            ecosystem=ecosystem,
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
            dependencies_scanned=len(results),
            risk_summary=summary,
            max_risk_score=max_score,
            avg_risk_score=avg_score,
            results=results,
            failed_ci=failed_ci,
            fail_reason=fail_reason
        )
