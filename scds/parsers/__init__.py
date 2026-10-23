"""
Manifest parsing modules for NPM (package.json), PyPI (requirements.txt), and Maven (pom.xml).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Dependency:
    name: str
    version: Optional[str] = None
    ecosystem: str = "PyPI"  # "npm", "PyPI", "Maven"
    is_dev: bool = False


def detect_ecosystem(file_path: str) -> str:
    """
    Infers package ecosystem from file name or extension.
    """
    name = Path(file_path).name.lower()
    if name == "package.json" or name.endswith(".json"):
        return "npm"
    elif name == "pom.xml" or name.endswith(".xml") or name.endswith(".gradle"):
        return "Maven"
    return "PyPI"


def parse_manifest(file_path: str, hint_filename: Optional[str] = None) -> List[Dependency]:
    """
    Automatically parses a manifest file based on ecosystem detection.
    """
    from scds.parsers.npm import parse_package_json
    from scds.parsers.pypi import parse_requirements_txt
    from scds.parsers.maven import parse_pom_xml

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {file_path}")

    target_name = (hint_filename or path.name).lower()
    if target_name == "package.json" or target_name.endswith(".json"):
        return parse_package_json(str(path))
    elif target_name == "pom.xml" or target_name.endswith(".xml"):
        return parse_pom_xml(str(path))
    else:
        # Default to PyPI requirements.txt parser
        return parse_requirements_txt(str(path))
