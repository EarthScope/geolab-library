#!/usr/bin/env python3
"""Generate fake project YAML files to test the gallery at scale.

Writes N projects (default 1000) to .dummy-projects/ (git-ignored), plus
copies of the real ones from projects/. Preview them with:

    python scripts/make_dummy_projects.py --count 1000
    GEOLAB_PROJECTS_DIR=.dummy-projects myst start

Thumbnails are a mix of real images (picsum.photos, so lazy loading is
exercised), none, and broken URLs (to exercise the fallback).
"""
import argparse
import pathlib
import random
import shutil

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

DOMAINS = ["seismology", "geodesy", "GNSS", "InSAR", "tectonics", "volcanology",
           "hydrology", "glaciology", "tsunami", "magnetotellurics", "gravity",
           "atmosphere", "oceanography", "seafloor geodesy", "infrasound"]
TECHNIQUES = ["cross-correlation", "machine learning", "time series", "inversion",
              "beamforming", "ambient noise", "receiver functions", "reflectometry",
              "tomography", "event detection", "visualization", "data access",
              "earthscope_sdk", "obspy", "xarray", "dask", "pygmt"]
SUBJECTS = ["Earthquake", "GNSS Station", "Seismic Noise", "Crustal Deformation",
            "Tremor", "Aftershock", "Ionosphere", "Snow Depth", "Tide Gauge",
            "Landslide", "Plate Motion", "Ground Motion", "Volcano Uplift"]
ACTIONS = ["Explorer", "Analysis", "Tutorial", "Workflow", "Dashboard",
           "Catalog", "Detection", "Mapping", "Primer", "Benchmark"]
FIRST = ["Alex", "Sam", "Jordan", "Riley", "Taylor", "Morgan", "Casey", "Jamie",
         "Avery", "Quinn", "Rowan", "Skyler", "Dana", "Kai", "Noor", "Ines"]
LAST = ["Garcia", "Chen", "Okafor", "Novak", "Silva", "Kim", "Haddad", "Larsen",
        "Moreau", "Patel", "Sato", "Kowalski", "Nguyen", "Adeyemi", "Rossi"]
VERBS = ["explores", "walks through", "demonstrates", "compares", "visualizes",
         "benchmarks", "automates"]


def dummy_project(i, rng):
    title = f"{rng.choice(SUBJECTS)} {rng.choice(ACTIONS)} {i:04d}"
    tags = rng.sample(DOMAINS, rng.randint(1, 2)) + rng.sample(TECHNIQUES, rng.randint(1, 3))
    authors = [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in range(rng.randint(1, 4))]
    roll = rng.random()
    if roll < 0.7:
        thumbnail = f"https://picsum.photos/seed/geolab{i}/480/270"
    elif roll < 0.9:
        thumbnail = None
    else:
        thumbnail = f"https://example.invalid/missing-{i}.png"
    project = {
        "title": title,
        "author": authors,
        "github": f"https://github.com/example/project-{i:04d}",
        "summary": (
            f"This notebook {rng.choice(VERBS)} {tags[0]} data using "
            f"{' and '.join(tags[1:]) or 'standard tools'}. "
            + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * rng.randint(0, 3)
        ).strip(),
        "nbgitpuller": "https://geolab.earthscope.cloud/",
        "tags": tags,
    }
    if thumbnail:
        project["thumbnail"] = thumbnail
    return project


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--out", default=".dummy-projects")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out = ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for real in (ROOT / "projects").glob("*.y*ml"):
        shutil.copy(real, out / real.name)

    rng = random.Random(args.seed)
    for i in range(1, args.count + 1):
        path = out / f"dummy-{i:04d}.yml"
        path.write_text(yaml.safe_dump(dummy_project(i, rng), sort_keys=False), encoding="utf-8")
    print(f"Wrote {args.count} dummy projects (+ real ones) to {out.relative_to(ROOT)}/")
    print(f"Preview: GEOLAB_PROJECTS_DIR={args.out} myst start")


if __name__ == "__main__":
    main()
