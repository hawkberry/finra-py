# ADR 0003: Enum-Based Representation of FINRA API Values

- **Status:** Accepted
- **Decision Date:** 2026-08-09

## Context

`finra-py` provides a Python interface to the FINRA API Platform. The API has many fixed, case-sensitive names and values (its API vocabulary). Some of these values are part of the structure of the API itself, such as resource endpoints, dataset groups, dataset field names, filter comparison operators, and filing operations. Others are data values returned by, or supplied to, a specific API field.

Manually entering API field names and other fixed API vocabulary creates an avoidable source of integration errors. A misspelled or incorrectly cased field name can result in a request being rejected by the API, while discovering a large dataset's available fields from raw strings is inconvenient for application developers. `finra-py` therefore represents many finite API vocabularies with Python enums and converts those members to the exact strings required by the API. Because the API may accept new values before `finra-py` includes them in its enums, applications need a way to use those values in the meantime.

The enum design serves several different consumers within the library. The `BaseClient` uses enums to represent dataset fields, endpoints, groups, and sorting fields. `Filter` uses dataset field enums and its own `CompareType` enum when constructing advanced query filters. Filing classes use enums for filing status, filing operations, and filing-specific filing types and options. The `RelabelJSON` response relabeling utility can derive a response-field relabel mapping from a dataset enum when its member names match the desired canonical labels; alternatively, applications can supply a mapping or an application-defined enum.

These uses do not imply that every finite set of API values should be an enum. In particular, a dataset field may have a small set of documented possible values without making those values part of the Python enum that represents the field name. Such values are often documented in the field's description or docstring and remain ordinary data supplied to the API.

Dataset-specific keyword parameters that are not query fields may have documented possible values, but those lists may not be authoritative or complete. Treating those values as enums could unnecessarily restrict callers as the API's accepted values evolve.

The cost of a field enum also depends on query capabilities. For example, `get_u4_form_prefill()` and `get_individual_pre_registration_search_v2()` do not support field selection, filtering, or sorting, so a large field enum would provide little value. A complete enum for `get_u4_form_prefill()` would require approximately 3,000 lines of source code. For such cases, response relabeling can instead use an application-supplied mapping.

The design therefore needs to balance type safety and developer usability against API compatibility, maintenance cost, source size, and the risk of misrepresenting an API value domain as complete when it is not.

## Decision

`finra-py` will use Python enums to represent **finite API vocabularies when the vocabulary is sufficiently stable and the enum is useful to developers using the library**. Enum members will contain the exact representation required by the API. `EnumConverter` will provide the common conversion and enforcement behavior used by the library's enum consumers.

Specifically:

1. Dataset field enums will represent documented field names where field selection, filtering, sorting, partition handling, or another feature available to library users makes the enum useful. `Endpoint` and `Group` will represent the finite Query API endpoint and group vocabularies.
2. For dataset field enums, an enum member’s `.value` will contain the exact API field name, preserving its spelling and casing. The Python member name may use a conventional or simplified identifier.
3. `Filter` will use dataset field enums and `CompareType` for filter construction.
4. `BaseFilingOps` will define `FilingStatus` and `Op`.
5. Filing subclasses will define filing-type enums where the filing process has a finite, sufficiently stable vocabulary that is useful to the library’s Python interface. A filing class without an applicable filing-type vocabulary, such as `CreateIndividual`, will not introduce an enum solely for consistency.
6. `FormU4` will also expose `RepAccessType` for its finite, sufficiently stable FINPRO access setting.
7. `EnumConverter` will convert enum members to API values, convert iterables of field enum members, and raise `TypeError` when enum enforcement is enabled and a value is not a member of the expected enum. It will suggest similar enum values for likely typos.
8. Enum enforcement will default to `require_enums=True`. Applications may disable enforcement with `require_enums=False` during construction or through `set_require_enums(False)`. This lets applications use values that the API accepts before `finra-py` adds them to its enums.
9. Enum definitions make the implemented API vocabulary inspectable in source and reference documentation, supporting code review and controlled changes. They do not check that a complete request follows all API rules or is valid for the underlying API operation.
10. `RelabelJSON` may derive a mapping from a dataset enum when the enum’s member names match the desired output labels. However, because application output labels may differ from enum member names, it will also accept application-supplied mappings or application-defined enums. Response relabeling does not require a library dataset enum.
11. A dataset will not receive a field enum merely because metadata exists. Datasets without field selection, filtering, or sorting may not justify a large enum; `get_u4_form_prefill()` and `get_individual_pre_registration_search_v2()` are examples. Applications may define their own enum or mapping when their use case warrants it.
12. Dataset-specific keyword parameters that are not query fields, such as `tier_identifier` and `report_view`, will remain ordinary values unless a separate decision establishes a stable, useful enum. Possible field values also remain application data; a short documented set does not itself justify an enum.

