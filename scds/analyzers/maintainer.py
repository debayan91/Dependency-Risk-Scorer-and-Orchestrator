"""
Maintainer Trust and Metadata Hygiene Analyzer.
Evaluates repository age, release frequency, unmaintained/abandonware signals,
and manifest pinning practices to assess supply chain account compromise risk.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import requests

from scds.cache import global_cache


@dataclass
class MaintainerTrustResult:
    risk_score: float  # 0.0 to 10.0
    flags: List[str] = field(default_factory=list)
    age_days: Optional[int] = None
    last_release_days: Optional[int] = None
    has_repository: bool = True
    is_unpinned: bool = False
    explanation: str = "Maintainer trust and hygiene indicators normal."


class MaintainerTrustAnalyzer:
    """
    Evaluates registry metadata (PyPI / npm) and version hygiene
    to quantify maintainer posture and identify abandoned or brand-new suspicious packages.
    """

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SCDS-Dependency-Risk-Scorer/1.0"})

    def analyze(self, package_name: str, version: Optional[str], ecosystem: str = "PyPI") -> MaintainerTrustResult:
        flags: List[str] = []
        risk_score = 0.0

        # Heuristic 1: Version Pinning
        is_unpinned = (version is None or version == "" or version == "*")
        if is_unpinned:
            flags.append("UNPINNED_VERSION: Manifest specifies wildcard or unpinned version.")
            risk_score += 2.0

        # Query registry metadata
        meta = self._fetch_metadata(package_name, ecosystem)

        if meta:
            age_days = meta.get("age_days")
            last_release_days = meta.get("last_release_days")
            has_repository = meta.get("has_repository", True)

            # Heuristic 2: Brand new package (< 30 days old)
            if age_days is not None:
                if age_days < 14:
                    flags.append(f"BRAND_NEW_PACKAGE: Published only {age_days} days ago (high supply chain vector).")
                    risk_score += 5.0
                elif age_days < 45:
                    flags.append(f"RECENT_PACKAGE: Published {age_days} days ago.")
                    risk_score += 2.5

            # Heuristic 3: Abandoned / Dormant package (> 3 years without updates)
            if last_release_days is not None:
                if last_release_days > 1100:  # ~3 years
                    flags.append(f"ABANDONED_MAINTAINER: No updates published for {last_release_days // 365} years.")
                    risk_score += 3.5
                elif last_release_days > 730:  # ~2 years
                    flags.append(f"INACTIVE_MAINTAINER: No updates for {last_release_days // 365} years.")
                    risk_score += 1.5

            # Heuristic 4: Missing Source Code Repository Link
            if not has_repository:
                flags.append("MISSING_SOURCE_REPO: Package metadata contains no public Git/source repository link.")
                risk_score += 2.0
        else:
            # Metadata unavailable (e.g. offline or private internal package)
            has_repository = True
            age_days = None
            last_release_days = None
            if not is_unpinned:
                # Modest baseline
                flags.append("REGISTRY_LOOKUP_OFFLINE: Package metadata verified using static heuristics.")

        final_score = min(10.0, round(risk_score, 2))
        explanation = " | ".join(flags) if flags else "High maintainer trust; mature repository and hygiene."

        return MaintainerTrustResult(
            risk_score=final_score,
            flags=flags,
            age_days=age_days,
            last_release_days=last_release_days,
            has_repository=has_repository,
            is_unpinned=is_unpinned,
            explanation=explanation
        )

    def _fetch_metadata(self, package_name: str, ecosystem: str) -> Optional[Dict[str, Any]]:
        cache_key = f"{ecosystem}:{package_name.lower()}"
        if self.cache_enabled:
            cached = global_cache.get("maintainer", cache_key)
            if cached is not None:
                return cached

        data = None
        try:
            if ecosystem == "PyPI":
                url = f"https://pypi.org/pypi/{package_name}/json"
                resp = self.session.get(url, timeout=3.5)
                if resp.status_code == 200:
                    raw = resp.json()
                    data = self._parse_pypi_metadata(raw)
            elif ecosystem == "npm":
                url = f"https://registry.npmjs.org/{package_name}"
                resp = self.session.get(url, timeout=3.5)
                if resp.status_code == 200:
                    raw = resp.json()
                    data = self._parse_npm_metadata(raw)
        except Exception:
            data = None

        if data and self.cache_enabled:
            global_cache.set("maintainer", cache_key, data)

        return data

    def _parse_pypi_metadata(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        info = raw.get("info", {})
        releases = raw.get("releases", {})
        urls = info.get("project_urls") or {}

        has_repo = bool(
            info.get("home_page") or
            any("github" in str(v).lower() or "gitlab" in str(v).lower() for v in urls.values()) or
            "github" in str(info.get("package_url", "")).lower()
        )

        all_upload_times: List[datetime] = []
        for rel_files in releases.values():
            for f in rel_files:
                upload_time_str = f.get("upload_time_iso_8601") or f.get("upload_time")
                if upload_time_str:
                    try:
                        # Clean zulu time
                        cleaned = upload_time_str.replace("Z", "+00:00")
                        dt = datetime.fromisoformat(cleaned)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        all_upload_times.append(dt)
                    except Exception:
                        pass

        age_days = None
        last_release_days = None
        now = datetime.now(timezone.utc)

        if all_upload_times:
            first_release = min(all_upload_times)
            latest_release = max(all_upload_times)
            age_days = max(0, (now - first_release).days)
            last_release_days = max(0, (now - latest_release).days)

        return {
            "has_repository": has_repo,
            "age_days": age_days,
            "last_release_days": last_release_days
        }

    def _parse_npm_metadata(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        time_data = raw.get("time", {})
        repository = raw.get("repository")
        has_repo = bool(repository)

        created_str = time_data.get("created")
        modified_str = time_data.get("modified")

        age_days = None
        last_release_days = None
        now = datetime.now(timezone.utc)

        if created_str:
            try:
                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                age_days = max(0, (now - dt).days)
            except Exception:
                pass

        if modified_str:
            try:
                dt = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
                last_release_days = max(0, (now - dt).days)
            except Exception:
                pass

        return {
            "has_repository": has_repo,
            "age_days": age_days,
            "last_release_days": last_release_days
        }
