---
name: generate-api-reference
description: >-
  Generate API reference docs from the API-/EVT- contracts — endpoints, schemas, auth, errors, examples — as static HTML. Embedded in the doc-site or standalone. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the spec to generate an API reference from
---

# generate-api-reference

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **project API reference docs (static HTML) from the contracts**.

## Process
1. **Render from the contracts** — per endpoint/event: method+path / topic, summary, request & response schemas, auth & scopes, status/error codes, and a runnable example (curl / sample payload). Group by resource/context; cross-link each entry to its `API-`/`EVT-`/`DATA-` IDs. Where an OpenAPI/AsyncAPI artifact exists in `09-solution/api/`, render from it; otherwise generate from the contract definitions.
2. **Interactive try-it console** — give each endpoint a request/response playground the reader can fire. If a hard static-only constraint holds, **state that constraint explicitly** and ship importable **Postman / HTTPie** examples as the fallback.
3. **Surface changelog + deprecations** — a changelog plus, on each affected entry, the **deprecated fields/endpoints · sunset date · replacement link**, mirroring the **`Deprecation`** and **`Sunset`** HTTP response headers.
4. **Error-catalog page** — a consolidated page mapping **error code → meaning → remediation** across the surface.

## Rules
- **Regenerate wholesale** — a pure projection of the contracts: rebuild from scratch each run. Timeless, consumer-facing voice (the reader is an API client, not the team).
- Embedded in the doc-site as its API section, or standalone; deployed by the same spec/doc-governance workflow, not the app pipeline.

## Output
Written under `docs-site/api/` (regenerated wholesale from the API/event contracts; no spec changes):

| File / target | Captures | Format |
|---|---|---|
| `index.html` | API reference home — grouped by resource/context, linked to API-/EVT-/DATA- IDs | — |
| `<resource>.html` | per resource/endpoint/event: method+path / topic · summary · request & response schemas · auth & scopes · status/error codes · runnable example (curl / payload) · try-it console (or, static-only, Postman/HTTPie import) · deprecation note (deprecated fields · sunset date · replacement link, per the `Deprecation`/`Sunset` headers) | — |
| `errors.html` | consolidated error catalog: error code → meaning → remediation | — |
| `changelog.html` | API changelog + deprecations/sunsets across the surface | — |

(embedded as the API section when the doc-site build runs it; standalone it writes the same files under docs-site/api/)
Consumes: the API/event contracts — `09-solution/api/` (`API-` REST/RPC endpoints, `EVT-` events) + their request/response schemas (`DATA-` where referenced) + auth/authz (`SEC-`) + error models + versioning — read-only, never edits the spec.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
