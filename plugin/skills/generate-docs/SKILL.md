---
name: generate-docs
description: >-
  Publish the project's documentation as a self-contained static HTML site built from the spec — tutorial, how-to guides, reference and explanation, with the API reference and the consolidated implementation design. Use when the docs site should be built or refreshed. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the spec to generate a docs site from
---

# generate-docs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill publishes a static documentation site from the spec tree, on demand. The site holds no decisions and mints no IDs: everything in it comes from the spec, the ADRs and the tests' trace tags, so it is built fresh on each run and never edited by hand. Its reader was not in the room when the spec was written; write in a timeless voice for them.

## What the site contains
Organize the site by what a reader comes to do, not by the spec's folders. The spec areas feed these four modes:

| Mode | For a reader who wants to | Built from |
|---|---|---|
| tutorial | learn by doing: a getting-started path through one core journey | the main use-case and its journey, the setup runbook |
| how-to | get a task done | use-cases, journeys, runbooks and operations records |
| reference | look something up | all requirements by ID (`UC-`/`AC-`, `NFR-`/`ASR-`, `DATA-`, `SEC-`, `OBL-`, `DS-`, `ML-`), the API and event reference (`API-`/`EVT-`), the data classes, the glossary, the criterion → test trace |
| explanation | understand why it is built this way | vision and goals, constraints, system context, the domain model, the solution architecture and the other solution areas, the implementation design, the commercial model, the ADRs |

Cover every area the project has; its profile decides which exist, and an absent area gets no empty page. Ship at least the getting-started tutorial and the key how-to guides beside the reference and explanation content, and tag each section with its mode.

Three parts need assembling rather than copying:

- **The implementation design.** Design notes are written per slice (`10-delivery/impl-design/`), so gather them into one section grouped by module or subsystem, so the design reads as a document and not as per-task fragments.
- **The criterion → test trace.** It is computed from the tree: run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec --trace` and render its output. `--json` gives the task status for a status page.
- **The API reference.** When the project has `API-` or `EVT-` contracts, build it with `generate-api-reference` and embed it under `api/`, cross-linked by ID, so the docs ship as one bundle. With no API surface, leave it out.

When releases are tagged, add a version selector so a reader can open the docs for the version they run.

## Rules
- **Assemble, do not author.** A tutorial or how-to is sequenced from material already in the spec. If a guide is needed and the spec has no source for it, report that as a documentation gap; steps or decisions invented for the site would be documentation of a system that was never specified.
- **Self-contained and deterministic.** A navigable static site with assets from a CDN (Tailwind, Mermaid), cross-linked by stable ID, buildable headless with no interaction, so it can run in CI.
- **Publishing is separate from the app's pipeline.** The intended wiring is a docs workflow (for example `.github/workflows/docs-site.yml`, deploying to GitHub Pages) that rebuilds and publishes `docs-site/` when the spec changes on the default branch.

## Output
Written under `docs-site/` at the repo root, outside `spec/`. The spec is read and not changed.

| Target | Captures |
|---|---|
| `index.html` | the site root: sections cross-linked by stable ID, each tagged by mode; the version selector when releases are tagged |
| `tutorial/` | the getting-started tutorial |
| `how-to/` | the task and operations guides |
| `api/` | the embedded API reference, when contracts exist |
| `assets/` | CSS and JS |

Reference and explanation pages sit beside these, one per area or topic, named for what they cover.

Reads: the whole `spec/` tree, the ADRs, and the output of `check_task.py`.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
