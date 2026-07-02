# audit-spec `--loop` — drive the spec to zero findings

Loaded only in `--loop` mode. Repeat full-depth audit passes and **fix everything each pass finds** until
a fresh, independent batch reports **zero findings, including minor** — K=2 consecutive dry batches, not
one lucky clean pass. The SKILL.md's phases define WHAT a pass judges; this file is the convergence
harness around them: the fan-out, the dedup, the fix discipline, and the propagation that keeps every
derived layer — `10-delivery` included — following from the corrected upstream.

## One pass = one parallel audit + full remediation

1. **Baseline.** Run the mechanical tools (Phase 0 set + `spec_status.py`); record the counts. They must
   stay green throughout — the floor, not the goal.
2. **Audit — two tracks, fanned out in parallel.** The loop conflates two kinds of work with *opposite*
   economics; run them on separate axes. Pass the cumulative **seen-set** + the **do-not-re-flag** list
   into every agent prompt. **Spawn every auditor read-only** (the `Explore` agent type — no Edit/Write):
   auditors **return findings tables only; they never edit the spec**. All fixing happens in the main
   loop (step 3) *after* verification. A write-capable auditor edits the spec mid-audit, contaminates the
   working tree and every verify-before-fix read, and forces a revert-and-re-apply — never use one.

   **Track A — domain & usage completeness (stochastic · whole-spec · EVERY round · never scoped down).**
   Phase 3 is a *blind re-derivation*, not a fixpoint check: each independent run samples a different
   region of the blind-spot space, so a later run finds gaps an earlier one missed — that is how a model
   finds what's MISSING, and it stays true after a clean round. Buy coverage by sampling **wide**, not by
   looping deep: spawn **N=3 independent full-depth re-derivations of the WHOLE spec** (never
   scope-partitioned), each seeded with a different lens so the samples don't collapse onto the same
   findings:
   - **entity-lifecycle** — every entity's states, especially the abnormal terminations products forget
     (cancel · refund · dispute · expire · suspend · merge · delete/erasure · archive · fraud-hold);
   - **rule-collision + universal edge-generators** — two business rules colliding, plus
     money/time/identity/quantity/concurrency/dependents applied to the model;
   - **persona × JTBD journeys** — each real journey through its unglamorous parts (empty-state ·
     abandon-return · permission-changed-mid-action · at-scale · hit-a-limit · blocked-by-another-actor).
   **Track B — consistency & structural (near-deterministic · scoped on rounds 2+).** The Phase 0–2 work:
   contradictions · scope adherence · decision coherence · derivation completeness · contract-vs-schema
   enums/fields/ranges · typed-field agreement · reference direction · house style. **Round 1:** full
   `--scope all`, split across ~3 non-overlapping scope bundles (domain + cross-area consistency ·
   requirements + the derived solution areas · functional + UX + design-system + commercial + discovery).
   **Rounds 2+:** scope to the **previous round's change set + its reference-graph downstream** (the files
   a fix touched and everything that cites them — `impact.py` computes it) — a deterministic re-check
   never re-reads files no fix went near; round 1 certified them and they haven't moved.

   Each agent returns a grounded findings table (severity · file:line/ID · rule · concrete gap ·
   recommended fix) **or** an explicit `ZERO FINDINGS`.
3. **Dedup, then fix.** Union the findings; dedup against the cumulative **seen-set** (key:
   `file:line`/stable-ID + rule) so a finding already resolved — or judged-and-rejected — never
   re-enters. The **fresh unique** findings are this round's work. Fix every one, nits and suggestions
   included. **Verify before fixing:** read the artifact, ground the finding in its `file:line`/ID; drop
   what you can't ground — a false fix corrupts the spec.
4. **Route each fix + drain the tail NOW, not next round.** Fix-zone routing per the SKILL.md: an
   authored-zone defect is fixed in place; a derived-zone defect (`05-functional-spec/`, `09-solution/*`,
   `10-delivery/{conventions,tasks,impl-design}/`, root `CLAUDE.md`) is fixed by editing its **upstream**
   and re-deriving — never hand-patched. Then run the **fix-mode exit contract** (SKILL.md): `impact.py`
   over the changed IDs → re-run the owning derive step for **every** derived artifact in the set — the
   enumerated tail below is the checklist, `impact.py` is the authority — and register every new stable
   ID in its registries. Draining the known tail in-round is what collapses the round count; leaving it
   for the next audit to rediscover is the avoidable serial cost Track B's scoping assumes you already paid.
5. **Re-verify + re-record.** Mechanical tools back to green; then `guard_derived.py --record` (the
   re-derived paths) + `check_freshness.py --record` (all touched paths) so the baselines reflect the
   reconciled state.
