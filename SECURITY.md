# Security Policy for `finra-py`

## Scope

This policy applies to latest released version of `finra-py` and its direct runtime dependencies:

- `authlib`
- `httpx`
- `jsonschema`
- `tzdata` (Windows only)

The supported version ranges for these dependencies are defined by the project's package metadata.

## Supported Versions

Security fixes are provided for the latest released version of `finra-py`. Older releases are not maintained as separate security-support branches.

A vulnerability in a supported runtime dependency may require a `finra-py` release even when no vulnerability exists in `finra-py` source code. When necessary, the minimum supported dependency version will be raised to exclude the affected versions.

## Security Boundary

`finra-py` is a client-side library that runs in the calling application's process. Applications communicate directly with the FINRA API. `finra-py` constructs API requests and returns standard `httpx.Response` objects directly t the application. Application storage, retention, access control, encryption, and response processing remain the responsibility of the calling application.

See the [Client Architecture and HTTP Response Boundary ADR](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0001-client-architecture-http-boundary.md).

`finra-py` does not provide a maintainer-operated service, proxy application traffic through maintainer infrastructure, or remotely store application or API data. `finra-py` does not implement telemetry, analytics, advertising, or usage tracking.

## Authentication and Token Storage

`finra-py` uses Authlib's HTTPX integration for OAuth 2.0 authentication. API credentials are handled by the underlying OAuth2 client. OAuth token data is managed by the token manager and accessed through the configured token-storage read/write functions. By default tokens are written to a local file system location set by the application's `token_path`. Alternatively, the application can configure custom read/write functions to implement local or non-local token storage patterns.

See the [Authentication documentation](https://finra.hawkberry.com/en/latest/auth.html) and the OAuth 2.0 ADR.

## Sensitive Data

| Data | `finra-py` handling | Library-managed persistence |
| --- | --- | --- |
| API key and API secret | Passed to the underlying OAuth2 client | Not written to the default token file |
| OAuth token data | Managed by the token manager and token-storage functions | `token_path` by default, or the application's custom storage callback functions |
| Query parameters and request payloads | Constructed and sent by the client | None |
| Submission payloads | Constructed and sent by the client | None |
| API responses | Returned as `httpx.Response` objects | None |
| Asynchronous result data | Retrieved and returned by the client | None |
| Diagnostic log data | Optional request/response logging with best-effort redaction | Only where the application configures logging output |
| Custom schema data | Retrieved when client-side validation is configured to use a schema URL | None |

Applications are responsible for protecting credentials, token data, sensitive request and response data, and diagnostic logs.

## Diagnostic Logging

Diagnostic logging is optional and intended for troubleshooting. When enabled, it can record request and response information and applies best-effort redaction of credentials and other sensitive values.

Redaction is not a security boundary or a guarantee that sensitive information cannot appear in logs. Applications must review diagnostic logs before sharing them.

For `text/plain` response content, automatic response-content redaction is not applied; a warning is emitted when that content is logged.

See the [Getting Help documentation](https://finra.hawkberry.com/en/latest/help.html).

## Dependency Security

Direct runtime dependency requirements are declared in `pyproject.toml`. GitHub's dependency graph and Dependabot alerts provide vulnerability monitoring. Automated dependency-update pull requests are not enabled. Dependency updates are made by the project maintainer.

GitHub Dependency Review checks dependency changes introduced through pull requests. CI also audits the resolved dependency set on pushes and pull requests. A dependency security issue may result in a `finra-py` release that changes only dependency minimums when that is sufficient to exclude an affected version.

## Automated Security Checks

The repository uses GitHub CodeQL for static analysis and GitHub secret scanning with push protection. Dependency security is monitored through the GitHub dependency graph, Dependabot alerts, Dependency Review, and CI vulnerability auditing.

## Release Integrity and Provenance

Release distributions are built by the project's GitHub Actions release workflow from versioned repository state and published to PyPI using Trusted Publishing. PyPI publish attestations identify the Trusted Publisher used to publish each release distribution.

The release process is:

1. The maintainer creates and pushes the release version tag.
2. GitHub Actions runs the test suite for the release tag and runs the release workflow.
3. The release workflow builds and publishes the release distributions to PyPI using Trusted Publishing.
4. PyPI records a publish attestation for each published distribution.

Trusted Publishing uses short-lived identity tokens rather than a long-lived PyPI upload credential.

## Reporting a Vulnerability

Please do not report suspected security vulnerabilities through a public GitHub issue.

Use GitHub's [Private Vulnerability Reporting](https://github.com/hawkberry/finra-py/security) to report a suspected vulnerability.

If private reporting is unavailable, use the contact address published on the [`finra-py` PyPI project page](https://pypi.org/project/finra-py/).

We will acknowledge reports and perform an initial assessment as soon as reasonably practicable. Reports will be reviewed to determine their validity, severity, affected versions, and appropriate remediation or disclosure steps.

Please include the following information:

### Describe Your Environment

- `finra-py` version
- Python version
- operating system
- other relevant details

### Steps to Reproduce the Vulnerability

Describe the steps needed to reproduce the issue, the affected functionality, and relevant security impact.

### Code to Reproduce the Vulnerability

Please provide a minimal example that reproduces the vulnerability. If possible, isolate the issue to a small, self-contained script that uses only `finra-py`.

### Error/Exception Log

**IMPORTANT:** Sanitize your code before sharing it. **NEVER share API credentials or the contents of your token file.**

Replace all sensitive values with placeholders, including API credentials, OAuth tokens, token files, production data, personal information, or other confidential information in a report.

See the [Bug Reporting facility](https://finra.hawkberry.com/en/latest/help.html) for guidance on providing error and exception logs.

## Disclosure

Please allow reasonable time for investigation and remediation before public disclosure. Confirmed security fixes are released through the normal project release process.
