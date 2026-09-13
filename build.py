#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the whole APEX project from the committed inputs.

    python build.py            full build into dist/ followed by validation
    python build.py --check    build, validate, then rebuild and prove that both
                               builds are identical bit for bit
    python build.py --clean    remove build/ and dist/ before building

Pipeline (each step is a module of the ``apex`` package):

    1. unzip     data/raw/f1db-csv.zip  ->  build/f1db/        (sha256 verified)
    2. data      f1db CSV + circuit GeoJSON  ->  dist/data/*.csv
    3. logo      brand mark and navigation icons  ->  build/assets/*.png
    4. background page background and accent strips  ->  build/assets/*.png
    5. svg_columns flags, cars, helmets, crests  ->  SVG data URIs inside dist/data
    6. model     TMDL semantic model  ->  dist/APEX.SemanticModel/
    7. measures  DAX measures  ->  dist/APEX.SemanticModel/definition/tables/Metrics.tmdl
    8. report    PBIR report (9 pages)  ->  dist/APEX.Report/
    9. validate  structural checks that fail the build on any defect

Everything the build needs travels with the repository; no network access is required.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apex import config  # noqa: E402

STEPS = ["data", "logo", "background", "svg_columns", "model", "measures", "report"]


def sha256_file(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def unzip_f1db():
    """Verify the committed f1db archive and extract it into build/f1db."""
    digest = sha256_file(config.F1DB_ZIP)
    if digest != config.F1DB_ZIP_SHA256:
        sys.exit("f1db archive checksum mismatch:\n  expected %s\n  actual   %s"
                 % (config.F1DB_ZIP_SHA256, digest))
    if config.F1DB_DIR.exists():
        shutil.rmtree(config.F1DB_DIR)
    config.F1DB_DIR.mkdir(parents=True)
    with zipfile.ZipFile(config.F1DB_ZIP) as z:
        names = [n for n in z.namelist() if n.endswith(".csv")]
        for n in names:
            # flatten: some releases nest the CSV files in a folder
            target = config.F1DB_DIR / Path(n).name
            with z.open(n) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    print("f1db %s: %d CSV files extracted (sha256 ok)" % (config.F1DB_RELEASE, len(names)))


def run_step(name):
    t0 = time.time()
    print("\n=== apex.%s" % name, flush=True)
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "apex." + name], cwd=str(config.ROOT), env=env)
    if r.returncode != 0:
        sys.exit("step apex.%s failed with exit code %d" % (name, r.returncode))
    print("    done in %.1fs" % (time.time() - t0))


def snapshot(folder):
    """Return {relative path: sha256} for every file under folder."""
    out = {}
    for p in sorted(Path(folder).rglob("*")):
        if p.is_file():
            out[str(p.relative_to(folder)).replace(os.sep, "/")] = sha256_file(p)
    return out


def build(clean=False):
    if clean:
        for d in (config.BUILD_DIR, config.DIST_DIR):
            if d.exists():
                shutil.rmtree(d)
    if config.DIST_DIR.exists():
        # start from a clean output folder so stale files can never survive a rebuild
        shutil.rmtree(config.DIST_DIR)
    config.ensure_dirs()
    unzip_f1db()
    for s in STEPS:
        run_step(s)
    run_step("validate")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="build twice and require bit-identical output")
    ap.add_argument("--clean", action="store_true", help="remove build/ and dist/ first")
    a = ap.parse_args()

    t0 = time.time()
    build(clean=a.clean)
    if a.check:
        first = snapshot(config.DIST_DIR)
        print("\n=== determinism check: rebuilding from scratch")
        build(clean=True)
        second = snapshot(config.DIST_DIR)
        changed = sorted(k for k in set(first) | set(second) if first.get(k) != second.get(k))
        if changed:
            print("NOT reproducible, %d file(s) differ:" % len(changed))
            for k in changed[:50]:
                print("   ", k)
            sys.exit(1)
        print("reproducible: %d files identical across two builds" % len(first))
    print("\nbuild complete in %.0fs -> %s" % (time.time() - t0, config.DIST_DIR))


if __name__ == "__main__":
    main()
