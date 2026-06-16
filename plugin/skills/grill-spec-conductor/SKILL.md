---
name: grill-spec-conductor
description: >-
  START HERE to spec, design, model, plan, or build a project, product, or feature end-to-end — the single front door and orchestrator for the whole idea-to-spec-to-architecture-to-tasks-to-code-to-operate workflow. Use when starting from an idea or from scratch, when the scope is the whole project rather than one area, or when you don't know which step you need: it scans the spec, re-derives the current state, and recommends or asks which area to work next. Owns the cross-area dependency order, the readiness gates, the global glossary/actors and consistency, the discovery/validation overlay, the pivot loop, and the lite path. Prefer this over any individual grill-, derive-, or exec- skill whenever the work spans more than one area. Run this first.
---

Each area is the skill **`grill-<id>`**. The shared engine is `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`;
the decide-vs-ask classifier is `${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md` (the convergence test);
the output tree + owners + modes are in `${CLAUDE_PLUGIN_ROOT}/grill-shared/repo-layout.md`. You orchestrate; the
area skills + engine interview. Everything writes into one `spec/` repo.

## Situational modes & deep-dives → `conductor-playbook.md`
For these, **read `${CLAUDE_PLUGIN_ROOT}/grill-shared/conductor-playbook.md`** and follow it (same authority as here): **doc-first start**, **migrate mode**, the **lite path**, **changing already-built work** (software change management) + **entry modes / small-change fast-path**, the **operations / production lifecycle**, and the **progressive-elaboration** deep-dive. Core routing (front door, stage map, gates, per-run loop, linter, cross-area reconciliation) stays here.

## Session start — the single front door
Invoke this to begin. On invocation:
1. **Run the linter** (`python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py`), then **scan + re-derive** (below):
   spec-health per area + the bet-health register. Linter ERRORs are authoritative for
   structure/headers/refs/placeholders — fix or surface them before anything else.
2. **Ask which area to focus on — an option menu, never an open prompt.** Build it from the scan:
   the **recommended next area** (default), **resume** an in-progress area (with open count), **fix
   cross-area issues** (if found), **go test/clear the riskiest assumption** (from bet-health), **a
   specific area I name**, or **migrate existing docs**. Once the implementation-readiness gate passes,
   add **prepare delivery** (derive-conventions → derive-tasks); once delivery-readiness passes, add **work
   the next task** (implement → run-tests → conformance-review, in build-order). Show blocked areas
   as unavailable + what unblocks them. Ground every suggestion in what the scan found.
3. **Run the chosen area yourself.** The area skills are reference docs (`disable-model-invocation: true`), **not dispatchable agents** — there is no handoff. You **load that skill's `SKILL.md` + its shared engine and execute the interview/derivation in-line** (or delegate to a subagent you spawn with that skill text as its brief), handing it its input and its target slot. **One focus per session;** finish or park, then re-run.
**Never silently start an area the user didn't choose.** Don't dump all areas — surface the few.

**Parallel sessions.** The user may run several Claude Code sessions at once. Keep them safe: **one area
per session** (above), **prefer a branch per session/area**, and since **each area owns its own output folder**, parallel areas don't contend on shared files. Real conflicts resolve at **git merge**; on the next run after a merge you **recompute the cross-area state from the repo** (each area's output is the record). See `${CLAUDE_PLUGIN_ROOT}/grill-shared/operator-map.md`.

## You own the structure; the skills don't - hand each its input and its target
The area skills are **self-contained units that know nothing about this system** - no gates, no tree, no awareness of you or each other. All orchestration is yours. They are **reference docs you load and run** (not agents you hand off to); whether you execute one in-line or in a subagent you spawn, you give it the same brief:
- **Give it its input.** Gather the existing artifacts it should build from (its upstream, by stable ID) and hand those over as its input. It uses what you give it; it never reaches for a required set itself, and it works behind no gate - **you** decide readiness and sequence, it just produces.
- **Give it its target.** Tell it the **working root** (`spec/`) and the **exact location** for its artifact - its slot in the tree from `${CLAUDE_PLUGIN_ROOT}/grill-shared/repo-layout.md`. It writes there; you own the layout, it does not.
- **Harvest from its output.** It writes one self-describing artifact — its own glossary and actors where it has them, ADRs to the shared `adr/` — to the slot you gave it. You read that output to pick up terms, actors, bets, and decisions; there are no companion files to merge. Then reconcile the cross-area glossary view and run `lint_spec.py` + `guard_derived.py`, check cross-area consistency, and drive propagation (`${CLAUDE_PLUGIN_ROOT}/tools/impact.py`) across dependents. None of that is the skill's job - it is all yours.

