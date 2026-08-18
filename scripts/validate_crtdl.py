#!/usr/bin/env python3
"""Validate CRTDL documents.

Runs two passes:
1. JSON Schema validation against json-schema/CRTDL_schema.json (with the
   referenced CCDL schema resolved, and format assertion enabled).
2. The cross-reference rules the schema cannot express (see the
   "Validation" section in docs/documentation.md): unique attribute group
   ids, attribute group names unique after slugification, resolvable
   linkedGroups references, non-reversed date filter ranges, and
   attribute group names that don't slugify to a reserved Windows device
   name.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.exceptions import Unretrievable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = REPO_ROOT / "json-schema" / "CRTDL_schema.json"

# The $id the CRTDL schema's $ref points to (see CRTDL_schema.json).
CCDL_SCHEMA_ID = "https://medizininformatik-initiative.de/fdpg/ClinicalCohortDefinitionLanguage/v2/schema"

# That $id isn't a fetchable URL, so we resolve it against the published
# source instead. Pinned to a commit rather than main so results don't
# change just because CCDL's main branch moves; bump it deliberately when
# CCDL v2 is tagged/released. Override with --ccdl-schema to validate
# against a local checkout instead.
CCDL_SCHEMA_FALLBACK_URL = (
    "https://raw.githubusercontent.com/medizininformatik-initiative/"
    "clinical-cohort-definition-language/"
    "5933fc8ce849f72e9e6bfa5dedafc686d392f2ca/json-schema/"
    "clinical-cohort-definition-language-schema.json"
)

WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}

# Matches docs/documentation.md's "Slugification of attributeGroup names".
GERMAN_TRANSLITERATIONS = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}


def slugify(name: str) -> str:
    value = name.strip().lower()
    for src, dst in GERMAN_TRANSLITERATIONS.items():
        value = value.replace(src, dst)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_validator(
    crtdl_schema_path: Path, ccdl_schema_path: Optional[Path]
) -> Draft202012Validator:
    schema = load_json(crtdl_schema_path)

    def retrieve(uri: str) -> Resource:
        if uri != CCDL_SCHEMA_ID:
            raise Unretrievable(uri)
        if ccdl_schema_path is not None:
            return Resource.from_contents(load_json(ccdl_schema_path))
        with urllib.request.urlopen(CCDL_SCHEMA_FALLBACK_URL) as response:
            return Resource.from_contents(json.load(response))

    registry = Registry(retrieve=retrieve)
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def check_schema(instance: dict, validator: Draft202012Validator) -> list[str]:
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(map(str, e.path)))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


def _duplicates(values: Iterable[Any]) -> set[Any]:
    seen: set[Any] = set()
    dupes: set[Any] = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    return dupes


def check_semantics(instance: dict) -> list[str]:
    problems: list[str] = []
    groups = instance.get("dataExtraction", {}).get("attributeGroups")
    if not isinstance(groups, list):
        return problems

    ids = [g["id"] for g in groups if isinstance(g, dict) and isinstance(g.get("id"), str)]
    names = [g["name"] for g in groups if isinstance(g, dict) and isinstance(g.get("name"), str)]
    slugs = [slugify(name) for name in names]

    for dup in _duplicates(ids):
        problems.append(f"duplicate attributeGroup id: {dup!r}")
    for dup_slug in _duplicates(slugs):
        conflicting = [name for name, slug in zip(names, slugs) if slug == dup_slug]
        problems.append(
            f"duplicate attributeGroup name after slugification: {dup_slug!r} "
            f"(from {', '.join(map(repr, conflicting))})"
        )
    for name, slug in zip(names, slugs):
        if slug in WINDOWS_RESERVED_NAMES:
            problems.append(
                f"attributeGroup name slugifies to a Windows reserved name: {name!r} -> {slug!r}"
            )

    known_ids = set(ids)
    for group in groups:
        if not isinstance(group, dict):
            continue
        group_id = group.get("id", "<unknown>")

        for attribute in group.get("attributes") or []:
            if not isinstance(attribute, dict):
                continue
            for linked in attribute.get("linkedGroups") or []:
                if linked not in known_ids:
                    problems.append(
                        f"attributeGroup {group_id!r}: linkedGroups entry {linked!r} "
                        "does not resolve to any attributeGroup id"
                    )

        for filter_ in group.get("filter") or []:
            if not isinstance(filter_, dict) or filter_.get("type") != "date":
                continue
            start, end = filter_.get("start"), filter_.get("end")
            if not start or not end:
                continue
            try:
                start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
            except ValueError:
                continue  # malformed dates are caught by schema format assertion
            if end_date < start_date:
                problems.append(
                    f"attributeGroup {group_id!r}: date filter end ({end}) is before start ({start})"
                )

    return problems


def validate_file(path: Path, validator: Draft202012Validator) -> list[str]:
    instance = load_json(path)
    return check_schema(instance, validator) + check_semantics(instance)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="CRTDL JSON files to validate")
    parser.add_argument(
        "--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to CRTDL_schema.json"
    )
    parser.add_argument(
        "--ccdl-schema",
        type=Path,
        default=None,
        help="Local path to the CCDL schema (skips fetching it from GitHub)",
    )
    args = parser.parse_args(argv)

    validator = build_validator(args.schema, args.ccdl_schema)

    exit_code = 0
    for path in args.files:
        problems = validate_file(path, validator)
        if problems:
            exit_code = 1
            print(f"FAIL {path}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"OK   {path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
