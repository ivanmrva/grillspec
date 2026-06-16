# conductor-playbook — situational modes & deep-dives

Loaded just-in-time by **`grill-spec-conductor`** when the session is in one of these modes; the conductor keeps the core routing. Same authority as the conductor — follow it when in-mode.

## Doc-first start — backfill the stages a doc presupposes
A doc rarely enters at Stage 0. A feature/requirements doc *presupposes* a domain model, actors, and
a scope; an architecture doc presupposes requirements + NFRs + a model. When you ingest a downstream
doc and its upstream stages are empty, **reverse-derive the implied upstream artifacts** and seed them
— clearly tagged `derived-from: <doc> · confidence: inferred · status: unconfirmed` — then **grill to confirm them
before trusting the downstream.** Migration runs *both* directions: scatter across peer areas **and**
back-fill upstream — never leave the foundation blank just because the doc started mid-pipeline.
Rules: mark every inference unconfirmed; raise each as Open or an assumption; never present inferred
upstream as settled; once confirmed upstream, the downstream becomes trustworthy. Reverse-derive only
what the doc actually implies — don't fabricate vision/strategy a feature list can't support (those
stay Open for elicitation, not invented).

## Migrate mode — bring an existing body of docs in
Per-area ingestion points one area at a file; migration **scatters** one mixed pile across many areas.
1. **Inventory** — list sources, classify each by which areas it feeds (one → many is normal); show
   the map before writing. 2. **Scatter in dependency order, ddd first** — read all sources, take only
   each area's fragments through its scope fence. If a source enters downstream and upstream stages
   are empty, **back-fill upstream** (see Doc-first start) — don't leave the foundation blank. 3. **Seed the domain glossary + actors first** (in the ddd area;
   raise assumptions). 4. **Tag provenance + confidence** (`source:`, `confidence: stated|inferred`,
   `status: unconfirmed`) — these are **transient migration scaffolding**, not permanent prose: the grilling pass (step 7) resolves them away. What survives in the artifact is at most a light `inferred` marker on an unconfirmed fact; durable provenance lives in the readiness view and hotspots, not as inline "produced by …" narration (which the house style bans). 5. **Reconcile across sources → Open** (contradictions, dangling
   refs, assumption gaps). 6. **Scope fence applies** — drop impl/GTM/roadmap mixed in. 7. **Grill the
   deltas** (flips `status: unconfirmed` to Resolved/Open) — running each area's full coverage lens over the migrated content, same depth as a fresh interview, sorted into settled / needs-clarification / contradiction, not a file-move plus a provenance tag. Expect it to look worse before better:
   it makes hidden debt legible. Garbage in is garbage migrated — now visible.

**Parallel-drafting checklist (when several subagents draft sibling files at once — multi-context ddd, a scatter migration).** Hand each unit these four rules up front; they are the exact failure modes that turn one clean pass into a multi-pass ID reconciliation:
- **Disjoint numeric bands per unit** — context A mints `AGG-2xx`, context B `AGG-3xx`; no two drafters reuse a number.
- **Bare type prefix only** — `AGG-250`, never `<CTX>-AGG-250` (a namespaced ID silently fails to register).
- **ID is the leading table column** (the row key) — a name-first row leaves the ID undefined and its references dangling.
- **Lint each unit before integrating** — run `lint_spec.py` on each draft on its own; resolve its ERRORs before merging siblings, so cross-file "undefined ID" noise doesn't pile up.

## Lite path (small products)
Don't force the apparatus. Offer: `discovery` (name the bet) + `product-vision` (1-pager, incl. coarse
scope) + `ddd` + a merged `quality`+`context` note → minimal `09-solution/arch`. Everything else stays
Deferred/N-A until warranted. A whole area may be **N/A** — record it.
**What still applies vs what you skip:** spec-governance stays on automatically (the `lint_spec.py` +
`guard_derived.py` GitHub Action — free, no setup) and `09-solution/arch` is still a **guarded derived
artifact** (regenerate-only); but you can **skip the two-tier test rig, the fitness-function suite, and
the full `code-ci.yml` pipeline** (keep one plain test job) until the project grows into them. Lite means
fewer areas and lighter ceremony — not a different system.

## Progressive elaboration, the per-layer ratchet, and where edge cases are actually found
Upfront completeness is neither achievable nor desirable — edge cases surface late, and some areas
(often UX) are legitimately thin or N/A. So: **specify coarse early, elaborate just-in-time, track every
deferral so it can't be lost.**

There is **no single forcing checkpoint** — that's a trap (task-spec is an *assembly* step; an edge you
couldn't see while modelling you usually can't see while wiring references either — you just rediscover
it at implementation). Instead the rule is a **per-layer ratchet: no artifact at any layer is *final*
while it carries an `UNRESOLVED` gap**, enforced at *every* layer. Edge cases have **four discovery
sites, each with its own active mechanism — don't rely on one:**
1. **Domain rules** → the interview engine's **stress-testing** ("what happens if…"). Primary upfront.
2. **Structural gaps** (every `CMD-` has a `UC-`, every `UC-` an `AC-`, …) → **coverage checks** in the
   linter. Mechanical; they *find* what's missing rather than wait for it.
3. **Behavioral edges** → **active test design** in `derive-test-strategy`: boundary-value, equivalence
   partitioning, property-based, and fuzz testing **manufacture** edges instead of waiting for prod. A
   failing/owned property that has no rule raises a gap upstream.
4. **The rest** → **production**, fed back through the maintenance loop as new gaps/assumptions.