The same skills, handed no input and no target, run standalone for someone who copied just a few of them; driven by you, they compose into one consistent `spec/`.

## Dashboards (report the relevant ones — they're orthogonal)
- **Spec health** — per-area maturity (L0–Ln) + invariants (is the spec consistent & complete-enough?).
- **Bet health** — the bets recorded across area artifacts: of the *critical* ones, how many are
  Validated / Testing / Accepted-risk / Untested / Invalidated; plus kill-criteria status and PMF
  signals. A green spec next to a red bet is the point — keep them visibly separate. *Spec consistent*
  ≠ *bet validated.*
- **Delivery health** (once in Stage 4–5) — tasks todo / in-progress / done / blocked, conformance
  pass-rate, next gate. The execution loop follows `build-order` (dependencies first); the conductor
  hands each execution skill a **tight context** (the task + its referenced spec IDs only) so the
  coding agent stays efficient.

## Dependency graph — zero → right before source code (stages = folders = one skill each)
```
STAGE 0 · DISCOVERY (runs FIRST · continuous · never closes)
        discovery            problem hypothesis · DVF bets recorded in the artifact · value-prop fit · PMF plan
STAGE 0 · FOUNDATION (elicited)
        product-vision       vision · positioning · COARSE scope · phasing · GTM motion       → 02-product/vision/
        customer-discovery   segments · personas · JTBD  (seeds actors.md)                   → 02-product/customers/
        market               competitors · alternatives · differentiation · sizing          → 02-product/market/
        goals                north-star · success metrics · KILL-CRITERIA                    → 02-product/goals/
        constraints          mandates · regulatory · environment (DDD only as context)      → 03-constraints/
        system-context       scope · external actors · neighbor systems · interfaces · C4 L1 → 03-system-context/
STAGE 1 · DOMAIN
        ddd                  the hub; seeds glossary + actors                                → 04-domain/ddd/
STAGE 2 · REQUIREMENTS (derive[domain] + reference[product,constraints] + elicit deltas)
        derive-functional (projected from ddd) · quality · data-reqs · integration-reqs · security-reqs · ux-reqs · design-system (DS-) · compliance (OBL-) · ml-reqs (AI features · ML-)  → 05-requirements/*
STAGE 2½ · COMMERCIAL (GATED on functional)
        monetization         business model · pricing · plans · entitlements · unit economics → 06-commercial/
PARALLEL · GTM + GROWTH (commercial execution + post-launch loop, not core spec)
        go-to-market         channels · launch · partnerships                                → 07-gtm/
        growth               activation/retention model · experiment backlog (EXP-) · analytics events → 08-growth/
        ───────────────── ARCHITECTURE-READINESS GATE ─────────────────
STAGE 3 · SOLUTION (the how)
        derive-architecture · derive-data-architecture · derive-api-contracts ·
        derive-security-architecture · derive-infra-ops · derive-test-strategy · derive-observability (SLO-) · derive-ml-architecture (AI)   → 09-solution/*
        (architecture fixes the module map + seam contracts; module INTERNALS are designed per-slice in execution — derive-impl-design is JIT, not a Stage-3 area)
        ───────────────── IMPLEMENTATION-READINESS GATE ─────────────────
STAGE 4 · DELIVERY PREP (build the agent's runway)
        derive-conventions   standards · dependency/boundary rules · DoD · build/test cmds · CLAUDE.md → 10-delivery/conventions/
        derive-tasks         minimal vertical slices (T-NNN) · walking-skeleton first · build-order DAG  → 10-delivery/tasks/
        ───────────────── DELIVERY-READINESS GATE ─────────────────
STAGE 5 · EXECUTION (per task, in build-order; CODE lives in the repo, NOT spec/)
        (slice flagged design-first → derive-impl-design designs its modules → 09-solution/impl/)  →  implement-task  →  run-tests  →  conformance-review  →  done    (loop; any red routes back)
        autorun         autonomous driver · runs that loop across the whole task queue (AFK) · stops only on a true blocker (HITL trigger)
                                                                            conformance-review → 10-delivery/verification/
        ──────────── RELEASE-READINESS CHECKLIST (advisory) ────────────
STAGE 6 · OPERATE & MAINTAIN (real/prod systems · feeds back to discovery)
        deploy-release  (rollout/rollback) · migrate-data (on DATA-/AGG- change) · operate-incident (learnings → assumptions/gaps)
        diagnose (hard bugs: feedback-loop → reproduce → hypothesise → fix+regression)
                                                                            operational records → 10-delivery/operations/
ANY STAGE · prototype (throwaway spike to answer ONE question empirically — resolves a gap/assumption instead of guessing → resolutions/assumptions/ux/ADR)
ANY STAGE · generate-docs / generate-api-reference / generate-ui-prototype (project the spec → the full-project docs site · the API reference · the slice's clickable UI prototype (per slice); regenerated on change — consumed by readers/clients and the build)
cross-cutting views (reconciled by reading outputs):  glossary, actors, bets, the risk + technical-debt register, decisions
```
**Stage purity:** each leaf folder is the exclusive output of one skill/stage; nothing co-located
across stages. The only cross-stage shared location is `adr/` (one file per ADR, so two skills never collide).

