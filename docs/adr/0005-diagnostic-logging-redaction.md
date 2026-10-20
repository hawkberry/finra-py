# ADR 0005: Diagnostic Logging and Log Redaction

- **Status:** Accepted
- **Decision Date:** 2026-08-09

## Context

`finra-py` performs diagnostic logging using Python's standard `logging` module. These logs are useful for troubleshooting API requests, responses, and authentication, but may also contain credentials, tokens, identifiers, and sensitive data. Applications control Python logging configuration and destinations.

There are two use cases:

1. **Ordinary logging**, where no redaction occurs; the application chooses configuration and accepts responsibility for output.
2. **Bug-report logging**, where `finra-py` provides a dedicated facility with best-effort redaction for logging sensitive values.

The bug-report facility can only apply targeted protection to `finra-py` loggers. Because `finra-py` cannot control every handler or every value an application may log, redaction is scoped to dedicated logging handlers which avoids modifying records seen by other handlers. In order to be redacted, sensitive values must be registered for redaction before corresponding diagnostic records are emitted.

The bug-report facility supports recursive inspection for JSON data, which can distinguish sensitive API fields from ordinary values. Free-text submission fields require regular expression pattern matching because sensitive information may appear within otherwise ordinary prose. Neither approach can guarantee that every sensitive value is recognized and redacted, and therefore redaction is **best effort**; the application and end user remain responsible for ensuring that all sensitive data is redacted before sharing any logs.

This ADR does not establish application logging policy, production logging, log retention or access-control policy.

## Decision

`finra-py` will support standard Python logging for ordinary diagnostics, and a separate, explicitly enabled logging facility with handler-scoped, best-effort redaction for bug-reporting.

Specifically:

1. Ordinary diagnostic logging will use Python's standard `logging` interfaces. The library will not install a process-wide redaction filter or otherwise reconfigure the root logger.
2. Ordinary `DEBUG` logging will not enable sensitive-value registration or automatically redact log output. Applications that configure ordinary logging remain responsible for the security of those logs.
3. `debug.enable_bug_report_logging()` will provide the dedicated bug-report logging path. It will explicitly enable redaction registration, configure the `finra.debug`, `finra.auth`, and `finra.base_client` loggers for `DEBUG`, and attach redacting file and/or stream handlers to those loggers.
4. Bug-report logging will write to `sys.stderr` by default. Applications may instead provide a file, disable the stream, or provide both. A dedicated file is recommended when logs will be shared for troubleshooting.
5. Bug-report logging is intended for troubleshooting rather than production logging or production audit trails. It will remain explicitly opt-in because detailed request and response logging and redaction processing introduce performance and data-handling costs.
6. Redaction will occur at the output-handler boundary. The redacting handlers will format a `LogRecord`, redact the resulting message, and write the redacted message without modifying the original record. Consequently, other handlers receiving the same record are not made redaction-safe by the presence of a redacting handler.
7. Sensitive values will be maintained in a redaction registry as exact strings associated with labels. `None` and empty or whitespace-only values will not be registered. When values are substituted, longer registered values will be matched before shorter values to reduce partial-value matches.
8. Structured request and token data will be inspected recursively before the related diagnostic log is emitted. Leaf values whose keys match the library's sensitive-key patterns will be registered for redaction, subject to explicit whitelisting where required.
9. FINRA filter objects will be labeled using their `fieldName` when associating `fieldValue` and `values` with the sensitive field being redacted.
10. Known potentially sensitive free-text submission fields will receive additional key-scoped inspection. The implementation will use regular expressions to detect sensitive patterns defined by the FINRA API, including patterns for identifiers and health-related information, and will redact matching portions or the complete field where the configured rules require it.
11. Redaction registration entry points will return immediately when redaction is disabled. Ordinary `DEBUG` logging therefore does not incur the structured-data traversal and registration work used by the bug-report facility.
12. HTTP `200` responses will be inspected for redaction registration by calling `Response.json()` regardless of the response content type. Successfully decoded JSON is recursively inspected with the response-specific free-text rules.
13. If an HTTP `200` response cannot be decoded as JSON, values from that response will not be registered for structured redaction. A warning will be emitted through the `finra.debug` logger instructing the user to review the log before sharing it.
14. Request data and authentication token state will be registered before their corresponding diagnostic messages are emitted. The same logging approach is used by synchronous and asynchronous client operations.
15. The redaction mechanism will remain explicitly documented as **best effort**. It is not a guarantee that sensitive information is absent from logs, and applications must review logs before retaining, sharing, or submitting them to another party.

