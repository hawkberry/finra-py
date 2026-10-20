# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - Unreleased

### Added
- [`Software Bill of Materials`](https://github.com/hawkberry/finra-py/tree/main/.sbom) files describing the PyPI package contents for each published release.

- Architectural Decision Records:

	* [`ADR 0002 - Authentication and Token Management`](https://github.com/hawkberry/finra-py/tree/main/docs/adr/0002-authentication-token-management.md)

	* [`ADR 0003 - Enum-Based Representation of FINRA API Values`](https://github.com/hawkberry/finra-py/tree/main/docs/adr/0003-enum-based-representation-finra-api-values.md)

	* [`ADR 0004 - Client-Side Submission Validation`](https://github.com/hawkberry/finra-py/tree/main/docs/adr/0004-client-side-submission-validation.md)

	* [`ADR 0005 - Diagnostic Logging and Log Redaction`](https://github.com/hawkberry/finra-py/tree/main/docs/adr/0005-diagnostic-logging-redaction.md)

- [`register_redactions_from_response()`](https://finra.hawkberry.com/en/latest/reference.html#finra.log_redactor.register_redactions_from_response) now identifies Form U4 and U5 free-text values matching the `warnOn` regex patterns defined in [`Submission Warnings`](https://developer.finra.org/docs#submission_api-api_basics-submission_warning) for diagnostic log redaction.

- When bug-report logging is enabled, [`register_redactions_from_response()`](https://finra.hawkberry.com/en/latest/reference.html#finra.log_redactor.register_redactions_from_response) now logs a warning if `httpx.Response.json()` fails to decode the response, preventing its contents from being inspected for redaction.

### Changed
- [`SECURITY.md`](https://github.com/hawkberry/finra-py/blob/main/SECURITY.md) now provides a single point of review for security and procurement purposes.

- [`BaseClient.get_async_request_status()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_async_request_status) and [`BaseClient.get_async_result()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_async_result) now restrict URL locations to approved hosts. Requests must use HTTPS and must not contain embedded credentials. This should not affect normal usage, so it is being introduced as a security patch.

- [`Validator`](https://finra.hawkberry.com/en/latest/reference.html#finra.filings.validator.Validator) now restricts schema retrieval to approved hosts over HTTPS and rejects URLs containing embedded credentials. Redirect destinations are subject to the same validation before a subsequent request is made.

- The `api_key` argument to [`BaseClient`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient) is deprecated and will be removed in version 2.0. It is unused by `BaseClient` and retained solely for backward compatibility.

- Errors logged by [`BaseClient`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient) are now passed through the [`base_client`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client) module logger instead of `logging.error`, allowing redaction if enabled.

- Setting the log level to `DEBUG` on the [`base_client`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client) module logger or an ancestor now enables ordinary request/response logging independently of the opt-in bug-report logging facility. Ordinary logging does not receive the bug-report facility's log redaction.

- Redaction registration is now enabled only when [`enable_bug_report_logging()`](https://finra.hawkberry.com/en/latest/reference.html#finra.debug.enable_bug_report_logging) has been called, preventing unnecessary registry growth during ordinary logging.

- Fixed the [`log_redactor`](https://finra.hawkberry.com/en/latest/reference.html#finra.log_redactor) module's default bad patterns to be case-insensitive for all patterns.

## [1.3.0] - 2026-09-30

### Added
- FINRA API Changelog page and RSS feed are now live and available in the [`finra-py` documentation](https://finra.hawkberry.com/en/latest/finra-changelog.html). These services are intended to help developers track API drift and better understand and implement FINRA API integrations.

- [`BaseClient.get_trace_sovereign_debt_summary()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_sovereign_debt_summary) query method to support the new TRACE Report Card dataset.

- [`BaseClient.get_trace_treasuries_execution_time_difference_summary()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_treasuries_execution_time_difference_summary) query method to support the new TRACE Report Card dataset.

- New query parameter support for the following TRACE Report Card datasets via the `report_view` keyword argument:

	* [`BaseClient.get_trace_agency_debt_details()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_agency_debt_details)

	* [`BaseClient.get_trace_agency_debt_summary()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_agency_debt_summary)

	* [`BaseClient.get_trace_corporate_bonds_details()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_corporate_bonds_details)

	* [`BaseClient.get_trace_corporate_bonds_summary()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_corporate_bonds_summary)

	* [`BaseClient.get_trace_securitized_products_details()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_securitized_products_details)

	* [`BaseClient.get_trace_securitized_products_summary()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_trace_securitized_products_summary)

- [`get_async_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.get_async_client) is an asynchronous version of [`get_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.get_client). It supports (but does not require) asynchronous `token_read_func` and `token_write_func` callbacks. It only returns [`AsyncClient`](https://finra.hawkberry.com/en/latest/reference.html#finra.async_client.AsyncClient).

- [`async_client_from_new_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.async_client_from_new_token) is an asynchronous version of [`client_from_new_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.client_from_new_token). It supports (but does not require) an asynchronous `token_write_func` callback. It only returns [`AsyncClient`](https://finra.hawkberry.com/en/latest/reference.html#finra.async_client.AsyncClient). It also uses an [`AsyncOAuth2Client`](https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html#async-oauth-2-0) for the initial token fetch, so it won't block other coroutines.

- [`async_client_from_storage_functions()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.async_client_from_storage_functions) is an asynchronous version of [`client_from_storage_functions()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.client_from_storage_functions). It supports (but does not require) an asynchronous `token_read_func` callback. It only returns [`AsyncClient`](https://finra.hawkberry.com/en/latest/reference.html#finra.async_client.AsyncClient).

## [1.2.1] - 2026-09-13

### Added
- `automatic_refresh` keyword argument for [`build_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.build_client) and [`build_async_client()`](https://finra.hawkberry.com/en/latest/reference.html#finra.auth.build_async_client) accepting a boolean, which configures the underlying [`authlib` OAuth 2.0 client](https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html) to automatically refresh when the token expires.

### Changed
- [`Client.refresh_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.client.Client.refresh_token) and [`AsyncClient.refresh_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.async_client.AsyncClient.refresh_token) propagate the return value of [`TokenManager.update_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.token_manager.TokenManager.update_token), which propagates the return value of a custom `token_write_func`.

- [`TokenManager.update_token()`](https://finra.hawkberry.com/en/latest/reference.html#finra.token_manager.TokenManager.update_token) propagates the return value of `token_write_func`, so that a custom `token_write_func` can return values back to the caller.

## [1.2.0] - 2026-09-09

### Added
- Architectural Decision Records:

  * [`ADR 0001 - Client Architecture and HTTP Response Boundary`](https://github.com/hawkberry/finra-py/tree/main/docs/adr/0001-client-architecture-http-boundary.md)

- [`BaseClient.get_firm_renewal()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_firm_renewal) query method to support the new Registration dataset.

- [`extract_expires_isoformat()`](https://finra.hawkberry.com/en/latest/reference.html#finra.utils.extract_expires_isoformat) to extract expiration datetimes that are in ISO format from the body of a response object.

- [`extract_request_timestamp_dt()`](https://finra.hawkberry.com/en/latest/reference.html#finra.utils.extract_request_timestamp_dt) to extract the request timestamp from the body of a response object and return it as a `datetime.datetime` object.

## [1.1.0] - 2026-09-02

### Added
- [`BaseClient.get_finpro_tasks()`](https://finra.hawkberry.com/en/latest/reference.html#finra.base_client.BaseClient.get_finpro_tasks) query method to support the new Registration dataset.

- [`Validator.is_valid()`](https://finra.hawkberry.com/en/latest/reference.html#finra.filings.validator.Validator.is_valid) method which returns a boolean indicating validation status.

### Changed
- [`Validator.validate()`](https://finra.hawkberry.com/en/latest/reference.html#finra.filings.validator.Validator.validate) method signature to explicitly match the underlying [`jsonschema.protocols.Validator.validate()`](https://python-jsonschema.readthedocs.io/en/stable/validate/#the-validator-protocol) method signature.

## [1.0.2] - 2026-08-19
- Effectively the initial release for major version 1, stable.

## [1.0.1] - 2026-08-18 [YANKED]
- Yanked due to a publishing error.

## [1.0.0] - 2026-08-17 [YANKED]
- Yanked due to a publishing error.
