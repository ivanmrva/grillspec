# exec-engine — shared core for build/verify skills (NOT an interview)

The shared method behind every exec profile. The profile's `SKILL.md` is the entrypoint and names what varies (the task, scope, what it touches); this engine is the judgment that's the same for all of them — the TDD cadence and test layers, the autonomous done-gate, the workflow, and what to decide vs. ask.

**Your output is code and reports in the project source tree** — that, plus your ADRs in the shared `adr/` folder, is the record; there is no side ledger. On a re-run you resume from the current state of the code and tests, not from memory.

**The baseline is the current workspace, nothing else.** Implement, verify, and resume against the **working tree exactly as it exists now** — the spec, code, and tests on disk. **Never** treat **git history** (old commits, `git log`/`git show`, stashes, branches, reflog) as a source of truth to reconstruct from: a removed file is **gone, not a recoverable draft**; "it used to work" is settled by the current code, not a past version; missing prior work is a **blocking gap to escalate**, not something to restore from history. (Routine git *mechanics* — branching/committing per the workflow below, or `git bisect` to localise a regression in `diagnose` — are fine; this fence is about what you treat as the baseline.) Likewise **never read or write outside the project folder** — no parent dirs, home dir, sibling repos, or absolute paths beyond the workspace root — **unless the user explicitly hands you that input**.

## Tight context (efficiency — what keeps a coding agent fast & accurate)
Load only the task, the exact spec IDs it references, and the code it touches — nothing more. A bloated context is slower and less accurate; precision is the discipline.

## Honor the spec — don't reinvent it
**Work from the task's *scoped* references — do NOT load the whole spec.** A coding slice is **construction, not synthesis**: it needs exactly its acceptance criteria, the domain elements it realises, the contracts/schema at its boundary, the architecture boundaries it must respect, and the conventions — that scoped set. You **may pull a specific upstream artifact on demand** if a boundary is unclear, but never ingest all upstream layers: market/GTM/business-model and unrelated requirements are *noise* that degrades focus and accuracy (irrelevant — especially topically-adjacent — context measurably hurts focused work). Scope tight; retrieve just-in-time. (Broad upstream context belonged to the *synthesis* that drew this slice's edges — the architecture and the task breakdown — not to building it.)
Implement to the referenced spec IDs exactly (domain model, contracts, data model, security rules, NFR/ASR decisions). If the spec is wrong, contradictory, or missing for this slice, **STOP and raise it** — record the blocking gap on the task and escalate to re-open the source spec; never silently diverge.

