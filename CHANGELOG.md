# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [UNRELEASED] - yyyy-mm-dd

### Added
- Add CRTDL JSON schema (`json-schema/CRTDL_schema.json`), composing a CCDL `cohortDefinition` with a `dataExtraction` object
- Add `dataExtraction.attributeGroups` with `id`, a human-readable `name` (unique after slugification), `groupReference`, `attributes` (`attributeRef`, `mustHave`), and an optional `filter`
- Add attribute group linking via `linkedGroups` and reference-only groups via `includeReferenceOnly`
- Add `token` and `date` filter types
- Add example CRTDL JSON files (`example-json/`)
- Add GitHub Pages documentation site built with VitePress (`docs/`), with per-version documentation and a version switcher
- Add `Validation` section to the specification documenting cross-reference rules JSON Schema cannot express: unique attribute group `id`s, attribute group `name`s unique after slugification, resolvable `linkedGroups` references, `date` filter `end` not before `start`, and attribute group names that don't slugify to a reserved Windows device name
- Add note requiring validators to enable JSON Schema format assertion, since draft 2020-12 treats `format` as annotation-only by default
- Add `scripts/validate_crtdl.py`, a reference validator implementing the schema plus the above rules (resolving the CCDL schema from a pinned commit, with strict `$ref` resolution and slugification-aware name checks), with `requirements.txt` for its dependencies
- Add `example-json/invalid/`, documents (labeled by each group's `id`) that each deliberately violate one validation rule, to demonstrate and exercise `scripts/validate_crtdl.py`
- Add CI workflow running `scripts/validate_crtdl.py` against `example-json/*.json` (must pass) and `example-json/invalid/*.json` (each must fail)
### Changed
- **Breaking:** `version` is now a fixed const `"1"` instead of the URI-format string used in `v0.1.0`, matching CCDL's own versioning
- **Breaking:** `dataExtraction.attributeGroups` now requires at least one entry (`minItems: 1`)
- **Breaking:** each attribute group's `attributes` now requires at least one entry (`minItems: 1`)
- **Breaking:** `id`, `groupReference`, and `attributeRef` now reject empty strings (`minLength: 1`)
### Deprecated
### Removed
### Fixed
### Security

## [0.1.0] - 2025-07-17

Tagged retroactively to give the schema shape already distributed to production before formal versioning existed a citable anchor. `$id` was a placeholder (`http://example.com/schema/data-extraction-schema.json`) and `version` was typed as a bare URI-format string rather than a real version identifier; both are formalized starting in the next release.

### Added
- Add CRTDL JSON schema (`json-schema/CRTDL_schema.json`) and example CRTDL JSON files (`example-json/`)
