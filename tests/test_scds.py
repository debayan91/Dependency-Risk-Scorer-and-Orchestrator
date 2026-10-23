"""
Unit and Integration Tests for Supply Chain Dependency Risk Scorer (SCDS).
"""

import os
import tempfile
import unittest
from click.testing import CliRunner

from scds.algorithms.distance import levenshtein_distance, jaro_similarity, jaro_winkler_similarity
from scds.analyzers.typosquatting import TyposquattingAnalyzer
from scds.cache import CacheManager
from scds.cli import cli
from scds.engine import RiskEngine
from scds.parsers import Dependency, detect_ecosystem, parse_manifest
from scds.parsers.maven import parse_pom_xml
from scds.parsers.npm import parse_package_json
from scds.parsers.pypi import parse_requirements_txt


class TestStringDistanceAlgorithms(unittest.TestCase):
    def test_levenshtein(self):
        self.assertEqual(levenshtein_distance("requests", "requests"), 0)
        self.assertEqual(levenshtein_distance("reqeusts", "requests"), 2)
        self.assertEqual(levenshtein_distance("lodsh", "lodash"), 1)
        self.assertEqual(levenshtein_distance("expres", "express"), 1)
        self.assertEqual(levenshtein_distance("coloramaa", "colorama"), 1)
        self.assertEqual(levenshtein_distance("", "test"), 4)

    def test_jaro_winkler(self):
        self.assertEqual(jaro_winkler_similarity("requests", "requests"), 1.0)
        self.assertGreater(jaro_winkler_similarity("lodsh", "lodash"), 0.90)
        self.assertGreater(jaro_winkler_similarity("coloramaa", "colorama"), 0.94)
        self.assertLess(jaro_winkler_similarity("numpy", "tensorflow"), 0.6)


class TestManifestParsers(unittest.TestCase):
    def test_npm_parser(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("""{
                "dependencies": { "express": "^4.19.2", "lodash": "4.17.15" },
                "devDependencies": { "jest": "~29.7.0" }
            }""")
            tmp_path = f.name

        try:
            deps = parse_package_json(tmp_path)
            self.assertEqual(len(deps), 3)
            dep_map = {d.name: d for d in deps}
            self.assertIn("express", dep_map)
            self.assertEqual(dep_map["express"].version, "4.19.2")
            self.assertFalse(dep_map["express"].is_dev)

            self.assertIn("jest", dep_map)
            self.assertEqual(dep_map["jest"].version, "29.7.0")
            self.assertTrue(dep_map["jest"].is_dev)
        finally:
            os.remove(tmp_path)

    def test_pypi_parser(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("""
                # Comments should be ignored
                requests==2.31.0
                flask >= 3.0.0
                pydantic
                --extra-index-url https://custom.repo/
            """)
            tmp_path = f.name

        try:
            deps = parse_requirements_txt(tmp_path)
            self.assertEqual(len(deps), 3)
            dep_map = {d.name: d for d in deps}
            self.assertEqual(dep_map["requests"].version, "2.31.0")
            self.assertEqual(dep_map["flask"].version, "3.0.0")
            self.assertIsNone(dep_map["pydantic"].version)
        finally:
            os.remove(tmp_path)

    def test_maven_parser(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("""<project>
                <dependencies>
                    <dependency>
                        <groupId>org.apache.logging.log4j</groupId>
                        <artifactId>log4j-core</artifactId>
                        <version>2.14.1</version>
                    </dependency>
                </dependencies>
            </project>""")
            tmp_path = f.name

        try:
            deps = parse_pom_xml(tmp_path)
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].name, "org.apache.logging.log4j:log4j-core")
            self.assertEqual(deps[0].version, "2.14.1")
            self.assertEqual(deps[0].ecosystem, "Maven")
        finally:
            os.remove(tmp_path)


class TestTyposquattingAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TyposquattingAnalyzer()

    def test_legitimate_package_is_safe(self):
        res = self.analyzer.analyze("requests", "PyPI")
        self.assertFalse(res.is_typosquat)
        self.assertEqual(res.risk_score, 0.0)

    def test_single_char_edit_typosquat(self):
        res = self.analyzer.analyze("lodsh", "npm")
        self.assertTrue(res.is_typosquat)
        self.assertEqual(res.target_package, "lodash")
        self.assertGreaterEqual(res.risk_score, 9.0)

    def test_transposition_typosquat(self):
        res = self.analyzer.analyze("reqeusts", "PyPI")
        self.assertTrue(res.is_typosquat)
        self.assertEqual(res.target_package, "requests")
        self.assertGreaterEqual(res.risk_score, 7.5)

    def test_separator_confusion(self):
        res = self.analyzer.analyze("react_dom", "npm")
        self.assertTrue(res.is_typosquat)
        self.assertEqual(res.target_package, "react-dom")
        self.assertGreaterEqual(res.risk_score, 9.0)


class TestCacheManager(unittest.TestCase):
    def test_cache_set_get_and_expiration(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            cache = CacheManager(db_path=db_path)
            cache.set("test_ns", "key1", {"status": "ok"}, ttl=2)
            self.assertEqual(cache.get("test_ns", "key1"), {"status": "ok"})
            self.assertIsNone(cache.get("test_ns", "nonexistent"))

            # Expired item test
            cache.set("test_ns", "key2", "expired_val", ttl=-1)
            self.assertIsNone(cache.get("test_ns", "key2"))
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestRiskEngineAndCICD(unittest.TestCase):
    def setUp(self):
        self.engine = RiskEngine(cache_enabled=True)

    def test_clean_dependency(self):
        dep = Dependency(name="pydantic", version="2.6.4", ecosystem="PyPI")
        res = self.engine.evaluate_dependency(dep)
        self.assertEqual(res.risk_level, "SAFE")
        self.assertLessEqual(res.total_risk_score, 2.9)

    def test_typosquat_escalation(self):
        dep = Dependency(name="lodsh", version="0.0.1", ecosystem="npm")
        res = self.engine.evaluate_dependency(dep)
        self.assertIn(res.risk_level, ("HIGH", "CRITICAL"))
        self.assertTrue(any("[TYPOSQUATTING]" in f for f in res.findings))

    def test_ci_fail_policy(self):
        deps = [
            Dependency(name="express", version="4.19.2", ecosystem="npm"),
            Dependency(name="lodsh", version="0.0.1", ecosystem="npm")
        ]
        report = self.engine.scan_dependencies(deps, fail_on_level="HIGH")
        self.assertTrue(report.failed_ci)
        self.assertIsNotNone(report.fail_reason)


class TestCLIExecution(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_check_single(self):
        result = self.runner.invoke(cli, ["check", "requests", "--ecosystem", "PyPI"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("requests", result.output)

    def test_cli_scan_sample_and_exit_code(self):
        # Scan samples/package.json with fail-on HIGH (contains lodsh -> should exit 1)
        result = self.runner.invoke(cli, ["scan", "samples/package.json", "--fail-on", "HIGH"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("FAILED CI/CD POLICY GATE", result.output)


if __name__ == "__main__":
    unittest.main()
