# Security Policy for finra-py

## Supported Versions

Security fixes are provided for the latest released version of `finra-py`.

## Reporting a Vulnerability

If you believe you have found a security vulnerability in `finra-py`, please do not open a public issue.

Please report the suspected vulnerability through GitHub's private vulnerability reporting feature:

https://github.com/hawkberry/finra-py/security

If that is unavailable, use the contact email listed on the `finra-py`
[PyPI project page](https://pypi.org/project/finra-py/).

Please include the following information:

### Describe Your Environment

Python version:
Operating system:
finra-py version:
Other relevant details:

### Steps to Reproduce the Vulnerability

Describe the steps needed to reproduce the issue.

### Code to Reproduce the Vulnerability

Please provide a minimal example that reproduces the vulnerability. If possible, isolate the issue to a small, self-contained script that uses only `finra-py`.

**IMPORTANT:** Sanitize your code before sharing it. **NEVER share API credentials or the contents of your token file.** Replace all sensitive values with placeholders.

### Describe the Expected Behavior

Describe what you expected to happen.

### Describe the Actual Behavior

Describe what actually happens.

### Error/Exception Log

See the [Bug Reporting facility](https://finra.hawkberry.com/en/latest/help.html) for guidance on providing error and exception information.

We will acknowledge receipt and review the report as soon as possible.

## Scope

This policy applies to `finra-py` and its direct dependencies:

- `authlib`
- `httpx`
- `jsonschema`
- `tzdata`

## Disclosure

Please allow reasonable time for investigation and remediation before public disclosure.