## Edge cases discovered while coding (the deepest last-responsible-moment)
Code reveals edge cases no model anticipated — expected, not a failure. When you hit an **undecided behavior** mid-implementation, **stop, don't guess**: record a `GAP <what's undecided> — <owning area> — UNRESOLVED` on the task and resolve it just-in-time one of three ways — **complete it** (elicit the rule/UX — it lands in the source spec), **mark N/A** for this slice, or **accept a default** (an ADR in `adr/`). The task is implementation-final again only once the gap is resolved. Never encode an invented behavior to keep moving. The same rule covers a **missing or inadequate design-system element** a UI slice needs (a component/variant/token the design system lacks): that is a `GAP … — design-system — UNRESOLVED` raised to the design system — **never bespoke-styled in code to keep moving** (the conventions forbid raw values / ad-hoc styling anyway); resolve it by extending the design system (which then propagates to the prototype + code) or marking it N/A for this slice.

## Incremental + always propagate
On a re-run after a change, **re-touch only the impacted code** (the change set you're given) — don't rewrite green, in-boundary code; re-run the tests and the conformance check on exactly the impacted slices.

## Architecture boundaries are law
Respect bounded-context boundaries, layering, and the dependency rules in your conventions. No cross-boundary shortcuts — long-term architecture is preserved only by enforcing these on **every** task.

## TDD & vertical slices — the red → green → refactor cadence
Build one **minimal vertical slice** at a time, end to end (entrypoint → application → domain → persistence); no horizontal layers, no big-bang. Within a slice, work the tight TDD micro-cycle — **never write production code without a failing test that demands it**:
1. **RED** — write ONE small test for the next bit of observable behavior (from an `AC-` or a test-strategy edge); run it, watch it fail for the right reason. A test you didn't see fail proves nothing.
2. **GREEN** — the **minimal** code to pass; the smallest version, not the elegant one.
3. **REFACTOR** — only **with the suite green** (never while RED): improve names, structure, and duplication without changing behavior, re-running after each step.

**Don't batch.** Writing all tests then all code is horizontal slicing and produces tests that assert imagined behavior and pass when behavior breaks. One test → one implementation → repeat. Tests assert **observable behavior through the public interface, not internals** (the warning sign of a bad test: it breaks on a behavior-preserving refactor). Each `AC-` → at least one test; an edge discovered here becomes a test (and, if it reveals an undecided rule, a gap).

## The slice's test set spans every layer it touches — produced WITH the code
A tracer bullet cuts through all layers, so its tests must too. Produce the full set with the slice, per your test strategy's levels:
- **unit** — domain logic, invariants, pure functions (fast, no I/O; the bulk).
- **integration** — the adapters and persistence the slice adds (real DB/queue via a test container or a double); the boundary to an external system.
- **contract** — every `API-`/`EVT-` the slice exposes or consumes (schema, versioning), provider- and/or consumer-side.
- **e2e** — the slice's user-observable path end-to-end (one happy path + the load-bearing edges; kept few, they're expensive).

Still TDD and one-at-a-time within each level, still behavior through the interface. An `NFR-`/`ASR-` target gets its **evidence test** here, not an assertion. These are the **per-slice (Tier-A)** tests; cross-feature journeys, architecture fitness functions, and NFR-evidence runs are the **system suite (Tier-B)** — owned by the test strategy, seeded by the walking-skeleton task, run in CI.

## What a good review checks (the MR/PR gate, not just CI green)
Before merge, confirm: behavior matches the referenced `AC-` and contracts · architecture **boundaries and dependency rules** intact · tests assert behavior (not internals) and cover the edges · names use the **ubiquitous language** · no dead code, no scope creep beyond the task. A green pipeline is necessary, not sufficient — these are the human-judgment checks it still owes.

## Code lives in the repo, not in spec/
Your code and tests live in the project source tree. The spec is the source of truth you implement to; you never edit it to match your code (if it's wrong for this slice, escalate). Your ADRs — in the shared **`adr/`** folder, prefixed with your area code (`ADR-<AREA>-NNN`) — record genuinely emergent implementation decisions.

## Definition of Done (every task)
The **layered test set** green (unit/integration/contract/e2e as the slice warrants) · conforms to architecture (the conformance check) · builds and lints clean · spec-lint clean · referenced NFR/security rules **evidenced** · traceability updated. Report your status; **never mark done on red**.

## Autonomous done-gate & self-correction loop (AFK execution)
For autonomous work, don't stop at the first failure or hand back a half-done task — **drive it to a fully green gate yourself, fixing your own code**, and stop only on a true blocker.

**The done-gate (run as ONE gate — the same set CI runs):** build · format · lint · type-check · unit · integration · contract · e2e · **architecture fitness functions** · spec-lint · the derived-file guard · **the conformance check (code vs spec & arch) clean** · **every `AC-` exercised by a passing test** · traceability updated. Done only when **all** are green.

**The loop — repeat until fully green or you escalate:** (1) run the **whole** gate, collect **all** failures; (2) diagnose each to root cause; (3) **fix the implementation code**, re-run the whole gate; (4) if the failure set didn't shrink for two consecutive iterations, or you hit the cap, **stop and escalate** — don't thrash, don't reach for a shortcut.

**Anti-cheat invariants — violating any means NOT done, even if everything is green:**
- **Fix the code, never move the goalposts.** Never delete or weaken a test or assertion, lower a coverage threshold, add `skip`/`xfail`/`ignore`, loosen a lint/type/fitness rule, or stub a function to fake a pass. A test changes **only** when the *spec* changed.
- **The spec is the source of truth.** Never edit the spec or an `AC-` to match buggy code; if the spec is wrong or ambiguous for this slice, **escalate**.
- **Green ≠ done.** Passing tests are necessary, not sufficient: the conformance check (judged independently of test colour) must pass, and every `AC-` must be exercised by a real test.
- **Never disable a gate, fitness function, or hook** to make progress.
- **Clean architecture always wins — never degrade structure to pass a test.** Fix failures **inside the designed boundaries**; you may not cross a context or layer boundary, reach into another module's internals, bypass a port/repository, fatten an interface, duplicate logic, introduce a cycle, or add a hack — even to make a test green. If the clean design genuinely can't satisfy the test/`AC-`, that's a **design/spec signal — escalate**, not a licence to hack.

**Escalate (stop autonomy) only when:** the spec is genuinely ambiguous or contradictory for this slice · a HITL input is truly required (a visual/UX decision, a product/legal/strategy call, an external credential/access) · the clean design can't satisfy the test/`AC-` without crossing a boundary · the loop can't converge after the cap. Append to the batched human-input queue (`spec/_human-input.md`): the task id · the precise blocker · **the actionable step-by-step resolution** (for a credential/access/provisioning block, exactly what to create and where to set it — never the secret value; for a UX or decision block, your **proposed default for the human to ratify**) — detailed enough to clear in one sitting without guessing. Mark the task `blocked`, and move to other AFK-eligible tasks. Never mark done on red; the CI run on the PR is the backstop, not the bar.

## Engineering workflow (standard practice — from conventions)
Per task: **branch off main** (`task/T-NNN-…`, never commit to main) → write the layered tests first → implement → **pre-commit hook runs the enforcers** (spec-lint · format · lint · type · secret-scan · fast tests · the mechanical conformance and fitness functions on the changed scope) → **conventional commit** → **open one MR/PR** → **CI** (build · full tests · full conformance · gate checks) → review → **merge** (auto-merge on green only where the conventions' review policy permits solo-merge; where it mandates ≥2-person review / branch protection, an `afk:eligible` agent parks the merge for a human rather than self-approving) → **deploy to dev → e2e/integration pipeline + docs site built**. Small, atomic, reversible — the *checks* aren't optional, the *release* decision is the team's.

## House style
Reports and artifacts: tight, structured, prose to clarify not walls; use the ubiquitous language; cite spec IDs. **Prefer a Markdown table whenever the content is even loosely tabular** — anything repeated over a set of items (results, gate checks, failures, IDs, mappings, AC×status) is a table, not a bullet list or prose, because tables are the most scannable form for the reader; reach for other readability structures (fenced code, a small diagram) where they fit better. **Where a table's row defines an ID-keyed record (a traceability row), the ID is the leading column** (the row key), and IDs you cite use their **bare type prefix** — never a context-namespaced `<CTX>-TYPE-NNN`. **Any artifact you write under `spec/` (a verification or operations record) opens with the `<!-- scope: … | excludes: … | format: … -->` header, like every spec file** (code under `src/`+`tests/` does not). When you implement or verify against an external **standard/format/protocol** (a WCAG level, an API/security standard), target its **current / latest stable** version, never a pinned historical one. **A record you write under `spec/` (a verification or operations record), and every ADR, is a timeless source of truth — it states what is true now, never the document's own history.** A reader has no idea it was generated, by what tool or in how many passes, so leave no development trace: never tag content with its edit history (`new` / `newly added` / `now` / `previously` / `no longer` / `expand→contract`), never note what *this* pass added, moved, cut, or deferred, never write `this round` / `as discussed`. The same word stays legitimate as **domain language** (a `new booking`); it is banned only when it narrates the document's own evolution. When you update such a record, **re-author it as a coherent whole** — integrate the change where it belongs, never append it and leave the rest; the result reads as if written in one pass, and emphasis marks meaning by the record's convention, never that something was just added. (A transient run-report back to the orchestrator may of course say what changed — that is not a `spec/` artifact.)

## System friction → plugin feedback, never your artifact
If you hit a defect or gap in **this system itself** — a check that's demonstrably wrong, an instruction you can't satisfy, a conformance rule that contradicts the spec it's checking — **don't silently work around it**; append it via `python3 ${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py --add --kind bug|gap|improvement --component <this skill/the tool> --summary "…" --suggest "…" --evidence <file:line>` (it writes `GRILLSPEC-FEEDBACK.md` at the project root, outside `spec/`). Capture-and-route for the plugin author; never self-patch.

---

# Deciding vs. asking

What you DECIDE vs. what you escalate is defined once, for every skill, in **`${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md`**. **Load it and apply it to every fork.** In one line: default hard toward **deciding** what engineering merit settles; raise a **gap** only for a fact the user/org/platform holds that the spec can't carry; pick the conventional option for inconsequential taste.
