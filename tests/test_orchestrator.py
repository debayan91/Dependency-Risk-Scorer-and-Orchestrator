"""Tests for repository-level orchestration without network requests."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from orchestrator.discovery import changed_manifests, discover_manifests
from orchestrator.policy import Policy, evaluate_policy
from orchestrator.service import RepositoryScanner
from scds.engine import ScanReport


class TestManifestDiscovery(unittest.TestCase):
    def test_discovers_only_supported_source_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "requirements.txt").write_text("requests==2.31.0")
            (root / "backend").mkdir()
            (root / "backend" / "pom.xml").write_text("<project />")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "package.json").write_text("{}")
            (root / "README.md").write_text("ignored")

            self.assertEqual(
                [path.relative_to(root).as_posix() for path in discover_manifests(root)],
                ["backend/pom.xml", "requirements.txt"],
            )

    def test_changed_files_filters_deleted_and_unsupported_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text("{}")
            selected = changed_manifests(root, ["package.json", "README.md", "missing/pom.xml"])
            self.assertEqual([path.name for path in selected], ["package.json"])


class TestPolicy(unittest.TestCase):
    def test_policy_warns_and_blocks_at_configured_levels(self):
        policy = Policy(warn_on="MEDIUM", block_on="HIGH")
        self.assertEqual(evaluate_policy(["LOW", "MEDIUM"], policy).status, "WARN")
        self.assertEqual(evaluate_policy(["CRITICAL"], policy).status, "BLOCK")


class TestRepositoryScanner(unittest.TestCase):
    def test_scanner_delegates_to_the_existing_risk_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text("requests==2.31.0")
            scanner = RepositoryScanner(policy=Policy(warn_on="MEDIUM", block_on="HIGH"))
            scanner.engine = Mock()
            scanner.engine.scan_dependencies.return_value = ScanReport(
                target_manifest="requirements.txt", ecosystem="PyPI", scan_timestamp="now",
                dependencies_scanned=1, risk_summary={"SAFE": 1}, max_risk_score=0.0,
                avg_risk_score=0.0, results=[], failed_ci=False,
            )

            result = scanner.scan_repository(root)

            scanner.engine.scan_dependencies.assert_called_once()
            self.assertEqual(result.decision.status, "PASS")
            self.assertEqual(result.manifests[0].path, "requirements.txt")


if __name__ == "__main__":
    unittest.main()
