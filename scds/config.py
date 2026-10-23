"""
Configuration settings, risk weights, severity thresholds, and curated popular package baselines.
"""

from typing import Dict, List, Set

# Weights for multi-vector risk engine (must sum to 1.0)
WEIGHT_VULNERABILITY = 0.45
WEIGHT_TYPOSQUATTING = 0.35
WEIGHT_MAINTAINER = 0.20

# Risk Level Boundaries (0.0 to 10.0 scale)
THRESHOLD_SAFE = 2.9
THRESHOLD_LOW = 5.4
THRESHOLD_MEDIUM = 7.4
THRESHOLD_HIGH = 8.9
# 9.0 - 10.0 is CRITICAL

# OSV API Endpoint
OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_QUERY_URL = "https://api.osv.dev/v1/query"

# Default Cache TTL: 24 Hours in seconds
DEFAULT_CACHE_TTL = 86400

# Curated Popular Packages (used as the ground truth baseline for Typosquatting Analysis)
POPULAR_PACKAGES: Dict[str, Set[str]] = {
    "PyPI": {
        "requests", "urllib3", "numpy", "pandas", "flask", "django", "scipy", "pytest",
        "boto3", "cryptography", "pydantic", "httpx", "aiohttp", "colorama", "black",
        "wheel", "setuptools", "pip", "certifi", "idna", "charset-normalizer", "attrs",
        "typing-extensions", "jinja2", "virtualenv", "six", "pytz", "pyyaml", "click",
        "rich", "pillow", "tqdm", "psutil", "transformers", "torch", "scikit-learn",
        "fastapi", "uvicorn", "celery", "redis", "sqlalchemy", "beautifulsoup4", "lxml",
        "paramiko", "gevent", "greenlet", "simplejson", "protobuf", "pygments", "markupsafe",
        "pluggy", "packaging", "iniconfig", "filelock", "platformdirs", "distlib"
    },
    "npm": {
        "lodash", "express", "react", "react-dom", "axios", "chalk", "vue", "next",
        "commander", "debug", "moment", "typescript", "webpack", "async", "uuid",
        "glob", "fs-extra", "rxjs", "request", "dotenv", "tslib", "core-js", "minimist",
        "semver", "colors", "body-parser", "cors", "cookie-parser", "multer", "nodemon",
        "jest", "mocha", "eslint", "prettier", "postcss", "babel-core", "jquery",
        "socket.io", "mongoose", "jsonwebtoken", "bcrypt", "winston", "morgan",
        "styled-components", "superagent", "yargs", "inquirer", "chokidar", "cheerio"
    },
    "Maven": {
        "org.springframework:spring-core", "org.springframework.boot:spring-boot-starter",
        "org.apache.commons:commons-lang3", "com.fasterxml.jackson.core:jackson-databind",
        "org.slf4j:slf4j-api", "junit:junit", "org.apache.logging.log4j:log4j-core",
        "com.google.guava:guava", "org.apache.httpcomponents:httpclient",
        "org.mockito:mockito-core", "ch.qos.logback:logback-classic", "com.google.code.gson:gson"
    }
}
