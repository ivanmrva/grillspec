---
name: implement-task
description: >-
  Implement one prepared task as a minimal, tested vertical slice — tests first, within architecture boundaries, code in the source tree. Use when you have a prepared task (T-NNN) to build. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# implement-task

**Load `references/exec-engine.md` first and follow it.** This skill: **implement one prepared task as a minimal, tested vertical slice** — the engine's TDD cadence, production-only bar, done-gate, and anti-cheat invariants all bind; below is only what is specific to driving a single task.

## Process
1. **Branch + open the Verification Record.** Off main (`task/T-NNN-…`); never commit to main. Generate the pre-implementation checklist — `python3 scripts/check_task_record.py spec --init T-NNN` — which materializes, from the task's frozen spec references, the obligation table you'll be held to. You see the bar before you write a line; you can't shrink it.
2. **UI slice? Open the visual contract before any test.** For a non-`N/A` `ux` dimension, load the frozen prototype + the `JRN-` journey's interaction states + the referenced `DS-` components/tokens + the `a11y` cell first — the slice's second acceptance reference (the engine's UI-contract rule).
3. **Tests first, layered.** From the acceptance criteria, write the failing tests across every layer the slice touches — unit, integration, contract, e2e — one behavior at a time, through the public interface. The task's cross-cutting cells (`SEC-`/`ENTL-` deny paths · `obs` signals — `SLO-` telemetry, `AEV-` analytics events · `DATA-` retention triggers · `ML-` evals) are test obligations written with the slice, not deferred.
4. **Implement the minimal slice.** End-to-end (entrypoint → application → domain → persistence) to green. For an empirical unknown about the slice's shape, spike a throwaway prototype first — and delete the spike before the green slice (it proves shape; it never becomes the implementation).
5. **Handle edges just-in-time.** A behavior no task anticipated → stop, record a `GAP`, resolve it (complete / `N/A` / accept a default as an ADR) before continuing.
6. **Ship the slice's deploy artifact real.** For any deployable surface the slice adds (always for the walking skeleton), produce the real CI/deploy artifact reaching the first environment of the promotion path (per `infra-ops/cicd.md` + `topology.md`); fill the `deploy` row with the evidence — the green e2e/smoke run against the deployed env — or `N/A — no new deployable surface`. If the env can't run yet: row `blocked — <env> not provisioned`, escalate per the engine; never `PASS`, never faked, never silently deferred.
7. **Run enforcers and ship.** Pre-commit → conventional commit → one MR/PR → CI → merge, per the engine's workflow. On a re-run, re-touch only the impacted code.

## Rules
- **A test-authoring task is a different shape** — its deliverable *is* the test (a system/journey acceptance test, an architecture fitness function, or an NFR-evidence test). Author it from its source spec, make it executable and able to fail, leave it guarding continuously; never fold it into a feature slice.
- **Author tests that pin behavior, not just cover lines** — for changed domain logic, assert observable outcomes strongly enough to kill mutants (the mutation gate the test run enforces); high coverage with weak assertions fails that gate. Meet the strategy's threshold here, don't bounce off the gate.
- **Contracts both directions** — for each `API-`/`EVT-` the slice consumes, author the consumer-side contract; for each it exposes, verify the provider against the published schema. Neither side ships unverified.
- **Fill the Verification Record as you go** — each obligation's evidence flips its row to `PASS`; set `status: done` only when every row is `PASS`/`N/A`.
- **Hand back the completion report** — end every task by emitting `check_task_record.py spec --report T-NNN`: a readable, tool-vouched summary that re-checks before rendering, so `✅ VERIFIED` means the steps were actually done, not merely claimed.
- **Done:** the layered suite green locally + hooks pass → hand off for the test run, then the conformance review; MR green → merge. Per the engine's bookends, the task is done only once an independent `VERDICT: PASS` for this `T-` is recorded and the Verification Record is green — you do not certify your own pass.

## Output
Written under the project source tree:

| File / target | Captures | Format |
|---|---|---|
| `src/` | the slice's implementation (entrypoint → application → domain → persistence) | — |
| `tests/unit/` | domain / logic | — |
| `tests/integration/` | adapters / persistence | — |
| `tests/contract/` | API- / EVT- schemas | — |
| `tests/e2e/` | the user-observable path | — |
| `spec/10-delivery/verification/tasks/T-NNN.md` | the per-task Verification Record — obligation table (generated `--init`, filled to `status: done`) | obligation · source · required · evidence · status |

(+ ADRs → `adr/ADR-BUILD-NNN.md` — a default accepted mid-implementation)
(walking-skeleton task only: `12-operate/bootstrap.md` — the **executable setup runbook**, composed from `infra-ops/environments.md` + `prerequisites.md` into a bulletproof, followed-step-by-step operational guide, **per platform** and **per environment**, phased:
 **A — initial** (local + dev up): per-audience steps (ops-admin/sys-admin/developer) · the **env-var worksheet** — each var: capture-from → store-in → author-per-env · bring dev up;
 **B — production / pre-launch** (deploy-release extends): prod-only credentials · DNS · scale/residency · the cross-environment differences · the go-live checklist;
 **C — later / day-2** (deploy-release extends): secret rotation · scaling · onboarding a new environment.
 Plus the operator-facing rendering of the **runtime contract** — the requirements the artifact needs to run are owned by `conventions/runtime-contract.md` (required env-vars → `environments.md`, backing services, migrations, **seed/reference data**, health-checks, ports); bootstrap composes that into the **canonical startup order**: provision → migrate → seed → set flag defaults → deploy → **`preflight`** → smoke (each phase opens with `preflight`, so a misconfigured environment is caught before traffic, not after). The walking-skeleton authors Phase A and stubs B/C; never a value, always where-to-set-it.)
*(writes CODE in the source tree — never `spec/`)*
Consumes: a single `T-NNN` + the exact spec IDs it references + the conventions + the code it touches — load only these (tight context).

## Resources
- `references/exec-engine.md`
- Worked example: `examples.md`