6. **Log + clean up.** Append this pass's fixes to `audit-fixes-log.md` (project root), increment the run
   count, **delete `spec-audit-report.md`**.
7. **Accumulate + count dry batches.** Add the fresh unique findings to the seen-set. If the whole batch
   — all N Track-A samples **and** Track B — yielded **zero fresh unique findings**, increment the **dry
   counter**; else reset it to 0.
8. **Convergence gate — stop only on K=2 consecutive dry batches** AND a fully green mechanical baseline
   AND a final independent full `--scope all` sweep of the recurring classes (stale `X-001..NNN` range
   claims vs the current max · schema enums vs aggregate state-sets · reference direction) coming back
   clean. One dry batch is NOT enough — a stochastic finder can miss on one sample and hit on the next;
   K-consecutive across independent samples is the bar.

## The propagation tail (the checklist behind step 4 — `impact.py` is the authority)

One authored fix cascades. A new/changed domain command, state, or rule typically propagates to: the
functional `UC-`/`AC-` · the schema/data model + its enums · the API contract (endpoint + error responses)
and the event contract (channel + payload enum) · the IA screen/nav + the journey · the actor roster + the
authorization rule · the strategic event-flow — **and then the terminal derived layer**: the affected
`T-` task manifests, the conventions (when the change moves an architectural/stack/testing fact), the
impl-design of touched modules, and root `CLAUDE.md`. The terminal layer is the one a partial propagation
most often strands — it is IN scope of every drain, never "next round's problem". Expect a feature's tail
to take a round or two to drain fully; that is normal convergence, not thrashing.

## Hard-won discipline (what makes the loop converge instead of thrash)

- **Read-only auditors; only the orchestrating loop edits** — after grounding each finding itself.
- **One loop per repo — never concurrent.** Two instances (or a loop racing another spec-mutating
  session) clobber each other's working tree. Before starting, confirm nothing else is mutating the spec;
  a converged-but-uncommitted tree from another run is reconciled against, not fought.
- **Verify, don't trust — in both directions.** Ground every finding before editing; and when an agent
  *rejects* a candidate, spot-check the high-risk classes yourself — a real defect can hide behind a
  "doc-lag, defensible" dismissal (a genuinely stale ID-range claim is the classic).
- **Reference direction (the #1 self-inflicted lint break).** A fix in an upstream/authored file must not
  cite a downstream ID (`UC-`, `AC-`, `NFR-`, `OBL-`, `SEC-`, `ENTL-`, `ML-`) — use domain language there;
  the linter flags every mention, not just marked refs.
- **Dense-prose WARN.** When an edit tips a line past the linter's prose thresholds, split or convert to
  structure — don't ship the WARN and don't waive it.
- **Carry the do-not-re-flag list** across rounds (documented deferrals, deliberate numbering schemes,
  intentional gaps, framing conventions) and pass it into every agent prompt, so settled non-defects never
  resurface.
- **Deferred ≠ defect.** `deferred`/`post-MVP`/`accepted-risk`/`needs-counsel`/`needs-domain-validation`
  markers are deliberate decisions — never "fix" them.
- **New stable IDs need their registries.** A new `CMD-`/`EVT-` needs an authorization rule (or an
  explicit system/unguarded mark), a reachable + terminal-clean state machine, and — if published — a
  contract channel or a documented exclusion. A new `THR-` needs a linked `SEC-`.

## Human decisions — park, don't block

A finding that genuinely needs a fact only the user/org/counsel holds (a GTM/phasing call, a
legal/tax/finance specific, a visual/UX choice): apply a defensible default so the spec stays consistent,
record it in `human-decisions-needed.md` (the finding · the default applied · what to ratify or flip), and
keep fixing everything else. Default hard toward deciding what engineering/domain merit settles (the
engine's decision classes); escalate only genuine one-way-door facts.

## Tools

All paths `python3 ${CLAUDE_PLUGIN_ROOT}/tools/…` — the Phase-0 baseline (`lint_spec.py` ·
`spec_status.py` · `guard_derived.py` · `check_freshness.py` · `check_contracts.py`), the propagation set
(`impact.py`, `guard_derived.py --record`, `check_freshness.py --record`). When running standalone in a
project that vendors the tools, resolve them from the project's own tools folder instead.

## Guardrails

- **No commit/push unless the user explicitly asks.** On the default branch, branch first.
- Edit only `spec/` (+ the lock files under `.claude/` and the root meta files this mode owns); never edit
  code; never hand-edit a derived artifact — root `CLAUDE.md` included.
- The three root meta files (`spec-audit-report.md` · `audit-fixes-log.md` · `human-decisions-needed.md`)
  are transient and git-ignored — meta-commentary, never committed spec content.
- Interrupted mid-loop: resume from the current working tree (the locks + the fixes log are the record) —
  never reconstruct from git history.