**Key edges:** discovery → product-vision · product-vision.scope → which ddd contexts exist · product-vision.motion (PLG vs sales-led) → ux · security · monetization ·
customer-discovery.personas → actors · constraints → bounds all · personas + neighbor-systems → system-context (the boundary) → ddd + integration + C4-L1 · ddd → all requirements · functional →
**monetization** (no priceable features ⇒ don't ask) · ddd flows + functional → quality, ux,
goals (refinement) · ALL requirements + product + monetization → solution (the gate) · derive-architecture →
the other solution areas · functional + data → ml-reqs (AI) → derive-ml-architecture · brand seed / provided tokens → design-system (DS-) → ux journeys + ui-prototype (per slice) → tasks/build · architecture seams + a design-first slice → derive-impl-design (JIT in execution) → module internals.

## Topic readiness — don't ask what isn't answerable yet
A topic is offered only when its prerequisites have **content**, not when its area is merely
"started." This stops premature interrogation — **never ask about subscriptions before any product
function exists.** Mechanism (reuses Deferred, pointed at sequencing):
- Prerequisite empty ⇒ **don't offer**; record **Deferred** with trigger "prerequisite `<area>` has
  content." Tracked, not forgotten, never asked early. Gate individual topics, not just areas.
- **Active promotion:** each run, promote any Deferred item whose trigger is now met — surface it
  ("`functional` now has content → monetization is unlocked; want to set plans?").
- **Seed caveat (reverse trap):** at foundation, don't over-ask either — `product-vision` scope is
  *coarse & revisable*; accept "roughly these areas," mark low-maturity, let it sharpen via
  `functional`. Scope matures across the process; it is not a perfect up-front gate.

## Gates (five)
1. **Desirability gate (soft, early):** don't pour effort into deep speccing until the riskiest
   *desirability* assumptions are at least **named with a test plan** (not necessarily passed). Stops
   speccing a product nobody's checked anyone wants.
2. **Architecture-readiness gate (requirements → solution):** every foundation + requirements +
   monetization area `done` & cross-area-consistent, **and** every *critical* assumption `Validated`
   or explicitly `Accepted-risk` (logged). You may proceed on accepted risks; not on un-acknowledged
   ones. When proceeding on accepted risk, **flag scoping the first build (MVP) to test it cheaply.**
   (`gtm` may trail — not a code prerequisite.)
3. **Implementation-readiness gate (solution → delivery prep):** all solution areas `done` &
   consistent — incl. the architecture's **module map + seam contracts** (module *internals* are
   designed per-slice in execution via `derive-impl-design`, not gated here). The spec is now
   buildable — proceed to **delivery prep**.
4. **Delivery-readiness gate (delivery prep → execution):** `derive-conventions` done (standards,
   dependency/boundary rules, build/test/lint commands, DoD, `CLAUDE.md`) **and** `derive-tasks`
   done — a walking-skeleton task exists and is first, every in-scope use-case is covered by ≥1 task,
   every task traces to spec IDs + has acceptance + DoD + dependencies, and `build-order` is acyclic.
   → ready to code.
