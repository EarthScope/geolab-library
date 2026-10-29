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
TYPES = ["notebook", "image"]
LOREM = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Curabitur pretium tincidunt lacus, nulla gravida orci a odio.",
    "Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris.",
    "Integer in mauris eu nibh euismod gravida.",
    "Duis ac tellus et risus vulputate vehicula.",
    "Donec lobortis risus a elit, etiam tempor ut ullamcorper ligula eu tempor congue.",
    "Praesent dapibus, neque id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros eu erat.",
    "Aliquam erat volutpat, nam dui mi, tincidunt quis, accumsan porttitor, facilisis luctus, metus.",
]
INSTITUTIONS = ["EarthScope Consortium", "University of Example", "Example Institute of Geophysics",
                "Placeholder State University", "Sample Polytechnic"]
IMAGES = ["geolab_default", "jupyter/scipy-notebook", "pangeo/pangeo-notebook"]
RESOURCES = ["2GB", "4GB", "8GB", "16GB"]
DIFFICULTIES = ["beginner", "intermediate", "advanced", "expert"]
TIME_COMMITMENTS = ["5 minutes", "15 minutes", "30 minutes", "1 hour", "2 hours", "half a day"]


def dummy_project(i, rng):
    title = f"{rng.choice(SUBJECTS)} {rng.choice(ACTIONS)} {i:04d}"
    tags = rng.sample(DOMAINS, rng.randint(1, 2)) + rng.sample(TECHNIQUES, rng.randint(1, 3))
    authors = [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in range(rng.randint(1, 4))]
    roll = rng.random()
    type = rng.sample(TYPES, rng.randint(1,2))
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
        "summary": dummy_summary(tags, rng),
        "nbgitpuller": "https://geolab.earthscope.cloud/",
        "tags": tags,
        "type": type
    }
    if thumbnail:
        project["thumbnail"] = thumbnail
    # Leave each detail field out now and then, so the pop-out's empty-field handling gets tested.
    first, last = authors[0].lower().split()
    if rng.random() < 0.9:
        project["maintainer contact"] = f"{first}.{last}@example.org"
    if rng.random() < 0.8:
        project["author_institution"] = rng.choice(INSTITUTIONS)
    if rng.random() < 0.8:
        project["recommended_image"] = rng.choice(IMAGES)
    if rng.random() < 0.8:
        project["recommended_resource_allocation"] = rng.choice(RESOURCES)
    if rng.random() < 0.85:
        project["citation"] = dummy_citation(i, title, authors, rng)
    if rng.random() < 0.8:
        project["difficulty"] = rng.choice(DIFFICULTIES)
    if rng.random() < 0.8:
        project["time_commitment"] = rng.choice(TIME_COMMITMENTS)
    return project


def dummy_summary(tags, rng):
    """One plain sentence, then 0-3 paragraphs of Latin, so some summaries fit the card and some overflow it."""
    intro = (f"This notebook {rng.choice(VERBS)} {tags[0]} data using "
             f"{' and '.join(tags[1:]) or 'standard tools'}.")
    paragraphs = [" ".join(rng.sample(LOREM, rng.randint(2, 6))) for _ in range(rng.choice([0, 1, 1, 2, 3]))]
    if paragraphs:
        paragraphs[0] = f"{intro} {paragraphs[0]}"
        return "\n\n".join(paragraphs)
    return intro


def dummy_citation(i, title, authors, rng):
    """APA-ish citation; DOI prefix 10.5555 is reserved for examples."""
    names = [f"{a.split()[1]}, {a.split()[0][0]}." for a in authors]
    names = names[0] if len(names) == 1 else ", ".join(names[:-1]) + f", & {names[-1]}"
    return f"{names} ({rng.randint(2018, 2026)}). {title}. GeoLab Library. https://doi.org/10.5555/geolab.{i:04d}"


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
