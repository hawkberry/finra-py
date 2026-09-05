# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- BaseClient.get_firm_renewal query method to support the new registration dataset
- utils.extract_expires_isoformat to extract expiration datetimes that are in ISO format from the body of a response object
- utils.extract_request_timestamp_dt to extract the request timestamp from the body of a response object and return it as a datetime.datetime object

## [1.1.0] - 2026-09-02

### Added
- BaseClient.get_finpro_tasks query method to support the new registration dataset
- Validator.is_valid method which returns a boolean indicating validation status

### Changed
- Validator.validate method signature to explicitly match the underlying jsonschema validator.validate method signature

## [1.0.2] - 2026-08-19
- effectively the initial release for version 1, stable

## [1.0.1] - 2026-08-18 [YANKED]

## [1.0.0] - 2026-08-17 [YANKED]
- yanked due a publishing error
