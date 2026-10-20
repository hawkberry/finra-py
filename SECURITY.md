# Security Policy for `finra-py`

## Overview

| Policy Area | Evidence |
| --- | --- |
| Supported versions and metadata | [`pyproject.toml`](https://github.com/hawkberry/finra-py/blob/main/pyproject.toml) |
| Dependency and supply-chain | [Dependabot](https://docs.github.com/code-security/dependabot); [Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review); [CodeQL](https://github.com/apps/github-advanced-security) |
| Published artifacts and provenance | [PyPI Attestations](https://pypi.org/project/finra-py/#files) |
| Source inventory and file integrity | [Release SBOMs](https://github.com/hawkberry/finra-py/tree/main/.sbom) |
| License and change history | [LICENSE](https://github.com/hawkberry/finra-py/blob/main/LICENSE); [CHANGELOG](https://github.com/hawkberry/finra-py/blob/main/CHANGELOG.md) |
| Application and network boundary | [ADR 0001](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0001-client-architecture-http-boundary.md) |
| Authentication and token storage | [ADR 0002](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0002-authentication-token-management.md); [Authentication and Client Creation](https://finra.hawkberry.com/en/latest/auth.html) |
| Client-side submission validation | [ADR 0004](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0004-client-side-submission-validation.md) |
| Diagnostic logging and redaction | [ADR 0005](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0005-diagnostic-logging-redaction.md); [Getting Help — Bug Reporting](https://finra.hawkberry.com/en/latest/help.html#bug-reporting) |
| Vulnerability reporting | [GitHub Private Vulnerability Reporting](https://github.com/hawkberry/finra-py/security) |

## Supported Versions

This policy applies to the latest released version of `finra-py` and its direct runtime dependencies: (1) `authlib`, (2) `httpx`, (3) `jsonschema`, and (4) `tzdata` (Windows only). Supported dependency ranges are defined by [`pyproject.toml`](https://github.com/hawkberry/finra-py/blob/main/pyproject.toml).

Security fixes are provided for the latest version only. Older releases are not currently maintained as separate security-support branches. Breaking changes, deprecations, removals, and security-related dependency changes are documented through the release and [CHANGELOG](https://github.com/hawkberry/finra-py/blob/main/CHANGELOG.md) where applicable.

## Dependency and Supply-Chain

Dependency vulnerability is monitored through GitHub’s dependency graph and [Dependabot](https://docs.github.com/code-security/dependabot) alerts. As part of the automated CI workflow, [Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review) checks dependency changes introduced through pull requests, and CI audits the resolved dependency set on pushes and pull requests. A dependency security issue may result in a `finra-py` release that changes only dependency minimums when that is sufficient to exclude an affected version.

Repository security checks include GitHub [CodeQL](https://github.com/apps/github-advanced-security) and secret scanning with push protection. These controls support the `finra-py` development process but do not replace an application's own security testing or risk assessment.

## Provenance and File Integrity

Release distributions are built from tagged repository state and published to PyPI using Trusted Publishing. [PyPI Attestations](https://pypi.org/project/finra-py/#files) provide cryptographic proof of provenance through verifiable records for each published release.

Each release also includes a versioned CycloneDX JSON SBOM in the [`.sbom/` directory](https://github.com/hawkberry/finra-py/tree/main/.sbom). The SBOM provides a machine-readable inventory of source files and dependencies, with SHA-256 hashes of the source files it inventories.

## Application and Network Boundary

`finra-py` is an open-source Python client library that runs in the calling application's process. It sends requests directly to the FINRA API Platform and related resources, and returns standard `httpx.Response` object directly to the application.

Asynchronous status/result URLs and JSON schema retrieval are restricted to approved hosts over HTTPS, and embedded credentials are rejected. For JSON schema URLs, these constraints are applied to redirects. For FINRA API and related resource URLs, redirect following is disabled entirely. These restrictions reduce the risk of exposing access tokens to unintended hosts.

Optional client-side validation checks filing data against the FINRA API's published JSON Schemas before submission, but does not replace the API's server-side validation.

`finra-py` does not pass requests through a service operated by the project maintainer. `finra-py` does not remotely store application or API data, or collect telemetry, analytics, advertising, or usage data.

See [ADR 0001 — Client Architecture and HTTP Response Boundary](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0001-client-architecture-http-boundary.md) and [ADR 0004 — Client-Side Submission Validation](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0004-client-side-submission-validation.md).

## Authentication and Token Storage

`finra-py` uses Authlib's HTTPX integration for OAuth 2.0 authentication. API credentials are passed to the underlying OAuth2 client, and access tokens are managed by the token manager.

By default, the token manager writes token state and metadata to the file at `token_path`, which contains ordinary JSON and is not encrypted by `finra-py`. Applications can instead provide custom functions to read and write tokens using other storage systems.

See [ADR 0002 — Authentication and Token Management](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0002-authentication-token-management.md) and [Authentication and Client Creation](https://finra.hawkberry.com/en/latest/auth.html).

## Sensitive Data

| Data | `finra-py` handling | Library-managed persistence |
| --- | --- | --- |
| API key and API secret | Passed to the underlying OAuth2 client | None |
| OAuth token data | Managed by the token manager | `token_path`, or application-provided callbacks |
| Request parameters and payloads | Constructed and sent by the client | None |
| API responses | Returned as `httpx.Response` objects | None |
| Asynchronous result data | Retrieved and returned by the client | None |
| JSON Schema resources | Retrieved for client-side validation | In-memory schema registry only |
| Diagnostic log data | Optional best-effort logging redaction | Depends on the configured logging output |

## Diagnostic Logging

Diagnostic logging is optional and intended for troubleshooting. The dedicated bug-report logging facility provides **best-effort** redaction for diagnostic output intended for review and sharing. Redaction is not guaranteed, so logs should be reviewed before they are shared. Response-content redaction is only applied to response content that can be decoded as JSON. Redaction is not intended for production use due to increased performance overhead.

Ordinary Python logging follows the application's logging configuration, and does not use the dedicated bug-report logging facility to redact sensitive data.

See [ADR 0005 — Diagnostic Logging and Log Redaction](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0005-diagnostic-logging-redaction.md) and [Getting Help — Bug Reporting](https://finra.hawkberry.com/en/latest/help.html#bug-reporting).

## Application Responsibilities

The application remains responsible for protecting its credentials, tokens, data, and diagnostic logs, and for the security of the environment in which `finra-py` runs. These responsibilities include, but are not limited to:

- **Credentials and tokens:** Storage, access control, and encryption of API credentials and OAuth tokens, including custom token-storage functions and the systems they access. The default token file is not encrypted by `finra-py`.

- **API environment separation:** Credentials and token storage for production, Mock, and QA Test environments.

- **Response and data handling:** Processing HTTP responses, classifying application data, and controlling access, retention, and deletion of data stored, cached, backed up, or passed to other systems.

- **Diagnostic logging:** Logging configuration and destinations, and the protection of sensitive information in logs. Bug-report logging provides best-effort redaction, which does not guarantee that sensitive information is classified correctly or redacted.

- **Application security controls:** Network, endpoint, identity, access-control, monitoring, and incident-response controls for the application and its operating environment.

These responsibilities are outside the security boundary of `finra-py`.

## Reporting a Vulnerability

Please do not report suspected security vulnerabilities through a public GitHub issue. Use GitHub's [Private Vulnerability Reporting](https://github.com/hawkberry/finra-py/security) to report a suspected vulnerability. If private reporting is unavailable, use the contact address published on the [PyPI project page](https://pypi.org/project/finra-py/).

Reports are reviewed to determine validity, severity, affected versions, and appropriate remediation or disclosure steps. The expected response process is:

1. Receive and acknowledge the report
2. Assess validity and security impact
3. Determine affected versions and remediation requirements
4. Develop and test an appropriate fix
5. Release the remediation through the normal release process
6. Coordinate appropriate disclosure with the reporter

### Provide Steps and Code to Reproduce the Vulnerability

1. Describe the environment. Include the `finra-py` version, Python version, operating system, and other relevant details.
2. Describe the steps needed to reproduce the issue, the affected functionality, and relevant security impact.
3. Provide a minimal reproducible example. If possible, isolate the issue to a small, self-contained script that uses only `finra-py`.

**IMPORTANT: Do not include API credentials, OAuth tokens, token-file contents, production data, personal information, or other confidential information in a vulnerability report.** See [Bug Reporting](https://finra.hawkberry.com/en/latest/help.html) for guidance on providing error and exception logs.

### Disclosure

Please allow reasonable time for investigation and remediation before public disclosure. Confirmed security fixes are released through the normal project release process. Unless otherwise agreed to in writing, response and remediation timing depends on the nature and severity of the issue and is not a fixed service-level commitment. 

