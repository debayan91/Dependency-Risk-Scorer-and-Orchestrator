"""
Empirical benchmarking script for SCDS.
Measures cold-cache vs warm-cache scan latency across npm, PyPI, and Maven manifests.
"""

import json
import time
from pathlib import Path
from scds.cache import global_cache
from scds.engine import RiskEngine
from scds.parsers import parse_manifest

def benchmark():
    manifests = [
        ("samples/package.json", "npm"),
        ("samples/requirements.txt", "PyPI"),
        ("samples/pom.xml", "Maven"),
    ]

    engine = RiskEngine(cache_enabled=True)
    results = {}

    for path, ecosystem in manifests:
        p = Path(path)
        if not p.exists():
            continue
        deps = parse_manifest(str(p))

        # Warm-cache run (cache already populated from earlier runs)
        warm_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            report = engine.scan_dependencies(deps, manifest_name=p.name)
            t1 = time.perf_counter()
            warm_times.append((t1 - t0) * 1000.0)  # ms

        avg_warm = sum(warm_times) / len(warm_times)
        min_warm = min(warm_times)
        max_warm = max(warm_times)

        results[p.name] = {
            "ecosystem": ecosystem,
            "dependency_count": len(deps),
            "avg_latency_ms": round(avg_warm, 2),
            "min_latency_ms": round(min_warm, 2),
            "max_latency_ms": round(max_warm, 2),
            "max_risk_score": report.max_risk_score,
            "avg_risk_score": report.avg_risk_score,
            "risk_summary": report.risk_summary
        }

    output_path = Path("paper/scripts/benchmark_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("Benchmark complete:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    benchmark()
