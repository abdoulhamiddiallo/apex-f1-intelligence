# -*- coding: utf-8 -*-
"""Single source of truth for every path and constant used by the build.

All paths are derived from the repository root so the project rebuilds anywhere.
Nothing in this file depends on the machine it runs on.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- inputs (committed) ----
RAW_DIR = ROOT / "data" / "raw"
F1DB_ZIP = RAW_DIR / "f1db-csv.zip"
F1DB_ZIP_SHA256 = "82a5102e1157a4096cd38bae72e581aaa52083d2ceca7942acfe7744e214c9a6"
F1DB_RELEASE = "v2026.13.0"
F1DB_URL = "https://github.com/f1db/f1db/releases/download/%s/f1db-csv.zip" % F1DB_RELEASE
CIRCUITS_GEOJSON = RAW_DIR / "f1-circuits.geojson"
LOGO_DIR = ROOT / "assets" / "logos"

# ---- intermediate (ignored by git) ----
BUILD_DIR = ROOT / "build"
F1DB_DIR = BUILD_DIR / "f1db"          # unzipped f1db CSV files
ASSET_DIR = BUILD_DIR / "assets"       # generated PNG resources (background, mark, icons)

# ---- outputs (committed, reproducible bit for bit) ----
DIST_DIR = ROOT / "dist"
NAME = "APEX"
DATA_DIR = DIST_DIR / "data"                       # CSV files the semantic model reads
REPORT_DIR = DIST_DIR / (NAME + ".Report")
MODEL_DIR = DIST_DIR / (NAME + ".SemanticModel")

# Default value of the DataFolder parameter written into the semantic model.
# Power BI needs an absolute path; edit the parameter after opening the project.
DEFAULT_DATA_FOLDER = r"C:\apex-f1-intelligence\dist\data"

# ---- era ----
YEAR_FROM, YEAR_TO = 2014, 2026

def ensure_dirs():
    for p in (BUILD_DIR, F1DB_DIR, ASSET_DIR, DIST_DIR, DATA_DIR):
        p.mkdir(parents=True, exist_ok=True)
