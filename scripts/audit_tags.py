#!/usr/bin/env python3
"""List every tag in the library and suggest duplicates to consolidate.

    python scripts/audit_tags.py                  # tags in projects/
    python scripts/audit_tags.py --field author   # same checks for author names
    python scripts/audit_tags.py --dir .dummy-projects

Reports, in order:
  1. Variants: tags that differ only in case, spacing, or - _ separators
     (e.g. "earthscope_sdk" / "EarthScope SDK").
  2. Plurals: "earthquake" / "earthquakes".
  3. Similar: likely typos or near-duplicates (e.g. "seismolgy" / "seismology").
     These are fuzzy matches, so review them before merging.
  4. Singletons: tags used by only one project (often too specific, or a
     misspelling of a common tag).
  5. All tags with their counts.

For each group the suggested canonical spelling is the most used one,
preferring spaces over - and _. On a tie it says so: pick one yourself.
This script only reports; it never edits project files.
"""
import argparse
import difflib
import pathlib
import re
import sys
from collections import defaultdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load(directory, field):
    """Map each value of `field` to the project files that use it."""
    uses = defaultdict(list)
    for path in sorted(directory.glob("*.y*ml")):
        try:
            metadata = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as err:
            print(f"warning: skipping {path.name}: {err}", file=sys.stderr)
            continue
        values = metadata.get(field) or []
        for value in values if isinstance(values, list) else [values]:
            value = str(value).strip()
            if value:
                uses[value].append(path.name)
    return uses


def normalize(tag):
    """Lowercase, and treat spaces, hyphens, and underscores alike."""
    return re.sub(r"[\s_\-]+", " ", tag.lower()).strip()


def singular(word):
    """Crude English singular, good enough to pair tag plurals."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and re.search(r"(ss|sh|ch|x)es$", word):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def group_by(tags, key):
    """Groups of 2+ tags sharing key(tag)."""
    groups = defaultdict(list)
    for tag in tags:
        groups[key(tag)].append(tag)
    return [g for g in groups.values() if len(g) > 1]


def numbered(a, b):
    """True if a and b differ only in one short or numeric word ("Author 1" / "Author B")."""
    wa, wb = a.split(), b.split()
    diff = [(x, y) for x, y in zip(wa, wb) if x != y]
    return len(wa) == len(wb) and len(diff) == 1 and all(
        len(w) <= 1 or w.isdigit() for w in diff[0]
    )


def similar_pairs(tags, cutoff):
    """Pairs of distinct normalized tags that look alike (likely typos)."""
    pairs = []
    norms = sorted({normalize(t) for t in tags})
    for i, a in enumerate(norms):
        for b in norms[i + 1:]:
            # Skip pairs the plural check already reports, and very short
            # tags, where one letter changes the meaning ("GPS" / "GIS").
            if singular(a) == singular(b) or min(len(a), len(b)) < 5 or numbered(a, b):
                continue
            if difflib.SequenceMatcher(None, a, b).ratio() >= cutoff:
                pairs.append((a, b))
    return pairs


def rank(tag, uses):
    """Sort key: most used first, then plain single spaces rather than - _ or doubled spaces."""
    return (-len(uses[tag]), bool(re.search(r"[_\-]|\s\s", tag)), tag.lower())


def show_group(title, groups, uses):
    if not groups:
        return
    print(f"\n## {title} ({len(groups)})\n")
    for group in groups:
        ranked = sorted(group, key=lambda t: rank(t, uses))
        canonical = ranked[0]
        tie = rank(ranked[0], uses)[:2] == rank(ranked[1], uses)[:2]
        variants = ", ".join(f'"{t}" ({len(uses[t])})' for t in ranked)
        print(f'- {variants}  →  suggest "{canonical}"' + ("  (tie: pick one)" if tie else ""))
        for tag in ranked[1:]:
            print(f'    "{tag}" in: {", ".join(uses[tag])}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default="projects", help="folder of project YAML files (default: projects)")
    parser.add_argument("--field", default="tags", help="YAML field to audit (default: tags; try author)")
    parser.add_argument("--cutoff", type=float, default=0.85,
                        help="similarity 0-1 for the 'Similar' check (default: 0.85)")
    args = parser.parse_args()

    directory = ROOT / args.dir
    uses = load(directory, args.field)
    tags = list(uses)
    print(f"# {args.field} in {args.dir}/: {len(tags)} distinct, "
          f"{sum(map(len, uses.values()))} uses")

    variants = group_by(tags, normalize)
    show_group("Variants (case / spacing / separators)", variants, uses)

    # Plurals: group the variant-normalized forms, then expand back to tags.
    by_norm = defaultdict(list)
    for tag in tags:
        by_norm[normalize(tag)].append(tag)
    plural_groups = group_by(list(by_norm), lambda n: " ".join(map(singular, n.split())))
    show_group("Plurals", [[t for n in g for t in by_norm[n]] for g in plural_groups], uses)

    pairs = similar_pairs(tags, args.cutoff)
    similar = [by_norm[a] + by_norm[b] for a, b in pairs]
    show_group("Similar (possible typos, review before merging)", similar, uses)

    # Skip tags already flagged above, so this lists only new candidates.
    flagged = {t for g in variants + similar for t in g}
    flagged |= {t for g in plural_groups for n in g for t in by_norm[n]}
    singletons = sorted((t for t in tags if len(uses[t]) == 1 and t not in flagged), key=str.lower)
    if singletons:
        print(f"\n## Used once, not flagged above ({len(singletons)})\n")
        for tag in singletons:
            print(f'- "{tag}" in {uses[tag][0]}')

    print(f"\n## All {args.field} ({len(tags)})\n")
    for tag in sorted(tags, key=lambda t: (-len(uses[t]), t.lower())):
        print(f"{len(uses[tag]):5}  {tag}")


if __name__ == "__main__":
    main()
