---
name: derive-api-contracts
description: >-
  Decide the API and event contract policy — the seam list, versioning and deprecation, error model,
  idempotency, pagination, event envelope and delivery — and at the regulated profile also author
  openapi.yaml and asyncapi.yaml. Use when the published language and integration requirements exist.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-api-contracts

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to the **API & event contracts**: the seams the system exposes, and the policies every seam follows.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the versioning and error policy are rows in `arch/solution-strategy.md`, the rest is in the conventions |
| `standard` | decision mode | `index.md` |
| `regulated` | full mode | `index.md` plus `openapi.yaml`, `asyncapi.yaml` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the contract package in code, which is the machine contract — and once code exists that package is the source of truth for request, response and event shapes. Decision mode therefore records only which seams exist and the policies they share, and an OpenAPI or AsyncAPI document is generated from the package when a consumer needs one; full mode authors both documents in the spec, because at `regulated` they are deliverables other teams and auditors read.

## Decision record
`index.md` is written in both modes and carries:
- **the seam list** — one row per endpoint (or group of closely related operations), webhook or external boundary, defining its `API-` id; a published event is a row keyed on its `EVT-`. Every row names what it serves (`UC-`/`CMD-`), so no endpoint exists without a use-case or command behind it, and its authorization scope (`SEC-`); a deliberately open seam says so in its scope cell;
- **versioning** — the scheme, additive-only compatibility, the deprecation and sunset window, and consumer-driven contract tests as the compatibility check;
- **the error model** — RFC 9457 `problem+json` for HTTP unless a constraint says otherwise;
- **conventions**, where the product has the concern — idempotency keys · pagination and filtering · rate limits · webhook signing with retry and dedupe;
- **events** — the envelope (id · type · version · time · correlation and causation · source), the delivery guarantee and ordering, schema evolution, dead-lettering;
- **style** — a non-REST seam (gRPC, GraphQL) is contracted in its own IDL and referenced here, not re-specified.

## Rules
- The deprecation and sunset window is a ratify-point. It is a commitment to external consumers that cannot be taken back, so propose a concrete window with its reason and surface it as the engine describes.
- Full mode: the two YAML files are real machine-readable contracts at the latest stable OpenAPI and AsyncAPI, and everything the seam list promises appears in them. Each operation carries `x-grillspec-id: API-NNN` (the seam-list row it belongs to), `x-serves: [UC-… / CMD-…]` and a per-operation `security` scope, or `x-public: true` for a deliberately open endpoint; each async channel carries `x-grillspec-id: EVT-NNN`. These extensions are what the contract check resolves against the rest of the spec. An id is defined in `index.md`; in YAML it is a reference.
- Full mode also records in `index.md` the target REST maturity and whether hypermedia is in scope.

## Output
Written under `solution/api/`. The rows marked `full` are written only at `regulated`; in decision mode their content is not raised.

| File | Mode | Captures | Format |
|---|---|---|---|
| `index.md` | decision | the decision record above | seam table keyed on `API-`/`EVT-`: seam · kind · serves · scope; one short table or section per policy |
| `openapi.yaml` | full | REST endpoints · component schemas · the error model · idempotency keys · pagination/filtering · per-endpoint scopes · rate limits · the `webhooks` object | latest stable OpenAPI YAML |
| `asyncapi.yaml` | full | async channels · the event envelope · delivery and ordering · schema evolution · dead-letter | latest stable AsyncAPI YAML |

ADRs → `adr/ADR-API-NNN.md`
Consumes: the published/ubiquitous language · the integration requirements · the per-operation `SEC-` authorization scopes.

## Excludes
implementation code · in decision mode, request/response/event shapes (the contract package in code states them)

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
