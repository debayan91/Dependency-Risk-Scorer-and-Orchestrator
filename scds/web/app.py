"""
FastAPI Backend for the SCDS Web Dashboard.
Provides RESTful scanning endpoints and serves the modern interactive UI.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scds import __version__
from scds.engine import RiskEngine
from scds.parsers import Dependency, parse_manifest

app = FastAPI(
    title="Supply Chain Dependency Risk Scorer (SCDS)",
    version=__version__,
    description="Deterministic supply chain risk scoring API and enterprise dashboard."
)

# Enable CORS for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RiskEngine(cache_enabled=True)
STATIC_DIR = Path(__file__).parent / "static"


class CheckRequest(BaseModel):
    name: str
    version: Optional[str] = None
    ecosystem: str = "PyPI"


class ScanTextRequest(BaseModel):
    content: str
    filename: str = "requirements.txt"
    fail_on: Optional[str] = None
    threshold: Optional[float] = None


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": __version__,
        "engine": "SCDS Deterministic Risk Engine",
        "author": "Debayan Dutta (23BCE0815)"
    }


@app.post("/api/check")
def check_single_package(req: CheckRequest) -> Dict[str, Any]:
    """Evaluates a single dependency."""
    try:
        dep = Dependency(name=req.name.strip(), version=req.version, ecosystem=req.ecosystem)
        report = engine.evaluate_dependency(dep)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan/text")
def scan_manifest_text(req: ScanTextRequest) -> Dict[str, Any]:
    """Scans manifest provided as raw text."""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Manifest content is empty.")

    # Write temporarily to disk for parser
    suffix = Path(req.filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as tmp:
        tmp.write(req.content)
        tmp_path = tmp.name

    try:
        deps = parse_manifest(tmp_path, hint_filename=req.filename)
        report = engine.scan_dependencies(
            dependencies=deps,
            manifest_name=req.filename,
            fail_on_level=req.fail_on,
            fail_threshold=req.threshold
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scan manifest: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/api/samples/{sample_id}")
def get_sample(sample_id: str) -> Dict[str, Any]:
    """Returns sample manifests for quick testing and demonstration."""
    samples = {
        "npm_compromised": {
            "filename": "package.json",
            "ecosystem": "npm",
            "content": """{
  "name": "my-web-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.19.2",
    "lodsh": "^0.0.1",
    "lodash": "4.17.15",
    "react": "18.2.0",
    "react_dom": "18.2.0",
    "axios": "^1.6.8"
  },
  "devDependencies": {
    "jest": "^29.7.0"
  }
}"""
        },
        "pypi_vulnerable": {
            "filename": "requirements.txt",
            "ecosystem": "PyPI",
            "content": """# Production Dependencies
requests==2.20.0
reqeusts==0.0.1
flask==3.0.3
coloramaa==0.4.6
urllib3==1.24.2
pytest>=7.4.0
pydantic
"""
        },
        "maven_sample": {
            "filename": "pom.xml",
            "ecosystem": "Maven",
            "content": """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>demo-app</artifactId>
  <version>1.0.0</version>
  <dependencies>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-core</artifactId>
      <version>2.14.1</version>
    </dependency>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>31.1-jre</version>
    </dependency>
  </dependencies>
</project>"""
        }
    }

    if sample_id not in samples:
        raise HTTPException(status_code=404, detail="Sample not found.")
    return samples[sample_id]


# Serve frontend static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"message": "SCDS API is running. Static files loading..."})
