---
name: implement-task
description: >-
  Build one task as a minimal, tested vertical slice — tests first, inside the architecture's boundaries, code in the source tree. Use for a task brief (T-NNN), or a routine change that has none. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# implement-task

**Load `references/exec-engine.md` first and follow it.** This skill builds one task as a minimal, tested vertical slice. The engine holds the method — how much process the task's risk tier owes, the test-first cadence, real production code, what done means, how work lands. Below is only what is specific to driving a single task.

## What you build from
A task brief, `spec/10-delivery/tasks/T-NNN.md`, is one `field | value` table written to be built from on its own:

| Row | What it tells you |
|---|---|
| `tier` | `routine` · `feature` · `critical` — how much process the task owes (the engine's risk-tier table) |
| `phase` · `status` | when it is due and whether it may run unattended; where it stands |
| `outcome` · `behavior` | the user-visible result, and each use-case with its acceptance criteria, criterion text inline |
| `touches` · `rules` | the modules, seams, tables and screens it changes; the cross-cutting obligations that bind it, each with a one-line statement |
| `non-goals` · `tests` · `depends` | what it deliberately leaves out; the test tiers and load-bearing edges; the tasks that come first |
| `ux` · `a11y` · `prototype-review` | UI slices only: journey, screens, named states and prototype path; the accessibility path; whether a human has seen the screen |
| `human-prereq` · `design` · `review` | where needed: a credential or config key; the design note to write first; the independent review's result |

A `routine` change (a bug fix, a copy tweak, a refactor, a dependency bump) has no brief. The request is its scope and the engine's `routine` row is its whole process.

## Process
1. **Check the brief is buildable.** Its dependencies are done, it carries no `UNRESOLVED` gap, and any `human-prereq` reads `provisioned` in `spec/_provisioning.md`. If something is missing, set `status` to `blocked — <why>`, say what would unblock it, and stop there; otherwise set `status` to `in-progress`.
2. **Design note first, where the brief asks for one.** A `design` row reading `design-first — <path>` names a short note under `10-delivery/impl-design/`. If the note does not exist yet, write it with `derive-impl-design` before the first test, then build to it.
3. **For a UI slice, open the visual contract before the first test.** The prototype screen the `ux` row names, the journey's named interaction states, the design-system components and tokens it uses, and the `a11y` row are the slice's second acceptance reference beside the criteria.
4. **Build test-first, one behaviour at a time**, as the engine describes. When the slice's shape rests on an unknown that only running code settles, spike it as a throwaway prototype, keep the answer, and delete the spike before the real slice starts: a spike proves shape and has none of the tests or structure the slice needs.
5. **Handle an edge the brief did not anticipate** the way the engine's scoped-context section says: decide it and write the decision into the spec area that owns it, or record the gap and ask.
6. **Ship the deploy surface for real.** When the slice adds something deployable (always, for the walking skeleton), it produces the pipeline that reaches the first environment of the promotion path — from `09-solution/infra-ops/cicd.md` and `topology.md`, or on a `lite` project from the solution strategy and the conventions. The smoke check after that deploy is the evidence. An environment that cannot run yet makes the task `blocked` with a provisioning ask; it does not make the deploy optional.
7. **Finish.** Run the project's gate and `python3 scripts/check_task.py spec --task T-NNN`. For a `routine` or `feature` task, review your own diff against the brief; for a `critical` task, hand the slice to a fresh-context `conformance-review` and fix what it finds — the reviewer sets the `review` row, and `check_task.py` stays red until it reads `PASS`. Then set `status` to `done` and land the work the way the project's `delivery` setting says (the engine's Delivery table).

On a re-run, re-touch only the code the change affects.

## Rules
- **A test-authoring task has a different shape.** Its deliverable is the test itself: a system or journey acceptance test, an architecture fitness function, or an NFR-evidence test. Write it from its source in the spec, make it executable and able to fail, and leave it guarding. Keep it out of a feature slice, where it would be sized and reviewed as a side effect.
- **Tests pin behaviour.** For changed domain logic, assert observable outcomes precisely enough that a mutated rule fails a test — a boundary asserted on both sides, a rejection asserted by its reason. Coverage without such assertions passes the coverage bar and fails the mutation bar the project's gate enforces.
- **Contracts are verified from both sides.** For each `API-` or `EVT-` seam the slice consumes, write the consumer-side contract; for each it exposes, verify the provider against the published schema.

## Output
Code and tests in the project's source and test trees, laid out as its conventions say; nothing under `spec/` except what follows.

| Target | What changes |
|---|---|
| the source tree | the slice, entrypoint → application → domain → persistence |
| the test tree | the unit, integration, contract and e2e tests the slice needs, tagged `@covers AC-…` and `@state:<name>` |
| `spec/10-delivery/tasks/T-NNN.md` | the `status` row |
| the owning spec area | a decision the slice forced, in the same change as the code |
| `adr/ADR-BUILD-NNN.md` | a costly-to-reverse choice made during implementation |

### Walking-skeleton task only: `12-operate/bootstrap.md`
The first task also writes the setup runbook an operator follows step by step to bring the system up. It is composed from the configuration matrix and the prerequisites register (`infra-ops/environments.md` and `prerequisites.md`, or the conventions on a `lite` project), per platform and per environment, in three phases:

| Phase | Covers | Written by |
|---|---|---|
| A — initial | local and the first environment up: steps per audience (ops-admin · sys-admin · developer), and a worksheet for each environment variable (captured from → stored in → set per environment) | this task |
| B — production | production-only credentials, DNS, scale and residency, the differences between environments, the go-live checklist | `deploy-release`, at the first production promotion |
| C — day 2 | secret rotation, scaling, adding an environment | `deploy-release` |

The runbook also renders the runtime contract (`conventions/runtime-contract.md`) as the startup order: provision → migrate → seed → set flag defaults → deploy → `preflight` → smoke. Each phase opens with `preflight`, so a misconfigured environment is caught before it takes traffic. The runbook says where each value is set and never states the value, because the file is committed and secrets are not.

The report back follows the engine's Reporting section; for a task it also names any decision written into the spec, since that changed a document the reader may rely on.

## Resources
- `references/exec-engine.md`
- Worked example: `examples.md`
