# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-09-13

### Added
- `automatic_refresh` keyword argument for [`build_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.build_client) and [`build_async_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.build_async_client) accepting a boolean, which configures the underlying [`authlib` OAuth 2.0 client](https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html) to automatically refresh when the token expires.

### Changed
- [`Client.refresh_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.client.Client.refresh_token) and [`AsyncClient.refresh_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.async_client.AsyncClient.refresh_token) propagates the return value of [`TokenManager.update_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.token_manager.TokenManager.update_token), which propagates the return value of a custom `token_write_func`.

- [`TokenManager.update_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.token_manager.TokenManager.update_token) propagates the return value of `token_write_func`, so that a custom `token_write_func` can return values back to the caller.

## [1.2.0] - 2026-09-09

### Added
- [`BaseClient.get_firm_renewal()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_firm_renewal) query method to support the new registration dataset.

- [`extract_expires_isoformat()`](https://finra.hawkberry.com/en/latest/reference.html#finra.utils.extract_expires_isoformat) to extract expiration datetimes that are in ISO format from the body of a response object.

- [`extract_request_timestamp_dt()`](https://finra.hawkberry.com/en/latest/reference.html#finra.utils.extract_request_timestamp_dt) to extract the request timestamp from the body of a response object and return it as a `datetime.datetime` object.

## [1.1.0] - 2026-09-02

### Added
- [`BaseClient.get_finpro_tasks()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_finpro_tasks) query method to support the new registration dataset.

- [`Validator.is_valid()`](https://finra.hawkberry.com/en/latest/reference.html#finra.filings.validator.Validator.is_valid) method which returns a boolean indicating validation status.

### Changed
- [`Validator.validate()`](https://finra.hawkberry.com/en/latest/reference.html#finra.filings.validator.Validator.validate) method signature to explicitly match the underlying `jsonschemajsonschema.protocols.Validator.validate` method signature

## [1.0.2] - 2026-08-19
- effectively the initial release for major version 1, stable

## [1.0.1] - 2026-08-18 [YANKED]
- yanked due a publishing error

## [1.0.0] - 2026-08-17 [YANKED]
- yanked due a publishing error
