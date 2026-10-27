#!/usr/bin/env python3
"""GeoLab Library: fills the {geolab-library} gallery with project data.

The {geolab-library} directive (plugins/geolab-library.mjs) emits an anywidget
node whose model has `source: geolab`. This document-stage transform sets that
model's `items` to one entry per project YAML file; the widget renders them.

Projects are read from projects/, or from the folder in $GEOLAB_PROJECTS_DIR
(used to preview dummy data, see scripts/make_dummy_projects.py).
"""
import argparse
import json
import os
import pathlib
import re
import sys

import yaml

WIDGET = "anywidget"  # node type emitted by {geolab-library}
HERE = pathlib.Path(__file__).resolve().parent
# Relative to this file, not the current directory.
PROJECTS = HERE / os.environ.get("GEOLAB_PROJECTS_DIR", "projects")

# PROJECTS = "/Users/sarahwilson/Code/geolab-library/.dummy_projects"
# print(PROJECTS)


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def thumbnail_url(metadata):
    """An absolute thumbnail URL, or None.

    Absolute URLs pass through; a relative path is resolved against the
    project's GitHub repo (default branch) like the template describes.
    """
    thumb = metadata.get("thumbnail")
    if not thumb:
        return None
    if re.match(r"https?://", thumb):
        return thumb
    match = re.match(r"https?://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$", metadata.get("github") or "")
    if not match:
        return None
    return f"https://raw.githubusercontent.com/{match.group(1)}/HEAD/{thumb.lstrip('/')}"


def collect_project(path):
    """One project file as a gallery item (or None if unreadable)."""
    try:
        metadata = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as err:
        print(f"Skipping {path.name}: {err}", file=sys.stderr)
        return None
    item = {
        "title": metadata.get("title") or path.stem,
        "description": metadata.get("summary"),
        "authors": [str(a) for a in as_list(metadata.get("author"))],
        "tags": [str(t) for t in as_list(metadata.get("tags"))],
        "types": [str(t) for t in as_list(metadata.get("type"))],
        "thumbnail": thumbnail_url(metadata),
        "url": metadata.get("nbgitpuller") or metadata.get("github"),
        "github": metadata.get("github"),
    }
    return {key: value for key, value in item.items() if value}


def collect_projects():
    paths = sorted(p for p in PROJECTS.iterdir() if p.suffix in (".yml", ".yaml"))
    return [item for item in map(collect_project, paths) if item is not None]


def find_all_by_type(parent, type_):
    for node in parent.get("children", []):
        if node.get("type") == type_:
            yield node
        yield from find_all_by_type(node, type_)


def run_transform(data):
    nodes = [
        node
        for node in find_all_by_type(data, WIDGET)
        if (node.get("model") or {}).get("source") == "geolab"
    ]
    if nodes:
        items = collect_projects()
        for node in nodes:
            node["model"]["items"] = items
    return data


PLUGIN_SPEC = {
    "name": "GeoLab Library",
    "transforms": [{"stage": "document"}],
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transform")
    args = parser.parse_args()

    if args.transform:
        json.dump(run_transform(json.load(sys.stdin)), sys.stdout)
    else:
        json.dump(PLUGIN_SPEC, sys.stdout)
