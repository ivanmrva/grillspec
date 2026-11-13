---
name: generate-api-reference
description: >-
  Publish API reference docs as static HTML from the API and event contracts — endpoints, schemas, auth, errors, examples, deprecations. Use when the API reference should be built or refreshed, on its own or inside the docs site. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the spec to generate an API reference from
---

# generate-api-reference

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill publishes the API reference from the contracts, on demand. The reference holds nothing of its own: it is built fresh from the contracts on each run and never edited by hand. Its reader is a client developer integrating against the API, not the team that built it, so write in a consumer-facing, timeless voice.

## Where the contracts are
Render from the machine-readable contract wherever the project keeps it: the OpenAPI and AsyncAPI files under `09-solution/api/` where the spec carries them, otherwise the contract package in the code. The seam index (`09-solution/api/index.md`) supplies the `API-` and `EVT-` IDs and the policies that apply across the surface (versioning, idempotency, the error model). With no machine-readable contract, build from the contract definitions in the spec and say in your report that the reference is only as exact as those definitions.

## What the reference contains
| Part | Content |
|---|---|
| per endpoint or event | method and path, or topic · summary · request and response schemas · authentication and scopes (the `SEC-` rule behind them) · status and error codes · a runnable example (curl, or a sample payload) |
| grouping | by resource or context, each entry cross-linked to its `API-`, `EVT-` and `DATA-` IDs |
| try-it | a request/response playground per endpoint. Where the site must stay purely static, say so on the page and provide importable HTTPie or Postman examples instead |
| deprecations | on each affected entry: the deprecated field or endpoint, its sunset date and its replacement, matching the `Deprecation` and `Sunset` response headers; and one changelog page collecting them across the surface |
| error catalog | one page: error code → meaning → what the client should do |

Include the deprecation and changelog parts when the contracts carry deprecations; an API with none gets no empty changelog.

## Output
Written under `docs-site/api/`. Run on its own it writes these files there; run as part of the docs site it is embedded as the API section. It is published by the docs workflow, not the app's pipeline, and it changes nothing in the spec.

| File | Captures |
|---|---|
| `index.html` | the reference home, grouped by resource or context |
| `<resource>.html` | the entries for one resource: its endpoints and events as described above |
| `errors.html` | the error catalog |
| `changelog.html` | deprecations and sunsets across the surface, when there are any |

Reads: the API and event contracts with their schemas, the `DATA-` classes and `SEC-` rules they reference, the error model and the versioning policy.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
