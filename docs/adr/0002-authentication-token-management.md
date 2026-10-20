# ADR 0002: Authentication and Token Management

- **Status:** Accepted
- **Decision Date:** 2026-08-09

## Context

`finra-py` provides a Python interface to the FINRA API Platform. To make authenticated requests, it must first obtain a valid access token from the FINRA Identity Platform for the provided credentials. It must operate for different API environments and credential types, and manage token expiration. If an application persists tokens, the application controls where and how they are stored.

The FINRA API Platform uses OAuth 2.0 for authentication and authorization. `finra-py` provides an interface for API authentication without reimplementing the OAuth 2.0 protocol or requiring an application to build and maintain its own token-management logic.

API credentials and OAuth tokens require special security considerations. Applications may already have established controls for managing secrets and storing credentials, so `finra-py` must not require a particular storage system or security model. Applications remain responsible for protecting credentials and persisted tokens, including controlling access and retention, managing encryption, and configuring diagnostic logging. The default token file is not encrypted.

`finra-py` supports synchronous and asynchronous (`asyncio`-based) authentication. Asynchronous token acquisition must use a non-blocking asynchronous HTTPX client. Applications must also be able to create and configure an asynchronous client before entering the `asyncio` event loop. Synchronous storage callbacks run inline and can block the event loop, so applications should use asynchronous callbacks for network-based storage. Authentication configuration and token state must remain separate for the production, Mock, and QA Test environments and for each credential type.

`finra-py` runs within the calling application’s process. It does not provide a maintainer-operated authentication service, route application traffic through maintainer infrastructure, or remotely store application or API data. FINRA authorization and entitlement policies are outside this decision and depend on the calling application and the FINRA API Platform.

This ADR addresses authentication and token management, not the broader HTTP client architecture established by [ADR 0001 — Client Architecture and HTTP Response Boundary](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0001-client-architecture-http-boundary.md).

## Decision

`finra-py` will use Authlib’s OAuth 2.0 HTTPX integrations to handle the OAuth 2.0 protocol and `TokenManager` to manage token lifecycle and persistence. This avoids maintaining a separate OAuth 2.0 implementation. Applications control how credentials are supplied and how tokens are persisted, and can configure token access through custom callbacks. By default, tokens are stored in a local JSON file.

Specifically:

1. OAuth 2.0 authentication will use Authlib's `OAuth2Client` and `AsyncOAuth2Client` rather than a `finra-py` implementation of the OAuth 2.0 protocol.
2. API keys and secrets will be supplied to the OAuth2 session. `TokenManager` will not manage them, and the default token file will not contain them.
3. `TokenManager` will hold the raw OAuth token in memory, along with its creation timestamp and the `token_write_func` callback used to persist the updated token state.
4. Persisted token state will include `finra-py` metadata and the raw OAuth token, allowing token age and expiration to be evaluated when a client is reconstructed.
5. Applications can use `token_read_func` and `token_write_func` callbacks to customize token persistence, and use their existing storage and security controls. By default, the token is stored in a local JSON file at the application-provided `token_path`.
6. The default token writer will write an application-managed file; it will not provide application-specific encryption or act as a credential store.
7. `get_client()` and `get_async_client()` will centralize token loading and lifecycle checks. They will reuse a stored token if it meets the configured `min_expires_in` threshold, otherwise they will obtain a new token.
8. When checking whether to reuse a stored token, `get_client()` and `get_async_client()` will require at least one hour of remaining lifetime by default. Applications can change or disable this threshold.
9. Lower-level authentication functions will retain distinct responsibilities:
   a. loading an existing token from a local file will not fetch a replacement
   b. storage access functions will use the provided `token_read_func` to access an existing token without replacing it
   c. new-token functions will always obtain a new token
   d. build functions will construct clients from an already configured `TokenManager`
10. Automatic token refresh will be opt-in through `automatic_refresh=True`. When enabled, the underlying Authlib OAuth2 session will obtain a new client-credentials token when the current one expires and pass it to the `token_write_func` for persistence.
11. `Client.refresh_token()` and `AsyncClient.refresh_token()` operations will remain available regardless of whether automatic refresh is enabled. They will propagate the return value of the configured `token_write_func` callback.
12. Synchronous authentication will use `OAuth2Client`; asynchronous authentication will use `AsyncOAuth2Client`.
13. Asynchronous authentication functions will perform initial token acquisition using an asynchronous HTTPX client, rather than using a blocking synchronous client inside an asynchronous application.
14. Synchronous authentication functions will support creating asynchronous clients for applications that require the client instance before entering its `asyncio` event loop.
15. Asynchronous authentication functions will support synchronous and asynchronous `token_read_func` and `token_write_func` callbacks.
16. Synchronous callbacks used by asynchronous authentication functions run inline and block the event loop. Applications should use asynchronous callbacks for network I/O.
17. Synchronous authentication functions will only support synchronous callbacks.
18. Clients will expose token lifecycle information (`token_age`, `token_expires_at`, and `token_expires_in`) as read-only values.
19. When bug-report logging is enabled, authentication tokens will be registered with the library's diagnostic-log redaction mechanism before authentication state is logged. Redaction is a best-effort safeguard, not a replacement for application-level logging controls. See [ADR 0005 — Diagnostic Logging and Log Redaction](https://github.com/hawkberry/finra-py/blob/main/docs/adr/0005-diagnostic-logging-redaction.md).
20. Production, Mock, and QA Test Environment authentication endpoints and credentials will remain distinct. Applications are responsible for using the appropriate credentials and separate token storage for each environment.

## Data Flow