5. **Per-task done (execution loop):** for each `T-NNN` in build-order (dependencies first):
   `implement-task` → `run-tests` (suite green, every `AC-…` exercised) → `conformance-review`
   (boundaries, contracts, data, security, NFR/ASR honored; traceability complete). All green = done;
   any red routes back to `implement-task`; a failure exposing a spec gap raises an Open and may
   re-open upstream (the pivot loop, for implementation).

## Cross-area consistency (a single skill can't do this)
Per-area Open lists are caches; the truth is recomputed over the whole repo. Consistency is
**non-monotonic across the graph** — a correct new fact can retroactively break another area. Route
any break to the owning area as Open: renamed term / split actor in ddd → may invalidate
security/ux/functional; a plan in monetization with no entitlement rule in ddd → gap; an NFR
referencing a removed flow → dangling ref; a security rule naming a missing actor → broken ref.

## Pivot loop (market-driven non-monotonicity)
An `Invalidated` critical assumption (from the market) becomes a high-priority Open that ripples
**upstream** — it can re-open scope, vision, even ddd. Route it to the owning area(s) for re-grilling,
exactly like a cross-area inconsistency but sourced from reality. This is why discovery never closes:
the world keeps invalidating things you thought you knew.

## Each run, the conductor
1. **Run `${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py`** — its ERRORs are the authoritative structural truth
   (closed-world paths · file headers · dangling local links · placeholder/stale tokens · duplicate
   cross-area term · invalid bet status · Deferred-without-trigger); its WARNs are candidates you
   judge (readiness-vs-reality · gate order · prose). Then **read the area outputs** (their recorded bets, gaps, and decisions) and **scan the repo** for the *semantic* consistency the
   linter can't see. 2. **Re-derive** cross-area state incl. cross-references; flag downstream of any
   changed upstream as "needs recheck"; recompute bet-health. 3. **Report both dashboards** + unlocked
   / blocked / nearest gate + the single riskiest untested assumption. 4. On the user's pick, load and
   run the area skill yourself (or migrate / a cross-area fix / an assumption-test plan); update your readiness view.

**System self-feedback (the run improves the plugin, not just the spec).** If at any point this run hits friction that is a **defect or gap in this system itself** — a linter check that is demonstrably wrong, a skill instruction that contradicts another or cannot be satisfied, an ID type the schema needs but the linter rejects, a path a skill is told to write that the structure won't allow, a stale tool/doc reference — **do not silently work around it and do not record it in any `spec/` artifact** (the spec must stay free of awareness of this system). Capture it: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py --add --kind bug|gap|improvement --component <skill/tool/engine> --summary "…" --detail "…" --suggest "…" --evidence <file:line>`. It appends to **`GRILLSPEC-FEEDBACK.md` at the project root** (a sibling of `spec/`, never inside it) for the plugin author to triage — capture-and-route, never self-patch. Keep the bar high: a real contradiction or a rule that demonstrably can't be satisfied, not a mere preference. When the file has entries, note their count in your end-of-run report.

## Skill kinds — interview vs derivation vs execution (and what each must NOT do)
- **Interview (`grill-*`)** — elicits facts only the human/market has (vision, domain, the *values*
  behind requirements: NFR numbers, retention, authz rules, acceptance criteria). May ask.
