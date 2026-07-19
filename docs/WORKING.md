# Working efficiently with this system

How to move fast at every stage. The system's *semantics* (flow, gates, the five records) live in
`grill-shared/operator-map.md`; this file is about throughput in Claude Code, Codex, or another Agent
Skills-compatible host.

## How propagation actually works (read this first)

Propagation is **two cooperating layers - a deterministic tool + agent judgment** - not an agent
guessing from memory.

- **The tool finds the set (mechanical, complete).** `impact.py <ID>` walks the spec's reference graph
  (the stable `UC-/AC-/AGG-/API-/...` IDs and their `implements:/depends:/realises:/...` links) and returns
  the *exact, transitive* downstream set - spec files, tasks, code - ordered upstream->downstream. It does
  not miss an edge buried in a prose sentence, and it does not invent one.
- **The agent re-derives each member (judgment).** For every artifact the tool returns, the active agent re-runs the
  owning derive skill *incrementally* - applying the delta, not regenerating from scratch.

**Why not just let the agent find related blocks itself?** It can - but unaided recall over a large spec is
probabilistic and context-window-limited: it will silently miss a transitive dependency some of the time,
and it isn't reproducible. The point of this system is that *nothing silently goes stale*, so **detection
is mechanical (the tool) and only the editing is intelligent (the agent).** The engines already treat this as
reflexive: any skill that changes an ID owns "detect -> impact -> mark -> re-derive -> re-verify"
(`derive-engine.md` and the conductor's *Change propagation* section). You don't have to ask for it.

**So is there something to run?** The loop is: change the upstream authored artifact -> `impact.py` runs
(by the agent, by you, or by the hook below) to surface the downstream set -> the agent re-derives that set. The
repo is wired so this is near-zero effort - see below. You can always run it by hand:
`python3 .grillspec/tools/impact.py AGG-Order` (one ID) or `--since HEAD` (everything changed since last commit).

## What's automatic (in the plugin) vs. what you add

**Ships in the plugin (passive):** the skills, engines, linters, the project-local spec-governance hook,
the project-local exec-gate, and host-native helper agents where supported. **The plugin installs no
_global_ hooks** - it acts only when you invoke a skill, and its enforcers are wired into the spec repo
only, so nothing fires on other projects or in either host's user-level configuration.

**You add to your project:** the active host's permission/approval policy for smooth auto/AFK runs.
Allow only the in-project commands the stack needs, deny destructive or out-of-scope commands, and do
not grant write access outside the project. The plugin cannot ship this trust decision and does not
impose a global command guard.
- **Spec governance (project-local, in the plugin → installed into your repo):**
  - `spec_governance_hook.sh` -> the walking-skeleton installs it as the project's spec **git pre-commit hook**. On commit it runs `lint_spec.py` + `guard_derived.py` over `spec/` and blocks a commit that breaks consistency or hand-edits a derived artifact. Runs **only in that repo, on commit** - nothing global. (Override: `git commit --no-verify`.) The conductor also runs `lint_spec.py` + `impact.py` each run, so consistency/propagation feedback isn't deferred to commit time.
  - `gate_exec.py` -> the walking-skeleton runs `install_exec_gates.py` to vendor one shared copy under `.grillspec/tools/` and merge equivalent **PreToolUse adapters** into this repo's `.claude/settings.json` and `.codex/hooks.json`. It is the **tool-call-time** sibling of the commit hook: it enforces the per-task build *order* a commit-time check can't see - a `src/**` edit is blocked until a failing test was recorded for the active task (red-before-green), and a flip to `status: done` is blocked while `check_task_record.py` is unmet. Project-local, fires **only in that repo**. (Override: `GRILLSPEC_GATE_OFF=1`.) The loop records its RED via `.grillspec/tools/gate_exec.py --start T-NNN` / `--red --test "…" --covers "AC-NNN …"` — `--covers` names the spec ID(s) the failing test drives and each must exist under `spec/` (chat is spec input: an ad-hoc behavior change gets its ID minted in the spec first); transient state stays under `.grillspec/gate/`.
- **Helper agents:** the Claude Code bundle includes native `test-runner` and `explorer` agents; in Codex,
  dispatch the same bounded roles through its subagent facilities.
  - `test-runner` - run the suites in parallel while you implement; failures come back as
    `file:line - reason`, logs stay out of the main context.
  - `explorer` (read-only) - context-heavy lookups without flooding the main session.
  - Pre-authorize the exact test command through the host's project permission policy when unattended
    helper agents cannot answer approval prompts.

## Autonomous coding machine (once the spec is implementation-final)

Goal: hand the finished spec to the system and have it implement, verify, self-correct, and merge with
minimal human involvement - stopping only where a human is genuinely required.

**Run it:** `autorun` (the orchestrator skill). It selects every AFK-eligible, dependency-ready task, runs
each through the closed loop in parallel, merges on green, unlocks dependents, and parks blockers.

**The closed loop per task (exec-engine):** implement -> run the **whole done-gate** (build / lint / type /
unit / integration / contract / e2e / architecture fitness functions / lint_spec / guard_derived /
conformance-review Lens-A / every AC exercised) -> if anything fails, **fix the code** -> repeat until the
gate is fully green. The gate is the *same set CI runs*; CI on the PR is the backstop.

**Why it won't cheat its way to green (the bulletproofing):** the loop must
- fix the **code, never the goalposts** - no deleting/weakening tests, lowering coverage, `skip`/`xfail`,
  loosening a lint/type/fitness rule, or stubbing to fake a pass;
- treat the **spec as upstream truth** - never edit a requirement to match buggy code; a wrong/ambiguous
  spec is *escalated*, not relaxed;
- remember **green != done** - conformance (code-vs-spec/arch, judged independently) and per-AC coverage
  must also hold;
- **never disable a gate, fitness function, or hook.**
If it can't converge after the cap, or the failure set stops shrinking, it **stops and escalates** rather
than thrashing.

**Where a human is still needed (and how it's minimized):** a task is `afk: eligible` only with no
unresolved gap and no **HITL trigger** - a closed list: a **visual/UX decision**, a **product/strategy**
call, a **legal/compliance** sign-off, an **external credential/access**, or an **irreducible preference
fork**. Everything else runs autonomously. To keep round-trips minimal:
- HITL asks are **batched** in `spec/_human-input.md` - clear them in one sitting, then re-launch `autorun`;
- for UX/decision blocks the system **proposes a concrete default** (mockup/states/microcopy) for you to
  **ratify or tweak**, not author from scratch;
- `autorun` keeps executing everything that *isn't* blocked while the queue waits.

**The hard part is the spec, not the code.** Autonomy is bounded by how implementation-final the tasks are:
`derive-tasks` forces every dimension to be an ID reference, a justified `N/A`, or a *resolved* gap before
a task is eligible. The more completely grilling/derivation is done, the larger the AFK-eligible set - so
invest there; the coding machine is only as autonomous as the spec lets it be.

## Per-stage throughput

**Spec / docs (grill + derive)**
- Use the host's plan/read-only mode for grilling and derivation - read-heavy reasoning should show the
  plan and stop before writing.
- Enter through the conductor ("what's next?"), not individual skills. Use the lite path; mark whole areas
  N/A up front.
- Parallelize independent areas (e.g. `ddd` / `quality` / `integration`) via the host's subagent mechanism;
  keep chains (`discovery -> product-vision -> ddd`) sequential.
- Change upstream -> let propagation (tool + re-derive) do the downstream edits. Never hand-hunt.

**Code (implement-task + tests + conformance)**
- Walking-skeleton green first; then each task is a vertical slice on existing rails.
- Fan the task DAG out by dependency: independent tasks -> parallel subagents/workflows; chained tasks -> sequential.
- Honor the task `mode`: AFK tasks -> headless (`claude -p` or `codex exec`); HITL -> interactive.
- Run `test-runner` in parallel while writing the next slice.
- conformance-review at `changed` scope per slice (the fitness-function subset runs in CI regardless).

**Operate / publish**
- `generate-docs` writes the site under `docs-site/`; commit it and the `docs-site.yml` Action deploys to
  GitHub Pages automatically (enable Pages once). For full auto, optionally regenerate docs through the
  chosen host's headless/CI integration and its repository secret, using the same opt-in pattern as the
  Layer-2 conformance job.
- Keep `diagnose`/incident as persistent subagents so you don't re-prime context each time.

**Model routing:** use the strongest reasoning model available for grilling, derivation, and conformance
judgment; use a faster capable model for bounded test/exploration helpers. Host-native agent metadata may
pin those helper roles, but the project workflow does not depend on a vendor model name.

## Cost note
Interactive, headless, subagent, and CI usage may be metered differently by the selected host. Check that
host's current limits before sizing an unattended wave; reserve headless/CI runs for mechanical,
high-volume work when that matches the available budget.
