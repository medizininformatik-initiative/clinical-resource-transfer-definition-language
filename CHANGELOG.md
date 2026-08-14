# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [UNRELEASED] - yyyy-mm-dd

### Added
### Changed
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