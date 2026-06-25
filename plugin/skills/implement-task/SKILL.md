---
name: implement-task
description: >-
  Implement one prepared task as a minimal, tested vertical slice — tests first, within architecture boundaries, code in the source tree (not the spec). Use when you have a prepared task to build. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: a prepared task (T-NNN) to implement
---

# implement-task

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **implement one prepared task as a minimal, tested vertical slice** — tests first, inside the boundaries, code in the source tree.

## Process
1. **Branch + open the Verification Record.** Off main (`task/T-NNN-…`); never commit to main. Generate the pre-implementation checklist — `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task_record.py spec --init T-NNN` — which materializes, from the task's **frozen** spec references, the obligation table you'll be held to (`spec/10-delivery/verification/tasks/T-NNN.md`, every row `PENDING`). You see the bar before you write a line; you can't shrink it.
2. **Tests first, layered.** From the acceptance criteria, write the failing tests across every layer the slice touches — unit (domain/logic), integration (adapters/persistence), contract (`API-`/`EVT-` schemas), e2e (the user-observable path). One behavior at a time, asserted through the public interface.
3. **Implement the minimal slice.** End-to-end (entrypoint → application → domain → persistence) to green. For an empirical unknown about the slice's shape, spike a throwaway prototype first.
4. **Handle edges just-in-time.** A behavior no task anticipated → stop, don't guess; record a `GAP` and resolve it (complete / `N/A` / accept a default as an ADR) before continuing.
5. **Run enforcers and ship.** Pre-commit runs the checks → conventional commit → open one MR/PR → CI → merge. On a re-run, re-touch only the impacted code.

## Rules
- A **test-authoring task is a different shape** — its deliverable *is* the test (a system/journey acceptance test, an architecture fitness function, or an NFR-evidence test). Author it from its source spec, make it executable and **able to fail**, leave it guarding continuously; never fold it into a feature slice.
- **Author tests that pin behavior, not just cover lines** — for changed **domain logic**, assert observable outcomes strongly enough to **kill mutants** (the mutation-score gate the test run enforces on changed logic); high coverage with weak assertions fails that gate. The test strategy sets the threshold — meet it **here**, don't bounce off the gate.
- **Contracts both directions** — for each `API-`/`EVT-` the slice **consumes**, author the consumer-side contract (the consumer-driven expectation); for each it **exposes**, verify the provider against the published schema. Neither side ships unverified.
- **Spike code is deleted before the green slice** — a throwaway prototype proves shape only; delete it, then re-drive the behavior with tests (it never becomes the implementation).
- Code lives in the source tree, never in `spec/`.
- **Fill the Verification Record as you go** — each obligation's evidence (the test path, the measured number, the verdict reference) flips its row to `PASS`; set `status: done` only when every row is `PASS`/`N/A`. `check_task_record.py --task T-NNN` is a gate: a done-claim with an unmet/dropped obligation, an unevidenced path, or no independent verdict **fails**.
- **Hand back the completion report** — end every task by emitting `check_task_record.py spec --report T-NNN`: a readable, **tool-vouched** summary (✓ per AC→test, contracts, security, NFR, coverage, no-fakes, conformance verdict). It re-checks before rendering, so `✅ VERIFIED` means the steps were actually done, not merely claimed — the artifact a human opens to confirm the task.
- **Done:** the layered suite green locally + hooks pass → hand off for the test run, then the conformance review; MR green → merge. **The task is not done on your own say-so** — it is done only once an **independent** conformance review has recorded `VERDICT: PASS` for this `T-` under `spec/10-delivery/verification/` **and the Verification Record is green**. You write the slice and its tests-first; you do **not** certify your own pass and skip the review. Report status; never mark done on red, never mark done without that recorded verdict and a green record.

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
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