Task-spec is the **last *pre-code* ratchet** (carried `at-task` gaps are forced to a decision there —
complete JIT / N/A / accept-ADR), and implementation is the **deepest** one. But the *test layer is the
primary behavioral-edge discovery engine* — treat it as discovery, not just verification. Net:
thin/absent upstream content is allowed, but **no artifact at any layer is finalized, and no task is ever
coded, past a gap it needs.**

**An empirical unknown is resolved by a `prototype`, not by guessing.** When a gap or a DVF assumption
turns on something asking can't settle — does this state model hold up, is this approach feasible, does
this UX flow work — the right move is a **throwaway spike** (`prototype`) that answers the one question;
its verdict lands in the artifact / a bet-status update / `ux` / an ADR. This is a first-class
resolution alongside complete-JIT / N/A / accept-default.

## Changing already-built work (software change management)
When the impact set includes a task that is `done` / implemented, do **not** silently mutate code.
Run the standard change process:
- **Record the change** — git history (always: what changed · when · impact set), **plus**
  an **ADR** *only if the change embodies a decision* (why we chose this) — they're different records.
- **Revise or supersede the task** — update the `T-NNN` manifest to the new spec; if the change is
  large, create a **follow-up task** `T-NNN' supersedes: T-NNN` rather than overloading the original.
- **Mark the code `needs-rework`** and re-run the loop for that slice: `implement-task` (amend
  code+tests to the new spec) → `run-tests` → `conformance-review`.
- **Re-evaluate** the task's phase/priority and dependencies; **update `traceability.md`.**
Records persist (ADRs + git history) for audit and for future runs.

## Revising a per-slice artifact (UI prototype · impl-design)
Both are produced JIT per slice and **regenerated from a source, never hand-edited** — so a change is recorded in the *source*, then the artifact re-renders. There is no separate "change request" file you author: you steer the regeneration, and the regenerated artifact (+ an ADR for any decision, + git) **is** the record.
- **UI prototype** (`prototypes/ui/<screen>.html`) is **kept** — the exact visual+interaction reference the coding task builds against, not throwaway — but it is a **projection**. Record the change in its source, then regenerate the screen:
  - flow · screen states · what's shown · microcopy → the **UX requirements** (`journeys.md` · `information-needs.md`)
  - a component's look · a token (colour/spacing/variant/state) → the **design system**
  - *exploring* (you don't yet know what you want)? the **throwaway spike** (`prototype`) is the disposable one — its chosen direction lands in the UX requirement, then the kept prototype regenerates from it. (Two different prototypes: the disposable explorer vs this kept projection.)
- **impl-design** (`solution/impl/<module>.md` — derived & guard-protected) — re-run the design for that slice:
  - **internals** (algorithm · concurrency · error handling) → re-run `derive-impl-design` with the new direction; the updated design lands in `solution/impl/<module>.md`, a load-bearing choice as an `ADR-IMPL-NNN`, the rest in git.
  - **the seam** (the module's public interface · role · dependency direction) → that's an **architecture** change, not an impl-design one: raise a gap → change the module map in the architecture → regenerate downstream.

Then: **in flight** (slice not built) → just regenerate and continue; **already built** → the change process above (`impact.py` → revise/supersede the task → `needs-rework` → re-run the slice's loop).

## Entry modes & the small-change fast-path
The conductor is the front door for greenfield, but **skills are independently invocable** and three
entry modes are first-class:
- **Greenfield (full):** zero→market, walk the stages with gates.
- **Focused change (the fast-path — use for most ongoing work):** enter at the *single artifact that
  changes* (a new rule, a price tweak, one new feature). Don't re-walk the tree. Make the change →
  **auto-propagate** (impact.py over the minimal subgraph) → only the *gates that apply to the touched
  subgraph* re-check. A one-feature change touches a thin vertical slice of the graph, not all 30+
  areas; "earn your place" keeps the rest N/A. This is the lightweight path — the propagation machinery
  *is* the fast-path.
- **Brownfield / import (assess existing):** point the system at existing code/docs → reverse-derive a
  *partial* spec (actors, contexts, contracts, data model from code) → seed every unknown as a tracked
  gap → then proceed in focused-change mode. Don't pretend a clean greenfield upstream exists.

**Gates are readiness signals, not locks.** Skills are independently invocable, so you may run any
derive/exec skill whenever you like (e.g. to preview output before its upstream is settled). Whatever it
produces is just a normal artifact — committed to git like anything else; if its upstream later changes,
the **same propagation + linter** keep it consistent. No special status, no extra bookkeeping.

## Operations, maintenance & the production lifecycle (spec → build → run → maintain)
Delivery does not end at merge. The lifecycle continues onto **real/prod systems** and feeds back:
- **Observability** (`derive-observability`): SLO/SLIs, logs/metrics/traces, alerting, dashboards,
  runbooks — derived from `quality` NFRs and the architecture.
- **Deploy/release** (`deploy-release`): promote a built increment through environments with an explicit
  rollout/rollback strategy; smoke-verify in the target env.
- **Data migration** (`migrate-data`): **mandatory** whenever a `DATA-`/`AGG-` change lands — derive-tasks
  emits a migration task and `conformance-review` (conformance lens) requires it. (Schema/data change with no migration is a
  data-loss bug.)
- **Incident response** (`operate-incident`): triage via runbooks; **capture every learning as a new
  assumption or gap** → it propagates back upstream. This closes the loop to discovery (site 4 above).
- **Maintenance** (a recurring *focused change*, not a new phase): dependency/security patching,
  deprecations, tech-debt — each is a change-event run through the propagation machinery, with its own
  ADRs + git history. Time passing on a live system is modelled as a stream of focused changes.