- **Derivation (`derive-*`)** — generates **strictly from the recorded spec**; **never interviews**.
  Decides engineering trade-offs with ADRs, surfaces high-impact ones for *ratification* (review, not
  interview), and on a missing/contradictory input **raises a gap to the owning interview skill** (you
  re-open it) rather than asking or inventing. **Before running a derivation skill, confirm its inputs
  exist** — if not, route to the upstream interview skill first. (This is why `constraints` must capture
  stack mandates *and preferences* — so `derive-architecture` has everything and needn't ask.)
- **Execution (`implement-task` · `run-tests` · `conformance-review`)** — act on the code repo;
  governed by `exec-engine`. Code lives in the repo, never in `spec/`.

## Task readiness & order — phasing × dependencies (how scope/release priority enters)
Two distinct things govern *which task next* and *in what order*:
- **Technical dependencies** (`build-order` DAG) — a **hard** constraint: never start a task before
  the tasks it `depends:` on are done. The **walking-skeleton task is always first.**
- **Product phasing** (`product-vision` MVP/near/deferred, tagged on each task) — the **soft** priority
  *within* what dependencies allow: MVP-phase tasks first, then near, then deferred. This is how
  **scope / release priority enters implementation order** (*which* features ship first). Release
  *dates / sprints* stay out of scope; only the priority ordering is used.
→ **Next task = the highest-priority (earliest-phase) task whose dependencies are all done.**
A task is **ready to implement** only when **every applicable dimension** in its package is **either an
ID-ref, `N/A — why`, or a consciously *resolved* gap** (behavior · domain · data · api · ux · security ·
nfr · integration · placement · tests · DoD). Missing detail is **not** a silent blocker and is **not**
forced upfront — it's recorded as `GAP … UNRESOLVED` and **surfaced at this task (the last responsible
moment), forcing the user to complete it, mark it N/A, or accept a default (ADR)**. A task with **any
`UNRESOLVED` gap is not implementation-final and cannot be coded** (lint-enforced). The conductor hands
`implement-task` only the task + its referenced spec IDs (tight context).

## Change propagation (ALWAYS on, self-triggered — not a step you wait to be told to run)
Every change — from an interview, a derivation, a ratified decision, or an operational learning — **must
flow to everything that depends on it, down to code, automatically and in the same session.** This is
reflexive, not optional, and not deferred. The traceability spine (stable IDs + references) IS the
dependency graph.
1. **Detect what changed yourself** — the IDs/files you just touched, or run `git diff` / `python3
   ${CLAUDE_PLUGIN_ROOT}/tools/impact.py --since <ref>` so the system *recognises its own changes* without being told.
2. **Compute the impact set** — `python3 ${CLAUDE_PLUGIN_ROOT}/tools/impact.py <changed-IDs…>` returns the minimal
   transitive set of downstream **spec files · tasks · code**, ordered upstream→downstream.
3. **Record + mark stale** — record what changed (git is the changelog); mark the set `status: stale · superseded-by-
   change` in your readiness view / the affected artifacts / tasks.
