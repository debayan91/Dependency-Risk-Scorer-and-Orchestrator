"""
Parser for Maven pom.xml manifest files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from scds.parsers import Dependency


def parse_pom_xml(file_path: str) -> List[Dependency]:
    """
    Parses pom.xml using standard ElementTree to extract Maven dependencies.
    """
    path = Path(file_path)
    dependencies: List[Dependency] = []

    try:
        tree = ET.parse(str(path))
        root = tree.getroot()

        # Handle XML namespace dynamically
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        # Find all <dependency> tags
        for dep in root.findall(f".//{ns}dependency"):
            group_elem = dep.find(f"{ns}groupId")
            artifact_elem = dep.find(f"{ns}artifactId")
            version_elem = dep.find(f"{ns}version")
            scope_elem = dep.find(f"{ns}scope")

            if group_elem is not None and artifact_elem is not None:
                group_id = (group_elem.text or "").strip()
                artifact_id = (artifact_elem.text or "").strip()
                version = (version_elem.text or "").strip() if version_elem is not None else None
                scope = (scope_elem.text or "").strip().lower() if scope_elem is not None else ""

                pkg_name = f"{group_id}:{artifact_id}" if group_id else artifact_id
                dependencies.append(
                    Dependency(
                        name=pkg_name,
                        version=version,
                        ecosystem="Maven",
                        is_dev=(scope in ("test", "provided"))
                    )
                )
    except Exception as e:
        raise ValueError(f"Failed to parse Maven pom.xml: {str(e)}")

    return dependencies
