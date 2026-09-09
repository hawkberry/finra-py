# ADR: Client Architecture and HTTP Response Boundary

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

`finra-py` provides a Python interface to the FINRA API Platform. The client is responsible for translating Python-level operations into requests understood by FINRA, including authentication, endpoint selection, dataset-specific parameters, filtering, sorting, pagination, partitions, notifications, and regulatory submissions.

The client must provide enough FINRA-specific functionality to make these operations practical from Python without imposing a separate application-level interface for standard HTTP behavior.

In particular, applications should be able to use the capabilities of a dedicated FINRA client while retaining direct access to the HTTP response and its standard semantics.

## Decision

`finra-py` will maintain a **direct, standards-based HTTP boundary** while providing **FINRA-specific interfaces for request construction and API operations**.

Specifically:

- FINRA-specific authentication and request construction are handled by `finra-py`.
- The client provides dedicated interfaces for the FINRA Query, Notification, and Submission APIs.
- FINRA-specific concepts are represented through Python interfaces such as dataset-specific methods, enums, filters, and submission functionality where appropriate.
- API requests return standard `httpx.Response` objects directly to the caller.
- The client does not replace HTTP responses with a custom response type or impose a separate response-processing model.
- Applications retain control over response status, headers, content, and payload processing.
- OAuth 2.0 authentication and token lifecycle management are handled through the client's authentication facilities.
- The client supports both synchronous and `asyncio`-based client operation.
- The client does not prescribe how applications represent, transform, validate, persist, or otherwise consume API response data.

## Rationale

A dedicated FINRA client is valuable because the FINRA API has concepts and requirements that should not have to be reconstructed by every application. Authentication, endpoint selection, dataset parameters, filtering, pagination, partitions, notifications, submissions, and other FINRA-specific operations belong at the client interface.

HTTP responses are different. HTTP already provides a well-established interface, and HTTPX provides a standard Python implementation of that interface. Replacing the response with a `finra-py`-specific abstraction would add another interface without solving a FINRA-specific problem.

Returning `httpx.Response` therefore establishes a clear boundary:

**FINRA-specific on the way in, standard HTTPX on the way out.**

This gives applications the convenience of a dedicated FINRA client while preserving the control and familiarity of the underlying HTTP interface.

The same principle applies to response processing. `finra-py` should not assume whether an application wants to deserialize JSON, inspect headers, handle particular status codes, persist raw responses, transform records into application models, or apply additional validation. Those are application concerns.

## Consequences

### Positive

- Applications do not need to implement FINRA-specific request construction themselves.
- Standard HTTPX response behavior remains available to applications.
- Applications are not coupled to a `finra-py` response model.
- FINRA-specific functionality can be exposed through purpose-built Python interfaces without obscuring the HTTP layer.
- Applications retain control over response processing and data representation.
- The client has a clearly defined boundary between FINRA-specific behavior and general HTTP behavior.
- Synchronous and `asyncio` client usage can be supported using the same `finra-py` `BaseClient` class by using either synchronous or asynchronous HTTPX clients.

### Negative

- Applications are responsible for processing returned responses.
- Applications must understand standard HTTP response semantics.
- `finra-py` does not automatically impose a single Python representation for all returned FINRA data.
- Applications requiring domain-specific models or additional response processing must implement those concerns themselves.

## Alternatives Considered

### Raw HTTPX Requests

Applications could use HTTPX directly and construct FINRA API requests themselves.

This would preserve the standard HTTP boundary but would require each application to independently implement FINRA-specific authentication, endpoint construction, dataset parameters, filtering, pagination, partitions, notifications, submissions, and related behavior.

This was rejected because it duplicates FINRA-specific client functionality across applications.

### Custom Response and Data Abstraction

The client could convert HTTP responses into `finra-py`-specific response objects or automatically transform returned data into higher-level Python models.

This was rejected because it would replace an established HTTP interface with a library-specific representation and would impose assumptions about how applications should consume FINRA data.

The application, rather than the client library, should determine how returned data is represented and processed.

## Scope

This decision establishes the architectural boundary between FINRA-specific client functionality and standard HTTP behavior.

It does not prohibit higher-level functionality where that functionality addresses a specific FINRA API requirement. Such functionality should preserve the direct HTTP response boundary unless there is a separate architectural decision establishing otherwise.
