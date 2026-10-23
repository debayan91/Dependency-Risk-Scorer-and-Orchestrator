"""Supported manifest definitions for repository scanning.

Add a pattern here when SCDS gains a parser for another dependency ecosystem.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ManifestRule:
    """A filename pattern that can be analysed by the current SCDS parser."""

    pattern: str
    ecosystem: str


# These patterns deliberately cover only formats the existing SCDS parsers can
# interpret. Lockfiles and other formats can be added when they have parsers.
SUPPORTED_MANIFESTS: Tuple[ManifestRule, ...] = (
    ManifestRule("package.json", "npm"),
    ManifestRule("requirements*.txt", "PyPI"),
    ManifestRule("pom.xml", "Maven"),
)

# Directories that are either generated, cached, or normally outside the source
# tree. Skipping them avoids duplicate and unexpectedly expensive scans.
IGNORED_DIRECTORIES = frozenset({
    ".git", ".hg", ".svn", ".tox", ".venv", "venv", "node_modules",
    "vendor", "dist", "build", "__pycache__",
})
