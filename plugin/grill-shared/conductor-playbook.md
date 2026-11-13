# conductor-playbook — situational modes

Loaded by `grill-spec-conductor` when a session is in one of these modes; the conductor keeps the core routing. Follow the section that applies.

## Entry modes
Three ways in, all first-class:
- **Greenfield** — from an idea: settle the profile and delivery mode, then walk the in-profile areas in dependency order.
- **Focused change** — the normal mode for ongoing work: enter at the one artifact that changes (a new rule, a price, one feature), make the change, let `impact.py` name what depends on it, and re-work only that. A one-feature change touches a thin slice of the graph.
- **Brownfield** — existing code or docs: reverse-derive a partial spec from what is there (actors, contexts, contracts, the data model as the code has it), record every unknown as a gap, then continue in focused-change mode. "Existing" means the current working tree; missing prior work is a gap to re-elicit. Keep it lean here too: write the decisions and rules the code cannot tell a reader, not a prose copy of the code.

## Adopting an existing project
A project that already has code is adopted once; after that it is ongoing work. Two cases.

**It has never used this system** — follow Brownfield above, and stop early. The code already holds the description, so write only what it cannot tell a reader: the product scope and non-goals, the domain vocabulary and invariants, the rules a later change must not break (authorization, retention, entitlements, quality targets), and the costly-to-reverse decisions as ADRs. A `lite` or `standard` profile is nearly always right. Acceptance criteria are written for behaviour as it is next changed, not back-filled for everything that exists.

**It was built with an earlier major version** — the spec exists and is larger than the current layout wants. The mechanical part is one command, a dry run until `--apply` is given:

`python3 ${CLAUDE_PLUGIN_ROOT}/tools/migrate_project.py --profile <p> --delivery <d>`

It writes the project settings, carries each task's status into its brief, removes the verification ledger, the locks and dangling host links, vendors the current tools, and prints the linter's findings grouped by check. Then work through that list by removing what has no reader, not by completing it:
- edit-trace stamps and change notes go (the fact stays; git has the history);
- an area beyond the profile, or a full-mode solution file, goes once nothing reads it — search the project's own scripts for the path first, because a project gate may parse a spec file (a tier contract, an environments matrix, a contract file), and that file stays until the script is repointed;
- open briefs get a tier and a status when they are next worked on; finished ones need nothing;
- the agent guide is rewritten short with `derive-conventions`.

Areas are not re-derived to bring them up to date; each is amended when a change reaches it. Expect the project to use a small part of the system from then on: the conductor in ongoing-work mode, `derive-tasks` and `implement-task` for each change, `derive-impl-design` and `conformance-review` for critical ones, and the interview skills only when a change needs a fact the spec does not hold.

## Starting from a document
A document rarely enters at the first stage. A feature list presupposes a domain model, actors and a scope; an architecture document presupposes requirements. When you ingest a downstream document and the areas above it are empty, derive the upstream facts it implies and seed them marked `inferred` and `status: unconfirmed`, then confirm them with the user before trusting what sits on top. Derive only what the document actually implies; a feature list cannot support an invented strategy, so that stays open for the interview.

## Migrating a body of docs
Per-area ingestion points one area at one file; a migration spreads a mixed pile across many areas.
1. Inventory the sources and show which areas each feeds, before writing anything.
2. Work in dependency order, the domain model first; take only each area's content through its scope fence, and back-fill upstream areas a source presupposes.
3. Seed the domain glossary and actors first.
4. Mark provenance while migrating (`inferred`, `status: unconfirmed`); these marks are scaffolding that the next step resolves away, not permanent prose.
5. Reconcile contradictions and dangling references across sources into open points.
6. Run each area's interview over the migrated content at the same depth as a fresh one — sorting it into settled, needs-clarification and contradiction — rather than filing it. Expect the result to look worse before it looks better: hidden debt becomes visible.

Migration is also the moment to drop what has no reader: change history, status narrative, content that restates code, and areas outside the profile do not come across.

When several subagents draft sibling files at once (a multi-context domain model, a migration), give each a disjoint numeric band for its IDs (context A mints `AGG-2xx`, context B `AGG-3xx`), the two ID rules from `house-rules.md`, and have each draft linted on its own before integrating, so cross-file "undefined ID" noise does not pile up.

## Elaborate just in time
Completeness up front is neither achievable nor useful: edge cases surface late, and some areas are legitimately thin or absent. Specify coarsely early, elaborate when a consumer needs it, and record each deferral with the trigger that reopens it so it cannot be lost.

Edge cases are found in four places, each with its own mechanism:
1. Domain rules — the interview's stress-testing ("what happens if…").
2. Structural gaps (a command with no use-case, a use-case with no criterion) — the linter's coverage checks.
3. Behavioural edges — test design: boundary values, equivalence classes, properties. A failing property with no rule behind it raises a gap upstream.
4. The rest — production, fed back as new gaps and bets.

No artifact is final while it carries an `UNRESOLVED` gap, and no task is coded past a gap it needs; the task brief is the last point before code where a carried gap is forced to a decision. An unknown that asking cannot settle — does this state model hold, is this approach feasible, does this flow work — is answered by a throwaway spike (`prototype`); its verdict lands in the artifact, a bet status, or an ADR.

## Changing already-built work
When the impact set includes a task that is done:
- Update the spec where the change belongs; record a decision as an ADR only when the change embodies one. Git carries what changed and when.
- Bring the task up to date: revise its brief, or for a large change write a follow-up brief that depends on it. Set the affected brief's status back from `done`.
- Re-run the loop for that slice: amend code and tests to the new criteria, run the gate, and review again if the tier requires it.
- Re-check the task's phase, tier and dependencies.

## Revising a prototype or a design note
- **UI prototype** (`prototypes/ui/<screen>.html`) is kept: it is the visual and interaction reference the build task works against. Change what it shows at its source — flow, states and microcopy in the ux requirements; a component's look or a token in the design system — then regenerate the screen and review it again. When the user does not yet know what they want, explore with a throwaway spike first; the direction it finds lands in the ux requirement.
- **Design note** (`10-delivery/impl-design/…`) covers a critical slice's internals: update it with `derive-impl-design` when the approach changes. A change to the module's public interface, role or dependency direction is an architecture change: make it in the module map, and let the note follow.

If the slice is not yet built, regenerate and continue; if it is built, follow "Changing already-built work".

## Operations and maintenance
Delivery does not end when code lands.
- **Deploy and release** (`deploy-release`) — promote a built increment along the project's promotion path with a rollback path, and verify it with the smoke check in the target environment.
- **Data migration** (`migrate-data`) — owed whenever a change alters stored data; a schema change with no migration is a data-loss bug.
- **Incidents** (`operate-incident`) — work the incident, then capture what it taught as a gap or a bet in the owning area, and as a new gate when a rule would have prevented it. This is how production feeds discovery.
- **Maintenance** — dependency and security patching, deprecations, debt paydown: each is a focused change, usually `routine`.