4. **Re-process only the impact set, incrementally** (diff, don't regenerate): re-grill deltas →
   re-derive (reading existing ADRs, applying a delta) → re-finalize affected tasks → re-run execution
   for affected code. Nothing outside the set is touched. **When a re-derivation rewrites a derived
   artifact** (anything under `09-solution/`, `05-requirements/functional/`, `10-delivery/conventions|tasks/`, or
   `CLAUDE.md`), **run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/guard_derived.py --record <those paths>`** so the
   derived-guard sees a legitimate regeneration and doesn't false-block the commit.
5. **Re-verify:** `lint_spec.py` + `guard_derived.py` + `conformance-review`.
Default end-state: **nothing stale remains.** Skills may be invoked directly (that's fine) — but *any*
skill that makes a change owns steps 1–5; the engines bake this in so it happens whether or not the
conductor is driving.

## ▣ RELEASE-READINESS CHECKLIST (advisory — *you* decide when to ship)
**The system has no concept of "release".** It does continuous spec + code work; promoting to
production is **your action, outside the system** (`deploy-release` runs it when you choose). This is
just the checklist to consult *when you decide to ship* — nothing here blocks you: every MVP-phase task
`done` & merged · a clean **`conformance-review --full`** pass · NFR/ASR targets have **test evidence**
(not assertions — load/soak as applicable) · `derive-observability` done (SLOs + alerting + runbooks) ·
required `migrate-data` tasks done · critical `OBL-`/`SEC-` verified · UAT/acceptance signed off by the **named sign-off owners** (legal · security · product, per the stakeholder/decision-rights table) — a gate has a real person to ask, not "the team".
Surfaced on Dashboard C as a readiness view, not a lock.

## Earn your place — no redundant layer (when is an area N/A?)
An area produces its artifact **only if a layer below consumes it**; otherwise mark it **N/A**, don't
fill it. (This is the test for "do we need use-cases?": `functional` earns its place because it
produces the **`AC-` acceptance layer** that `derive-tasks`, `derive-test-strategy`, and
`conformance-review` all reuse — assembled once with stable IDs instead of re-projected from raw `ddd`
in every task. If a project's `ddd` ever made that projection add nothing, `functional` would be N/A.)
Apply the same test everywhere: a layer that produces nothing a downstream layer reads is overhead.

## Consistency linter (deterministic backbone)
`${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py` (stdlib, no deps) mechanically checks what shouldn't need judgment, so
re-validation is trustworthy at scale. It **complements, not replaces, you:**
- **ERROR** (ground truth — hard violation): file outside the structure · missing/empty
  `scope|excludes|format` header · dangling local link · placeholder/stale token (`{{`, TODO, NNNN) ·
  duplicate cross-area term · invalid bet status · Deferred with no trigger · **reference to an
  undefined ID** · **illegal downward reference** (a file referencing a layer it shouldn't) ·
  **ID defined in more than one place** (define once) · **ID defined outside its owning directory** · **a child ID whose keyed parent is missing** (AC->UC, ASR->NFR)
  (mechanical stage-purity / no-unrelated-content) · **unresolved `GAP … UNRESOLVED` in a task** (the
  last-responsible-moment forcing checkpoint). Non-zero exit (use in CI).
- **WARN** (you judge): marked-done-but-empty · content-but-not-started · architecture-before-gate ·
  dense prose blocks · **structural coverage gaps** — an element with no downstream reference
  (every `CMD-`→`UC-`, `UC-`→`AC-`, `AC-`→test, `AGG-`→`DATA-`, `OBL-`→control, …). *This WARN set is
  the mechanical gap-detection surface for structural completeness; unknown-unknowns still need the
  interview/test/prod layers.*
- **INFO** (still your job): event→consumer, entitlement→feature, term-used-but-undefined are
  *semantic* — the conductor judges these, **unless** skills emit machine refs (`[t](path)` /
  `ADR-<PREFIX>-NNN`), which the linter *does* verify.
Run it at session start and each run, before trusting any cached state.

## Cross-area reconciliation (no shared singletons)
There are **no shared mutable singletons**. Each area writes its own self-describing artifact; **`glossary.md`** and **`actors.md`** are deliverables only in the areas whose job is to define them — the **domain model** owns the canonical ubiquitous language and domain actor roster, **customer-discovery** owns personas/system-users, **system-context** owns the external/boundary actors + neighbor systems, and (optionally) **design-system**/**compliance** keep their own UI/regulatory lexicons; most areas own neither. **All ADRs** live in the **one shared `adr/`** folder, each filename prefixed with its area code (`ADR-<PREFIX>-NNN`) so no two skills collide. The conductor **reads the area outputs** and reconciles across them: it **maintains the system-wide `glossary.md` and `actors.md` at the spec root** (reconciled from the per-area ones — one term/one meaning; personas ↔ domain roles ↔ boundary actors unified into one roster), derives the **global ADR index** from `adr/` (every `ADR-` reference resolves; every filename carries a registered prefix), and harvests the **bet register** and **risks** inline from the artifacts. **No file may exist at a path not listed in `repo-layout.md`** — on scan, relocate or merge any stray file. Every file opens with its `<!-- scope: … | excludes: … | format: … -->` header; style is tight, structured, ubiquitous-language, **no prose**, and **prefer a Markdown table whenever the content is even loosely tabular** — the glossary, actor roster, ADR index, and readiness dashboards are all tables, because tables are the most scannable form for the reader.

**What the conductor itself writes** (reconciled at the spec root — it owns no area artifact):

| File (spec root) | Captures |
|---|---|
| `glossary.md` | system-wide ubiquitous language, reconciled from the per-area glossaries (one term / one meaning) |
| `actors.md` | the unified actor roster (personas ↔ domain roles ↔ boundary actors merged) |
| `_readiness.md` | the per-area readiness dashboard (status per area · which gates are met) |

DERIVED-by-reading the area outputs (NOT stored as files): the **global ADR index** (from `adr/`), the **bet register**, the **risk + technical-debt register** (each entry: category · probability · impact · owner · mitigation · status / paydown-trigger), and the **decisions log**. The conductor writes **no ADRs of its own** and **no area artifact** — every area artifact belongs to its worker skill.
