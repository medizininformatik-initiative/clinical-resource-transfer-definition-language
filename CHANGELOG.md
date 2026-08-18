# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [UNRELEASED] - yyyy-mm-dd

### Added
- Add `Validation` section to the specification documenting cross-reference rules JSON Schema cannot express: unique attribute group `id`s and `name`s, `linkedGroups` resolution, `date` filter `end` not before `start`, and reserved Windows device names in `name`
- Add note requiring validators to enable JSON Schema format assertion, since draft 2020-12 treats `format` as annotation-only by default
- Add `scripts/validate_crtdl.py`, a reference validator implementing the schema plus the above rules, with `requirements.txt` for its dependencies
- Add `example-json/invalid/`, documents that each deliberately violate one validation rule, to demonstrate and exercise `scripts/validate_crtdl.py`
- Add CI workflow running `scripts/validate_crtdl.py` against `example-json/*.json` (must pass) and `example-json/invalid/*.json` (each must fail)
### Changed
- **Breaking:** `$id` changed from `.../ClinicalResourceTransferDefinitionLanguage/v1/schema` to `.../v2/schema`
- **Breaking:** `version` now requires a `2.x.y` release (`^2\.\d+\.\d+$`) instead of `1.x.y`
- **Breaking:** `dataExtraction.attributeGroups` now requires at least one entry (`minItems: 1`)
- **Breaking:** each attribute group's `attributes` now requires at least one entry (`minItems: 1`)
- **Breaking:** `id`, `groupReference`, and `attributeRef` now reject empty strings (`minLength: 1`)
### Deprecated
### Removed
### Fixed
- Fix `example-json/*.json` setting `cohortDefinition.version` to `2.0.0` instead of the CCDL-required const `2`, which made the examples fail schema validation
- Fix `scripts/validate_crtdl.py` fetching the CCDL schema from the `main` branch (an unpinned, moving target); pin to a commit instead
- Fix `scripts/validate_crtdl.py`'s `retrieve()` ignoring the requested `$ref` URI and always returning the CCDL schema, which would silently resolve any future unrelated `$ref` to the wrong schema instead of failing
- Fix `scripts/validate_crtdl.py` comparing attribute group `name`s and checking for Windows-reserved names on the raw string instead of the [slugified](docs/documentation.md#slugification) form, as `docs/documentation.md` documents; two names that only differ after slugification (e.g. `"Con!"` vs. `"con"`) previously went undetected
- Fix `example-json/invalid/CRTDL_invalid_example.json` carrying a stray `display` field per attribute group (removed from the schema earlier), which made every group in that fixture additionally fail on `additionalProperties` and obscured the one intentional violation per group; labeling now uses each group's `id` instead, matching the docs
- Fix `docs/documentation.md`'s Validation section describing attribute group `name` uniqueness and the reserved-device-name check without mentioning slugification, contradicting the more precise "Uniqueness comparison" and "Slugification" sections
- Fix `docs/documentation.md`'s embedded full example setting `cohortDefinition.version` to `2.0.0` instead of `2`
### Security

## [1.0.0] - 2026-08-14

### Added
- Add CRTDL JSON schema (`json-schema/CRTDL_schema.json`), composing a CCDL `cohortDefinition` with a `dataExtraction` object
- Add `dataExtraction.attributeGroups` with `id`, machine-readable `name`, optional `display`, `groupReference`, `attributes` (`attributeRef`, `mustHave`), and optional `filter`
- Add attribute group linking via `linkedGroups` and reference-only groups via `includeReferenceOnly`
- Add `token` and `date` filter types
- Add example CRTDL JSON files (`example-json/`)
- Add GitHub Pages documentation site built with VitePress (`docs/`), with per-version documentation and a version switcher