The authentication and refresh paths are shown together to make the relationship between token acquisition, `TokenManager`, Authlib, and the calling application explicit.

```text
              Initial Authentication
             ┌──────────────────────┐
             │ Calling application  │
             └──────────┬───────────┘
                        ▼
             ┌──────────────────────┐
             │      finra-py        │
             │    auth functions    │
             └──────────┬───────────┘                   Token Refresh
                        │                         ┌──────────────────────┐
                 existing token?                  │   Client / OAuth2    │
                 ╱              ╲                 │       session        │
              yes                no               └──────────┬───────────┘
               │                  │                          │ refresh
               ▼                  ▼                          ▼
      ┌─────────────┐   ┌──────────────────┐      ┌──────────────────────┐
      │   token     │   │  FINRA Identity  │      │    FINRA Identity    │
      │   storage   │   │  Platform        │      │    Platform          │
      └────────┬────┘   └─────────┬────────┘      └──────────┬───────────┘
               └────────┬─────────┘ new token                │ new token
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │    TokenManager      │             │     TokenManager     │
             └──────────┬───────────┘             └──────────┬───────────┘
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │  Authlib OAuth2      │             │ token_write_func     │
             │  HTTPX integration   │             │ application-managed  │
             └──────────┬───────────┘             │ storage or file      │
                        │                         └──────────┬───────────┘
                        ▼                                    ▼
             ┌──────────────────────┐             ┌──────────────────────┐
             │        Client        │             │        Client        │
             └──────────────────────┘             └──────────────────────┘
```

The same architectural boundary is used by synchronous and asynchronous clients. The asynchronous path uses Authlib's `AsyncOAuth2Client` for token acquisition and can await asynchronous callbacks where provided.

## Consequences

### Positive

- Applications do not need to implement the OAuth 2.0 token acquisition flow themselves.
- Authlib handles OAuth 2.0 protocol operations, reducing the amount of custom authentication code `finra-py` must maintain.
- API credentials are separated from persisted token state; the default token representation does not contain the API secret.
- Applications can use the default local token file for straightforward deployments without having to implement token serialization themselves.
- Enterprise applications can integrate token persistence with existing credential-management infrastructure through callbacks without introducing a `finra-py`-specific storage service.
- The authentication boundary remains inside the application's process, with no maintainer-operated service or authentication proxy between the application and the FINRA API Platform or related resources.
- Synchronous and asynchronous applications receive equivalent authentication capabilities without forcing asynchronous applications through a blocking initial token request.
- Applications can set a proactive token-replacement threshold, opt in to automatic refresh, and invoke manual token refresh.
- Token lifecycle information is available to applications without exposing the internal storage mechanism.
- When bug-report logging is enabled, authentication-sensitive values are registered with the library’s redaction mechanism.

### Negative

- Applications remain responsible for protecting API credentials and persisted OAuth tokens. `finra-py` does not make an application's storage location secure.
- The default token writer uses ordinary JSON file persistence and does not provide application-specific encryption, access-control policy, key management, or retention policy.
- Custom token-storage callbacks become part of the application's security boundary, and the application is responsible for implementing them correctly and securely.
- The distinction among the authentication factory functions provides flexibility but requires applications using the lower-level functions to understand their different token-loading and refresh behaviors.
- Automatic refresh reduces application control over the timing of token acquisition, and return values from `token_write_func` cannot be propagated directly to the caller when Authlib performs a refresh implicitly.
- Persisted token state includes `finra-py` metadata and therefore is a library-managed representation of the token, rather than simply the raw OAuth token returned by the FINRA Identity Platform. Existing persisted data that does not contain the required metadata must be recreated.

## Alternatives Considered

### Hand-Rolled OAuth 2.0 Implementation

`finra-py` could implement the OAuth 2.0 client-credentials flow and token lifecycle directly.

This was rejected because OAuth 2.0 is a standardized security-sensitive protocol and Authlib already provides the required client functionality. Maintaining a second implementation would increase the amount of authentication code that `finra-py` must secure, test, and maintain without providing a corresponding benefit to API users.

### Authentication Credentials Stored in the Client

The client could own and directly manage API credentials and token persistence.

This was rejected because it would combine protocol state, application credential management, and token storage into a single abstraction. Keeping credentials within the underlying OAuth2 session while assigning token persistence to `TokenManager` establishes a clearer boundary and prevents the client abstraction from becoming a credential store.

### Built-In Encrypted Token Store

`finra-py` could provide an encrypted token database or a vendor-specific secrets-management implementation.

This was rejected because encryption, key management, access control, retention, auditing, and deployment-specific credential infrastructure are application concerns. A built-in store would impose security and operational assumptions on consuming applications instead of allowing them to integrate with controls already required by their environment.

### Mandatory Automatic Refresh

All clients could automatically obtain a replacement token whenever the current token expires.

This was rejected because authentication timing is observable application behavior. Some applications require explicit control over authentication calls, token persistence, and error handling. Automatic refresh is therefore available as an explicit option rather than being imposed on every integration.

### Filesystem-Only Token Persistence

`finra-py` could require all applications to persist tokens through `token_path`.

This was rejected because many deployments do not use local filesystem storage for credentials. The callback interface allows the same `finra-py` authentication lifecycle to be preserved while storing tokens in a location appropriate to their environment.

### Synchronous Token Acquisition During Asynchronous Authentication

Asynchronous authentication functions could obtain the initial token through the synchronous `OAuth2Client`.

This was rejected because synchronous token acquisition during asynchronous authentication would block the event loop. Asynchronous authentication functions will use `AsyncOAuth2Client` for token acquisition. Synchronous authentication functions may still create an asynchronous client before the application enters the event loop.
