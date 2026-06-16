# Working efficiently with this system

How to move fast at every stage. The system's *semantics* (flow, gates, the five records) live in
`${CLAUDE_PLUGIN_ROOT}/grill-shared/operator-map.md`; this file is about *throughput in Claude Code*.

## How propagation actually works (read this first)

Propagation is **two cooperating layers - a deterministic tool + Claude's judgment** - not Claude
guessing from memory.

- **The tool finds the set (mechanical, complete).** `impact.py <ID>` walks the spec's reference graph
  (the stable `UC-/AC-/AGG-/API-/...` IDs and their `implements:/depends:/realises:/...` links) and returns
  the *exact, transitive* downstream set - spec files, tasks, code - ordered upstream->downstream. It does
  not miss an edge buried in a prose sentence, and it does not invent one.
- **Claude re-derives each member (judgment).** For every artifact the tool returns, Claude re-runs the
  owning derive skill *incrementally* - applying the delta, not regenerating from scratch.

**Why not just let Claude find related blocks itself?** It can - but unaided recall over a large spec is
probabilistic and context-window-limited: it will silently miss a transitive dependency some of the time,
and it isn't reproducible. The point of this system is that *nothing silently goes stale*, so **detection
is mechanical (the tool) and only the editing is intelligent (Claude).** The engines already treat this as
reflexive: any skill that changes an ID owns "detect -> impact -> mark -> re-derive -> re-verify"
(`derive-engine.md` and the conductor's *Change propagation* section). You don't have to ask for it.

**So is there something to run?** The loop is: change the upstream authored artifact -> `impact.py` runs
(by Claude, by you, or by the hook below) to surface the downstream set -> Claude re-derives that set. The
repo is wired so this is near-zero effort - see below. You can always run it by hand:
`python3 tools/impact.py AGG-Order` (one ID) or `--since HEAD` (everything changed since last commit).

## What's automatic (in the plugin) vs. what you add

**Ships in the plugin (passive):** the skills, engines, linters, the project-local spec-governance hook, and the subagents below. **The plugin installs no global hooks** - it acts only when you invoke a skill, so it never fires on your other projects or your `~/.claude` config.

**You add to your project** (a plugin cannot ship a permission allowlist): a `.claude/settings.json` for smooth auto/AFK runs - a broad in-project `allow`, a `deny` for destructive/out-of-scope commands, and **no `additionalDirectories`** so writes cannot leave the project. Prune the allow-list to your stack and add your test command (see `test-runner`). **Scope and destructive-command guarding is this permission layer's job** (Claude Code already prompts) - the plugin does not impose a global command guard.
- **Spec governance (project-local, in the plugin → installed into your repo):**
  - `spec_governance_hook.sh` -> the walking-skeleton installs it as the project's spec **git pre-commit hook**. On commit it runs `lint_spec.py` + `guard_derived.py` over `spec/` and blocks a commit that breaks consistency or hand-edits a derived artifact. Runs **only in that repo, on commit** - nothing global. (Override: `git commit --no-verify`.) The conductor also runs `lint_spec.py` + `impact.py` each run, so consistency/propagation feedback isn't deferred to commit time.
- **Subagents** (in the plugin):
  - `test-runner` (Sonnet) - run the suites in parallel while you implement; failures come back as
    `file:line - reason`, logs stay out of the main context.
  - `explorer` (Sonnet, read-only) - context-heavy lookups without flooding the main session.
  - To let `test-runner` run tests without a prompt, add your test command to `permissions.allow` in
    `settings.json`, e.g. `"Bash(npm test*)"` / `"Bash(pytest*)"` / `"Bash(cargo test*)"`. (Subagents
    cannot answer permission prompts - an unlisted/`ask` match is treated as denied.)

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
- Plan mode (Shift+Tab twice) for grilling and derivation - read-heavy reasoning; it shows the plan and
  stops before writing.
- Enter through the conductor ("what's next?"), not individual skills. Use the lite path; mark whole areas
  N/A up front.
- Parallelize independent areas (e.g. `ddd` / `quality` / `integration`) via the `Task` tool / subagents;
  keep chains (`discovery -> product-vision -> ddd`) sequential.
- Change upstream -> let propagation (tool + re-derive) do the downstream edits. Never hand-hunt.

**Code (implement-task + tests + conformance)**
- Walking-skeleton green first; then each task is a vertical slice on existing rails.
- Fan the task DAG out by dependency: independent tasks -> parallel subagents (or dynamic workflows on
  Opus 4.8 / Enterprise); chained tasks -> sequential.
- Honor the task `mode`: AFK tasks -> headless (`claude -p`); HITL -> interactive.
- Run `test-runner` in parallel while writing the next slice.
- conformance-review at `changed` scope per slice (the fitness-function subset runs in CI regardless).

**Operate / publish**
- `generate-docs` writes the site under `docs-site/`; commit it and the `docs-site.yml` Action deploys to
  GitHub Pages automatically (enable Pages once). For full auto, optionally regenerate docs in CI with a
  Claude GitHub Action (needs `ANTHROPIC_API_KEY`), same opt-in pattern as the Layer-2 conformance job.
- Keep `diagnose`/incident as persistent subagents so you don't re-prime context each time.

**Model routing:** Opus 4.8 in the main session (grilling, derivation, conformance judgment); Sonnet for
the subagents (set in their frontmatter). Opus thinks, Sonnet executes.

## Cost note
Agent-SDK and GitHub-Actions usage is metered separately from interactive Claude Code (separate weekly
pool on subscription plans, from 2026-06-15). Push judgment-heavy work to interactive sessions; reserve
headless/CI runs for mechanical, high-volume work.
