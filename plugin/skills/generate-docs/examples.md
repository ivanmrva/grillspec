# generate-docs — worked example

Illustrative. Publishing the docs site for a `standard` project with a UI and an API. The outline below is what lands under `docs-site/`; each section is tagged with its mode.

| Mode | Section | Built from |
|---|---|---|
| tutorial | Getting started: book your first repair, end to end | the book-a-repair journey and the setup runbook |
| how-to | Reschedule a job · Issue a refund · Add a branch · Wire up webhooks | the use-cases and journeys |
| how-to | Bring up an environment · Respond to a checkout outage | `12-operate/bootstrap.md` and the incident runbook |
| reference | Requirements by ID: use-cases and criteria, quality, data, security, obligations, design system | the requirement areas |
| reference | API and events | `api/`, built by the API-reference step and embedded |
| reference | Criterion → test trace · Task status | the output of `check_task.py spec --trace` and `--json` |
| reference | Glossary | the domain glossary |
| explanation | Overview: vision, goals, constraints, system context | the foundation areas |
| explanation | Domain model: context map, aggregates, events (Mermaid) | the domain area |
| explanation | Solution: architecture, module map and seams, storage, security, environments, objectives, the test tiers | the solution areas (decision records, on this profile) |
| explanation | Implementation design, grouped by module | the design notes under `10-delivery/impl-design/` |
| explanation | Decisions | the ADRs |

Root: `index.html` with the navigation, every section cross-linked by stable ID, and a version selector (v1.0 · v1.1) because releases are tagged. `assets/` holds the CSS and JS.

One documentation gap was reported instead of filled: there is no source in the spec for a "Rotate the payment gateway credentials" guide, since the setup runbook's day-2 phase is not written yet.

The project has no ML area and no commercial area in its spec, so the site has no pages for them.
