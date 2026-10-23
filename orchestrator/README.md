# SCDS Repository Orchestrator

This package is the automation boundary around the existing `scds` analysis
engine. It does not replace or duplicate the scanner. Instead, it discovers
supported dependency manifests, calls `parse_manifest` and `RiskEngine`, then
returns a machine-readable policy decision suitable for CI or a future Git
provider integration.

## Supported manifests

- `package.json` (npm)
- `requirements*.txt` (Python/PyPI)
- `pom.xml` (Maven)

Generated and dependency directories such as `.git`, `node_modules`, `venv`,
and `vendor` are skipped.

## Local and CI entry points

Scan every supported manifest in a repository:

```bash
python3 -m orchestrator . --warn-on MEDIUM --block-on HIGH
```

Scan only the manifests supplied by a pull-request or webhook event:

```bash
python3 -m orchestrator . --changed requirements.txt --changed frontend/package.json
```

The command prints JSON and returns exit code `1` only for `BLOCK`; `PASS` and
`WARN` return `0`. A CI system can use that exit status as a required check.

## Integration boundary

A GitHub/GitLab app, webhook handler, scheduler, or background job should use
`RepositoryScanner.scan_changed_files()` for change events and
`RepositoryScanner.scan_repository()` for scheduled full scans. Such adapters
need repository read access; publishing a status/check is optional and can be
granted separately.
