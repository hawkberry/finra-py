# ADR 0004: Client-Side Submission Validation

- **Status:** Accepted
- **Decision Date:** 2026-08-09

## Context

`finra-py` provides filing objects for constructing FINRA Submission API requests and a `Validator` object for comparing JSON objects against JSON Schemas published by the FINRA API Platform.

Client-side validation is not a replacement for the API's server-side validation. For supported filings, validation can be invoked on the server-side after transmitting a filing to FINRA by setting `FilingStatus.VALIDATE` in the filing metadata. Alternatively, client-side validation is performed locally prior to transmitting a filing to FINRA. The primary benefit of client-side validation is that schema-level filing errors can be corrected before potentially sensitive data is transmitted, reducing unnecessary exposure and shortening the correction cycle. Once retrieved, schemas can be reused for validation without repeated network requests.

Client-side validation checks constraints represented by the available schemas, but it cannot reproduce the validation performed by the API outside those schemas. The API's documentation and schemas can be inconsistent; see [Known FINRA API Issues](https://finra.hawkberry.com/en/latest/help.html#known-finra-api-issues). `finra-py` filing objects enforce construction-time requirements for documented metadata fields when an filing is built, whereas the `Validator` handles the broader schema-defined constraints without duplicating the schema rules in Python code.

Although submission filings are the primary use case, `Validator` can be used independently of submission methods, for example for dataset response data defined by a FINRA API schema. Network retrieval is restricted to approved FINRA API Platform schema hosts. Applications remain responsible for protecting filing data during construction, validation, logging, and error handling.

## Decision

`finra-py` will provide optional client-side JSON Schema validation as the final client-side validation step before submission. Filing objects enforce construction-time requirements for documented metadata fields, and the API's published schemas define the broader schema-level checks performed by client-side validation.

Specifically:

1. `BaseFiling` subclasses will enforce clear, documented construction-time requirements. They will not duplicate every schema constraint for every filing. Requirements not documented as part of the filing object's interface remain schema-level rules.
2. Passing client-side validation does not imply that FINRA will accept a filing. For supported filings, `FilingStatus.VALIDATE` will invoke a server-side completeness check, while `validate=True` validates locally before the submission request is sent.
3. `BaseClient` submission methods will default to `validate=False`. Validation is available through `Client`, but not through `AsyncClient` which rejects `validate=True` because the `jsonschema` library is synchronous. With `validate=True`, the exact JSON object built for the request will be validated before the corresponding `POST`, `PUT`, or `PATCH` request is sent.
4. A `BaseFiling` supplies its own `schema_url` by default, but an explicit `schema_url` may override it. Providing a pre-built filing to a submission method as a dictionary requires a non-empty `schema_url` if `validate=True`.
5. `Validator` will be usable outside of submission methods. It will validate a `BaseFiling` or a pre-built filing as a dictionary against a provided top-level schema URL. It will use `jsonschema` and `referencing.Registry` to resolve `$ref` URLs, with `jsonschema.Draft7Validator` as the default. Retrieved schemas without `$schema` are treated as Draft 7.
6. Retrieved schemas will be stored under the requested URL in the client's `schema_registry` or in an explicitly supplied `schema_registry` dictionary. Applications can clear the registry when validation is complete to free up resources.
7. The `schema_registry` will be checked before network retrieval. If a URL is in the `schema_registry`, its cached schema will be used rather than fetching it over the network. Compatible non-FINRA schemas will be used if present in the `schema_registry`, but they cannot be fetched from arbitrary external hosts.
8. The following network policy will be enforced when an uncached schema is fetched over the network, and a `ValueError` will be raised if the destination URL fails the policy. If the URL is not found in the `schema_registry`, the schema will be fetched using the authenticated client's existing HTTPX client **only if** the URL:
   a. uses HTTPS
   b. does not contain embedded credentials, and
   c. has a hostname that exactly matches one of the approved FINRA API hosts (ports are unrestricted):
      1. `datacollection-api.finra.org`
      2. `fingerprints.finra.org`
      3. `ramp-schemas.datacollection.finra.org`
      4. `schemas.api.finra.org`
      5. `static.rampweb.finra.org`, or 
      6. `static.rampweb.qa.finra.org`
9. Redirects will be handled individually, rather than automatically by HTTPX, by setting `follow_redirects=False`. This allows every redirect to be validated against the network policy described above. Allowing HTTPX to redirect automatically would bypass network policy validation for redirects. The number of allowed redirects is equal to the `max_redirects` parameter configured on the HTTPX client, and `httpx.TooManyRedirects` is raised if that limit is exceeded.
10. The `Validator` class will proxy validator methods and attributes to the underlying `jsonschema.protocols.Validator` that it does not override. `Validator.is_valid()` will accept a `BaseFiling` object or pre-built filing dictionary and return a boolean, while `Validator.validate()` will accept the same, but raise a `jsonschema.ValidationError` on failure.

## Data Flow

The two validation paths share the schema registry but remain distinct:

