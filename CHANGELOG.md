# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [UNRELEASED] - yyyy-mm-dd

### Added
- Add `Validation` section to the specification documenting cross-reference rules JSON Schema cannot express: unique attribute group `id`s and `name`s, `linkedGroups` resolution, `date` filter `end` not before `start`, and reserved Windows device names in `name`
- Add note requiring validators to enable JSON Schema format assertion, since draft 2020-12 treats `format` as annotation-only by default
- Add `scripts/validate_crtdl.py`, a reference validator implementing the schema plus the above rules, with `requirements.txt` for its dependencies
- Add `example-json/invalid/`, documents that each deliberately violate one validation rule, to demonstrate and exercise `scripts/validate_crtdl.py`
### Changed
- **Breaking:** `$id` changed from `.../ClinicalResourceTransferDefinitionLanguage/v1/schema` to `.../v2/schema`
- **Breaking:** `version` now requires a `2.x.y` release (`^2\.\d+\.\d+$`) instead of `1.x.y`
- **Breaking:** `dataExtraction.attributeGroups` now requires at least one entry (`minItems: 1`)
- **Breaking:** each attribute group's `attributes` now requires at least one entry (`minItems: 1`)
- **Breaking:** `id`, `groupReference`, and `attributeRef` now reject empty strings (`minLength: 1`)
### Deprecated
### Removed
### Fixed
### Security

## [1.0.0] - 2026-08-14

### Added
- Add CRTDL JSON schema (`json-schema/CRTDL_schema.json`), composing a CCDL `cohortDefinition` with a `dataExtraction` object
- Add `dataExtraction.attributeGroups` with `id`, machine-readable `name`, optional `display`, `groupReference`, `attributes` (`attributeRef`, `mustHave`), and optional `filter`
- Add attribute group linking via `linkedGroups` and reference-only groups via `includeReferenceOnly`
- Add `token` and `date` filter types
- Add example CRTDL JSON files (`example-json/`)
- Add GitHub Pages documentation site built with VitePress (`docs/`), with per-version documentation and a version switcher