## Data Flow

```text
                           Ordinary Diagnostic Logging
                           ┌─────────────────────────┐
                           │   Calling application   │
                           └────────────┬────────────┘
                                        ▼
                           ┌─────────────────────────┐
                           │     Python logging      │
                           └────────────┬────────────┘
                      ┌─────────────────┴─────────────────┐
                      ▼                                   ▼
        ┌────────────────────────────┐        ┌──────────────────────┐
        │ `finra-py` logger handlers │        │ Application handlers │
        └─────────────┬──────────────┘        └──────────────────────┘
                      ▼
           ┌──────────────────────┐
           │   LogRecord output   │
           └──────────────────────┘
```

```text
                               Bug-Report Logging
                       ┌─────────────────────────────────┐
                       │ Request / token / response data │
                       └────────────────┬────────────────┘
                                        ▼
                            ┌────────────────────────┐
                            │ Redaction registration │
                            └───────────┬────────────┘
                                        ▼
                            ┌────────────────────────┐
                            │   Python `LogRecord`   │
                            └───────────┬────────────┘
                                        ▼
                            ┌────────────────────────┐
                            │   Redacting handler    │
                            └───────────┬────────────┘
                                        ▼
                            ┌────────────────────────┐
                            │    Format + Redact     │
                            └───────────┬────────────┘
                                        ▼
                          ┌────────────────────────────┐
                          │ File and/or stream output  │
                          └────────────────────────────┘
```

## Consequences

### Positive

- Applications can obtain detailed diagnostics for FINRA API troubleshooting without adopting a separate logging framework.
- Bug-report logs receive targeted protection for tokens, identifiers, and sensitive structured or free-text values.
- Ordinary Python logging remains unchanged and under application control.
- Redaction is isolated to dedicated output handlers and does not alter `httpx.Response` objects or logging-record interfaces.
- Redaction registration is skipped unless bug-report logging is explicitly enabled.
- The same design applies to synchronous and asynchronous client operations.

### Negative

- Redaction may be incomplete and may produce false negatives or false positives.
- Non-JSON response content and other data not covered by registration rules may remain visible and require manual review.
- Other application or root-logger handlers may receive unredacted records, and can handle and log sensitive values outside the portions of the logging path controlled by `finra-py`.
- Exact-value redaction can produce value collisions, resulting in unintended redactions or inaccurate redaction labels.
- The redaction registry retains registered values in process memory while it is used by the logging facility.
- Detailed `DEBUG` logging and redaction processing introduce performance overhead.
- Applications remain responsible for secure logging destinations, retention, access control, and review before disclosure.

## Alternatives Considered

### No Built-In Redaction

Applications could use ordinary Python logging and redact records themselves before storing or sharing them.

This was rejected because `finra-py` has direct knowledge of FINRA request and response structures and can provide useful targeted redaction for common sensitive values. Requiring every application to reconstruct that handling would make bug reporting less consistent and increase the chance of accidental disclosure.

### Global Logging Filter

`finra-py` could install a filter on the root logger or otherwise reconfigure process-wide logging so that every record is redacted.

This was rejected because `finra-py` does not control the application's logging architecture. Process-wide configuration would affect unrelated application records and could interfere with application logging configuration while still failing to guarantee that every output path is safe.

### Mutate the `LogRecord`

The library could redact the message in the `LogRecord` before other handlers process it.

This was rejected because it would change the record seen by unrelated handlers and make redaction an implicit property of the logging record rather than an explicit property of the destination being protected.

### Always-On Redaction Registration

The client could always inspect request and response data and maintain the redaction registry even when ordinary logging is used.

This was rejected because ordinary logging does not promise redaction, and maintaining the registry and traversing structured data would add processing overhead to normal client operation without providing a corresponding benefit.
