"""
Parser for NPM package.json manifest files.
"""

import json
import re
from pathlib import Path
from typing import List

from scds.parsers import Dependency


def clean_npm_version(raw_version: str) -> str:
    """
    Cleans semver prefixes like ^, ~, >=, <=, v, etc.
    """
    if not raw_version:
        return ""
    cleaned = raw_version.strip()
    # Remove leading operators and 'v'
    cleaned = re.sub(r"^[~^><=v\s]+", "", cleaned)
    # Remove build metadata or pr-release tags for basic matching
    cleaned = re.split(r"[\s<>=|]+", cleaned)[0]
    return cleaned.strip()


def parse_package_json(file_path: str) -> List[Dependency]:
    """
    Parses package.json to extract direct and development dependencies.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    dependencies: List[Dependency] = []

    # Direct dependencies
    prod_deps = data.get("dependencies", {})
    if isinstance(prod_deps, dict):
        for name, version in prod_deps.items():
            dependencies.append(
                Dependency(
                    name=name.strip(),
                    version=clean_npm_version(str(version)),
                    ecosystem="npm",
                    is_dev=False
                )
            )

    # Dev dependencies
    dev_deps = data.get("devDependencies", {})
    if isinstance(dev_deps, dict):
        for name, version in dev_deps.items():
            dependencies.append(
                Dependency(
                    name=name.strip(),
                    version=clean_npm_version(str(version)),
                    ecosystem="npm",
                    is_dev=True
                )
            )

    # Optional / peer dependencies
    peer_deps = data.get("peerDependencies", {})
    if isinstance(peer_deps, dict):
        for name, version in peer_deps.items():
            if not any(d.name == name for d in dependencies):
                dependencies.append(
                    Dependency(
                        name=name.strip(),
                        version=clean_npm_version(str(version)),
                        ecosystem="npm",
                        is_dev=True
                    )
                )

    return dependencies
