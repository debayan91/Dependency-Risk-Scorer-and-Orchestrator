"""
Parser for PyPI requirements.txt manifest files.
"""

import re
from pathlib import Path
from typing import List

from scds.parsers import Dependency


def parse_requirements_txt(file_path: str) -> List[Dependency]:
    """
    Parses a requirements.txt file and returns extracted dependencies.
    """
    path = Path(file_path)
    dependencies: List[Dependency] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Ignore pip flags (-r, -f, -i, etc.)
            if line.startswith("-") or line.startswith("--"):
                continue

            # Strip environment markers (e.g. ; python_version >= '3.8')
            if ";" in line:
                line = line.split(";")[0].strip()

            # Match package name and version specification
            # Examples: requests==2.31.0, flask>=2.0, urllib3~=1.26, numpy
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([<>=!~]+.*)?$", line)
            if match:
                pkg_name = match.group(1).strip()
                version_spec = match.group(2)
                cleaned_version = ""
                if version_spec:
                    # Clean out relational operators and extra constraints
                    version_spec = version_spec.strip()
                    # If multiple constraints separated by comma, take the first
                    primary_spec = version_spec.split(",")[0].strip()
                    cleaned_version = re.sub(r"^[<>=!~]+", "", primary_spec).strip()

                dependencies.append(
                    Dependency(
                        name=pkg_name,
                        version=cleaned_version if cleaned_version else None,
                        ecosystem="PyPI",
                        is_dev=False
                    )
                )

    return dependencies