## Data Flow

```text
           ┌─────────────────────────────────────────────────────┐
           │ API vocabulary with a stable, useful finite domain  │
           └──────────────────────────┬──────────────────────────┘
                                      ▼
                            ┌───────────────────┐
                            │    Enum member    │
                            └─────────┬─────────┘
                                      ▼
                            ┌───────────────────┐
                            │   EnumConverter   │
                            └───────────────────┘
                                ╱           ╲
                        require_enums     conversion
                              │               │
                              ▼               ▼
                         ┌──────────┐   ┌────────────┐
                         │ validate │   │ enum.value │
                         └────┬─────┘   └─────┬──────┘
                              └───────┬───────┘
                                      ▼
                            ┌───────────────────┐
                            │ FINRA API request │
                            └───────────────────┘
```

```text
              ┌────────────────────┐
              │ Dataset field enum │
              └─────────┬──────────┘
                        ├──▶ BaseClient fields / sort_fields
                        │
                        ├──▶ Filter field names
                        │
                        ├──▶ partition and sorting logic
                        │
                        └──▶ RelabelJSON convenience mapping
```

```text
              ┌──────────────────────────────────────────┐
              │ Application-specific values and mappings │
              └─────────┬────────────────────────────────┘
                        ├──▶ field values
                        │
                        ├──▶ dataset-specific control keywords
                        │
                        └──▶ custom RelabelJSON mappings
```

## Consequences

### Positive

- Developers can inspect the API field names and other finite, stable API names and values through `finra-py` enums and reference documentation.
- Default enforcement catches many spelling and casing errors before requests or filing payloads are sent to the API.
- `EnumConverter` provides consistent conversion and enum-membership enforcement across `BaseClient`, `Filter`, and filing classes.
- Dataset field enums can be reused for selection, filtering, sorting, partitions, and response relabeling where appropriate.
- Application-defined mappings and `require_enums=False` preserve flexibility for application-specific names and values the API accepts before `finra-py` adds them to its enums.
- The field-enum criterion avoids large definitions where datasets do not let callers use fields for selection, filtering, sorting, or similar query features.

### Negative

- Enum definitions require maintenance as the API's documented vocabulary changes, and a new value may not be available until a later library release.
- Applications may need to disable enforcement temporarily when using a value that the library does not yet represent.
- An enum that incorrectly assumes its members are complete can be more restrictive than the underlying API.
- Datasets without a library enum require an application-supplied mapping or enum if enum-based relabeling is needed.

## Alternatives Considered

### Raw Strings Everywhere

The library could represent all API names and values as strings, and require applications to supply the exact strings the API expects. This was rejected because it would duplicate the API vocabulary in applications that use the library, and lose an opportunity to catch common errors.

### Enums for Every Finite Value or Dataset

The library could create enums for every documented finite value or every dataset with metadata. This was rejected because a short list of documented or accepted values for dataset-specific parameters may not be stable or complete, while a large enum provides little query benefit for datasets without field selection, filtering, or sorting.

### Runtime Metadata-Generated Enums

The library could retrieve metadata at runtime and generate enums dynamically. This was rejected because the public Python interface would depend on runtime retrieval and become less straightforward for static typing, IDE discovery, code review, and reproducible application behavior.

### Application-Only Enums

The library could provide enum conversion utilities but require applications to define their own enums for the API field names. This was rejected because it would move stable API vocabulary back into every application that uses the library.

### No Enum Enforcement

The library could make enums optional conveniences and accept raw strings by default. This was rejected because it would weaken protection against known spelling and casing errors. `require_enums=False` remains available for API evolution and other compatibility cases.