```text
         Build and validate submission              Resolve and cache schemas
        ┌─────────────────────────────┐                  ┌─────────────┐
        │  Filing object / JSON dict  │                  │  Validator  │
        └──────────────┬──────────────┘                  └──────┬──────┘
                       ▼                                        ▼
               ┌───────────────┐                      ┌───────────────────┐
               │ build object  │                      │ top-level schema  │
               └───────┬───────┘                      └─────────┬─────────┘
                       ▼                                        ▼
         ┌───────────────────────────┐                 ┌─────────────────┐
         │ Filing object constraints │                 │ Registry / $ref │
         └─────────────┬─────────────┘                 └────────┬────────┘
                       ▼                                        │
                ┌─────────────┐                        referenced resource?
                │ JSON object │                           ╱            ╲
                └──────┬──────┘                        yes              no
                       │                                │                │
                 validate=True?                         ▼                │
                   ╱       ╲                       ┌─────────┐           │
                 no         yes                    │ cached? │           │
                 │           │                     └─────────┘           │
                 │           ▼                       ╱     ╲             │
                 │     ┌───────────┐              yes       no           │
                 │     │ Validator │               │         │           │
                 │     └─────┬─────┘               │         ▼           │
                 │           ▼                     │ ┌───────────────┐   │
                 │    ┌─────────────┐              │ │ retrieve with │   │
                 │    │ client-side │              │ │ authenticated │   │
                 │    │ JSON Schema │              │ │    client     │   │
                 │    │ validation  │              │ └───────┬───────┘   │
                 │    └──────┬──────┘              │         │           │
                 └─────┬─────┘                     └────┬────┘           │
                       ▼                                ▼                │
            ┌─────────────────────┐             ┌────────────────┐       │
            │ POST / PUT / PATCH  │             │ resource store │ ◀─────┘
            └──────────┬──────────┘             └───────┬────────┘
                       ▼                                ▼
                   FINRA API               client-side JSON Schema validation
```

The resulting workflow for filing data is:

```text
              Local application                       FINRA API Platform
        ┌───────────────────────────┐           ┌───────────────────────────┐
        │ ┌───────────────────────┐ │           │                           │
        │ │ Build filing locally  │ │           │                           │
        │ └───────────┬───────────┘ │           │                           │
        │             ▼             │           │                           │
        │ ┌───────────────────────┐ │           │  ┌──────────────────────┐ │
        │ │Retrieve/cached schemas│◀─── schema ───▶│  FINRA schema URLs   │ │
        │ └───────────┬───────────┘ │           │  └──────────────────────┘ │
        │             ▼             │           │                           │
        │ ┌───────────────────────┐ │           │                           │
        │ │   Validate locally    │ │           │                           │
        │ └───────────────────────┘ │           │                           │
        │       ╱          ╲        │           │                           │
        │    fail          pass     │           │  ┌──────────────────────┐ │
        │     │              │      │     ┌───────▶│Server-side validation│ │
        │     └─ edit/retry ─┤      │     │     │  └──────────┬───────────┘ │
        │                    ▼      │   filing  │             ▼             │
        │                ┌────────┐ │     │     │  ┌──────────────────────┐ │
        │                │ submit │───────┘     │  │Submission processing │ │
        │                └────────┘ │           │  └──────────────────────┘ │
        └───────────────────────────┘           └───────────────────────────┘
```

## Consequences

### Positive

- Schema-defined filing errors can be detected before sensitive filing data is transmitted to FINRA.
- Retrieved schema resources can be reused across validations, reducing repeated network traffic.
- Documented construction-time checks provide focused errors without duplicating the schema rules in Python.
- `Validator` can be used outside of submission methods to validate filing data or other FINRA API schema-based data.
- Schema retrieval uses the existing authenticated client rather than introducing a separate HTTP or credential boundary, while restricting network requests to approved FINRA API schema hosts.

### Negative

- Uncached schema URLs outside the approved FINRA API hosts cannot be fetched. Applications using other schemas must preload all required resources into the registry.
- The set of approved hosts must be deliberately updated when an additional FINRA schema host is required.
- Validation depends on the accuracy and completeness of the published schemas; results can differ from server-side behavior.
- Schema resources remain in memory until the registry is cleared or discarded.
- Integrated validation in submission methods using `validate=True` is not available through `AsyncClient`.

## Alternatives Considered

### Rely Only on Server-Side Validation

This was rejected because potentially sensitive filing data must be transmitted before many correctable errors are identified, potentially creating unnecessary submission traffic.

### Duplicate FINRA Schema Rules in Python

This was rejected because a second independently maintained ruleset could diverge from FINRA's schemas. Filing objects therefore enforce documented construction requirements while the validator handles schema-defined constraints.

### Validate Only During Filing Construction

This was rejected because construction checks alone would leave schema-defined constraints unvalidated locally and would not provide a general validator for other compatible JSON objects.

### Retrieve Only Top-Level Schemas or Use Separate Unauthenticated Retrieval

This was rejected because complete validation can require referenced resources, some of which require authentication. The existing client session preserves the established HTTP and authentication boundary.

### Allow Arbitrary Schema Destinations

Unrestricted schema retrieval was rejected because requests use the authenticated client and may carry OAuth credentials. Allowing arbitrary initial URLs or unchecked redirect destinations could disclose an access token to unintended hosts. Therefore, network retrieval is limited to six explicitly approved FINRA API schema hosts. Before each authenticated request, the validator checks the URL against the set of allowed hosts. Every allowed host may receive the access token. A newly required subdomain must be explicitly reviewed and added to the allowed list.

### Allow HTTPX to Follow Redirects Automatically

Automatic redirect following was rejected because a customized HTTPX client could follow a redirect before the `Validator` checks the destination. Since the request uses authentication headers, this could disclose the access token to a destination outside the allowed hosts. Each request therefore disables automatic redirect following explicitly, validates the proposed destination against the network policy before making the next request, and closes the intermediate redirect response.

### Persist Schemas Across Application Runs

Persistent caching was rejected for the current design because it adds freshness, invalidation, integrity, and lifecycle concerns beyond those needed to eliminate repeated retrievals during validation.

### Always Validate Submissions

This was rejected because schema retrieval and validation add network and processing overhead, and applications may already validate data or need explicit control over that work. Client-side validation therefore remains opt-in.
