# ADR 0001: Client Architecture and HTTP Response Boundary

- **Status:** Accepted
- **Decision Date:** 2026-08-09

## Context

`finra-py` provides a Python interface to the FINRA API Platform. It translates Python operations into FINRA API requests and centralizes FINRA-specific behavior, including authentication, request construction, endpoint selection (data, metadata, partitions, and datasets), field selection, filtering, sorting, pagination, server-side asynchronous requests, content-type handling, dataset-specific parameters, notifications, regulatory filings, and submission functionality. This saves applications from implementing that functionality themselves.

`finra-py` uses HTTPX for HTTP communication, a well-established Python library with support for synchronous and `asyncio`-based requests. It does not add a separate interface for standard HTTP behavior or replace HTTPX responses with `finra-py`-specific response objects or data models.

This keeps the division clear: `finra-py` handles FINRA-specific API behavior while returning standard `httpx.Response` objects directly to applications. Applications can inspect response status codes, headers, and content, and control any further processing, validation, or persistence. Higher-level features for specific FINRA API operations can still be added, provided they do not hide or replace the underlying `httpx.Response`.

## Data Flow

```text
                 Normal HTTP path
             ┌──────────────────────┐
             │ Calling application  │
             └──────────┬───────────┘
                        ▼
             ┌──────────────────────┐
             │      finra-py        │
             └──────────┬───────────┘
                        │
               access token needed?
                   ╱          ╲
                yes            no
                 │              │
                 ▼              │
      ┌─────────────────────┐   │
      │   FINRA Identity    │   │
      │   Platform (FIP)    │   │
      └──────────┬──────────┘   │             Async result retrieval (3rd leg)
                 │              │                 ┌──────────────────────┐
            access token        │                 │ Calling application  │
                 └──────┬───────┘                 └──────────┬───────────┘
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │      finra-py        │             │      finra-py        │
             └──────────┬───────────┘             └──────────┬───────────┘
                        │                                    │
               bearer-authenticated                 pre-signed result URL
                   API request                               │
                        │                                    │
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │  FINRA API Platform  │             │ Async Result Server  │
             └──────────┬───────────┘             └──────────┬───────────┘
                        │                                    │
                  HTTP response                        HTTP response
                        │                                    │
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │      finra-py        │             │      finra-py        │
             └──────────┬───────────┘             └──────────┬───────────┘
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │ Calling application  │             │ Calling application  │
             └──────────────────────┘             └──────────────────────┘
```

## Decision

**`finra-py` is FINRA-specific on the way in, and standard HTTPX on the way out.**

`finra-py` communicates directly with FINRA’s API Platform and related resources over HTTPS. It provides FINRA-specific interfaces for constructing requests and performing API operations, and returns `httpx.Response` objects directly to the calling application.

Specifically:

1. `finra-py` handles FINRA-specific authentication and request construction.
2. `finra-py` provides dedicated interfaces for the FINRA Query, Notification, and Submission APIs.
3. `finra-py` represents FINRA-specific concepts through Python interfaces, **such as**:
   a. dataset-specific methods
   b. endpoint enums
   c. field enums for selection and sorting
   d. filter objects for value comparisons, domains, and date ranges
   e. pagination parameters
   f. parameters and methods for multi-leg server-side asynchronous requests
   g. response content-type parameters
   h. other dataset-specific parameters
   i. filing objects for building regulatory submissions
   j. submission functionality for regulatory filings
4. `finra-py` does not introduce a custom response type or separate response-processing model. API requests return standard `httpx.Response` objects directly to the caller.
5. Applications control how they handle response status, headers, and content, and how they process, represent, transform, validate, or persist response data.
6. `finra-py` provides OAuth 2.0 authentication and token lifecycle management.
7. `finra-py` provides synchronous and asynchronous (`asyncio`) clients.
8. No maintainer-operated service sits between the calling application and FINRA API endpoints or related resources.
9. For server-side asynchronous check status and result requests, `finra-py` restricts URL locations to approved hosts and disables automatic redirect following, to reduce the risk of exposing access tokens to unintended hosts.

## Consequences

### Positive

- Applications do not need to implement FINRA-specific request construction themselves.
- Applications retain access to standard `httpx.Response` behavior.
- Applications are not coupled to a `finra-py`-specific response model.
- FINRA-specific functionality can be exposed through purpose-built Python interfaces without obscuring the HTTP layer.
- Applications control how responses are processed and how data is represented.
- The client has a clearly defined boundary between FINRA-specific behavior and general HTTP behavior.
- Synchronous and `asyncio`-based operation use the same underlying `finra-py` `BaseClient` class with either a synchronous or asynchronous HTTPX client.
- Asynchronous URL validation and disabled automatic redirects reduce the risk of exposing access tokens to unintended hosts.

### Negative

- Applications are responsible for processing returned responses.
- Applications must understand standard HTTP response semantics.
- Applications that require domain-specific models or additional response processing must implement those themselves.

## Alternatives Considered

### Raw HTTPX Requests

Client query methods could have applications construct FINRA API requests themselves using raw HTTPX. This would preserve the HTTP boundary, but each application would need to implement FINRA-specific behavior independently, including all of the features implemented by `finra-py` listed in the Context section above.

This was rejected because it would require applications to implement the core FINRA API functionality themselves.

### Custom Responses and Data Models

The client could convert `httpx.Response` objects into `finra-py`-specific response objects or data models.

This was rejected because it would replace the established `httpx.Response` interface with a library-specific representation and would impose assumptions about how applications should consume FINRA data. Applications should determine how returned data is represented and processed, rather than the client library.
