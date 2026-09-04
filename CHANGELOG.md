# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [1.1.0] - 2026-09-02

### Added
- added BaseClient.get_finpro_tasks query method to support the new Query API dataset
- added Validator.is_valid method which returns a boolean indicating validation status

### Changed
- updated Validator.validate method signature to explicitly match the underlying jsonschema.protocols.Validator.validate method signature

## [1.0.2] - 2026-08-19

- effectively the initial release for version 1, stable

## [1.0.1] - 2026-08-18 [YANKED]

## [1.0.0] - 2026-08-17 [YANKED]

- yanked due a publishing error
