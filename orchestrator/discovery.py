"""Find supported dependency manifests in a repository."""

from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Sequence

from orchestrator.config import IGNORED_DIRECTORIES, ManifestRule, SUPPORTED_MANIFESTS


def is_supported_manifest(path: Path, rules: Sequence[ManifestRule] = SUPPORTED_MANIFESTS) -> bool:
    """Return whether *path* has a filename handled by a configured rule."""
    return any(fnmatch(path.name.lower(), rule.pattern.lower()) for rule in rules)


def discover_manifests(
    repository: str | Path,
    rules: Sequence[ManifestRule] = SUPPORTED_MANIFESTS,
) -> List[Path]:
    """Recursively return supported manifests below *repository*.

    Returned paths are absolute, sorted paths to make scans deterministic.
    """
    root = Path(repository).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Repository directory not found: {root}")

    manifests: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts[:-1]):
            continue
        if is_supported_manifest(path, rules):
            manifests.append(path)
    return sorted(manifests)


def changed_manifests(
    repository: str | Path,
    changed_paths: Iterable[str | Path],
    rules: Sequence[ManifestRule] = SUPPORTED_MANIFESTS,
) -> List[Path]:
    """Return supported files from a Git/CI change event.

    Paths outside the repository, deleted files, and unsupported files are
    ignored. This lets webhook adapters safely pass changed-file lists through.
    """
    root = Path(repository).resolve()
    found: List[Path] = []
    for changed in changed_paths:
        candidate = Path(changed)
        path = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            continue
        if path.is_file() and is_supported_manifest(path, rules):
            found.append(path)
    return sorted(set(found))
