---
name: derive-api-contracts
description: >-
  Produce machine-readable API and event contracts — an `openapi.yaml` (latest-stable OpenAPI), an `asyncapi.yaml` (latest-stable AsyncAPI), schemas and versioning — from the published language and integration requirements. Use when the published language and integration requirements exist and you need the API/event contracts derived. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-api-contracts

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **API & event contracts** — a machine-readable spec in the **latest stable OpenAPI**, an event spec in the **latest stable AsyncAPI**, their schemas and versioning.

## Method
1. per endpoint + published event + external boundary: the contract, written **into the spec files** (not prose)
2. schema (request/response/envelope) authored as the specs' component schemas
3. versioning + compatibility strategy

## Rules
- contracts are **real machine-readable specs**, not prose: REST → `openapi.yaml`, async → `asyncapi.yaml`
- every endpoint has an error model in **RFC 9457 `application/problem+json`**, idempotency keys, pagination/filtering, per-endpoint authz scopes (`SEC-`), and rate-limits; webhooks carry signing/HMAC + retry/dedupe
- **every operation carries the traceability extensions** so the contract binds to the spec ID graph: `x-grillspec-id: API-NNN` (the endpoint's own id), `x-serves: [UC-… / CMD-…]` (what it serves — no orphan endpoint), and a per-operation `security` scope (mark a deliberately open endpoint `x-public: true`); async channels carry `x-grillspec-id: EVT-NNN`. These are what the contract checks resolve against the rest of the spec
- every published event has an envelope (id·type·version·time·correlation+causation·source), declared delivery & ordering, schema-evolution rule, and dead-letter
- versioning + compatibility-test strategy defined (additive-only, deprecation+sunset, consumer-driven contract tests)
- non-REST styles (gRPC/GraphQL) are contracted via their own IDL, **referenced** from `index.md`, not re-specified here

## Output
Written under `solution/api/`:

| File | Captures | Format |
|---|---|---|
| `openapi.yaml` | REST endpoints (`API-`) · component schemas · error model = **RFC 9457** `problem+json` · idempotency keys · pagination/filtering · per-endpoint authz scopes (`SEC-`) · rate-limits · the `webhooks` object (signing/HMAC + retry/dedupe) | latest-stable OpenAPI YAML |
| `asyncapi.yaml` | async channels (`EVT-`) · event envelope (id·type·version·time·correlation+causation·source) · delivery & ordering · schema evolution · dead-letter | latest-stable AsyncAPI YAML |
| `index.md` | rationale · versioning policy (scheme · additive-only compat · deprecation+sunset · consumer-driven contract tests) · target REST maturity & whether hypermedia/HATEOAS is in scope · cross-links to `API-`/`EVT-`/`DATA-` IDs · note on non-REST styles (gRPC/GraphQL) contracted via their own IDL, referenced not re-specified | rationale + versioning |

ADRs → `adr/ADR-API-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the published/ubiquitous language + the integration requirements + the per-operation `SEC-` authz scopes.

## Excludes
implementation code

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
