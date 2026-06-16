# Live test - verifying the system runs as designed

Everything in this repo is verified statically (skill logic, the deterministic
linters, the spec backbone). The one thing static checks cannot prove is whether
a live Claude Code agent actually *follows* the skills end to end - routes through
the conductor, grills instead of rubber-stamping, respects the gates, and keys the
autorun loop on the verdict. This is a 20-minute protocol to confirm that, and to
confirm the plugin packaging resolves correctly once installed.

## Setup (throwaway repo)

```bash
mkdir /tmp/grillspec-livetest && cd /tmp/grillspec-livetest && git init -q
# put a real, messy input doc in the repo root - e.g. a product brief, an
# existing CONTEXT.md, or a few requirement notes. Real docs beat a clean prompt.
cp ~/path/to/CONTEXT.md .
```

Install the plugin into this project (project scope so it is repo-local), then
reload:

```
/plugin marketplace add ivanmrva/grillspec     # or your fork / local path
/plugin install grillspec@ivanmrva --scope project
/reload-plugins
```

Confirm it loaded and see its real context cost:

```
/plugin details grillspec     # lists skills/agents/hooks + always-on token cost
```

## Plugin-resolution checks (do these first - they prove the packaging)

These are the things that only break once the system is a *cache-installed*
plugin rather than files in `.claude/`:

1. **Engine loads.** Invoke a worker skill directly, e.g. `/grillspec:grill-ddd`.
   It must read its shared engine. If it behaves like a bare profile with no
   engine discipline (no three-bucket intake, no output-hygiene), the
   `${CLAUDE_PLUGIN_ROOT}/grill-shared/...` reference did not resolve - check
   `/plugin details` and `claude --debug`.
2. **Tools run.** Ask the agent to lint the spec. It should execute
   `python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py` against the project's
   `spec/` and return `N error(s), M warning(s)`. A "file not found" means the
   tool path or the working directory is wrong.
3. **Spec governance is project-local.** The plugin installs no global hooks. The
   walking-skeleton (`derive-tasks`, `T-001`) installs `spec_governance_hook.sh`
   as the project's spec **git pre-commit hook**: `git commit` a broken `spec/`
   file and the commit is blocked by `lint_spec.py`/`guard_derived.py` (override
   with `--no-verify`). It runs only in that repo, never on other projects.

## The five deviation signals (the actual behavioural test)

Start the system the way a user would - `/grillspec:grill-spec-conductor`, or
just describe the feature and let it engage - and watch for where the live agent
*diverges* from the design. Each signal maps to the skill that needs tightening.

| # | Watch for | Pass | Fail -> fix |
|---|-----------|------|-------------|
| 1 | **Routing.** Does it orchestrate through the conductor and the staged pipeline, or free-style an answer? | Conductor drives; areas are visited in dependency order | Tighten the conductor's routing/entry instructions |
| 2 | **Grilling, not filing.** Given the input doc, does it sort into settled / needs-clarification / contradiction and *push back*, or accept confident prose as fact? | Open questions and contradictions are surfaced | Strengthen the engine's Ingestion section + the area profile |
| 3 | **ID normalization.** Does a foreign id (a "compliance NFR", a `REQ-` constraint) get re-prefixed to its owning area / a decision, or pass through? | `NFR-CMP-*` -> `OBL-*`, `REQ-*` -> `ADR-*` | Reinforce the ID-normalization rule in the engine |
| 4 | **Gating.** Does derivation wait for the architecture-readiness gate, or derive against an inconsistent spec? | It refuses to derive until requirements are consistent | Tighten the gate check in derive-engine + the conductor |
| 5 | **Autorun verdict.** In AFK/autorun, does the loop key on the `VERDICT:` line from run-tests, or declare done on its own? | Loop advances only on `VERDICT: PASS` | Fix the verdict contract in run-tests / autorun |

## Output-hygiene spot check

Open the generated `spec/` tree. It must read as project documentation: no skill
names (`grill-*`, the conductor), no tool names, no "derived by ..." narration.
A leak means the global output-discipline rule in the engines is being ignored -
reinforce it in the offending area profile.

## What a clean run looks like

Conductor routes; the input doc is grilled (real open questions raised, foreign
ids normalized, no fabricated contradictions); derivation waits for the gate;
`lint_spec.py` returns 0 errors on the produced slice; the autorun loop advances
only on `VERDICT: PASS`; and `spec/` contains no trace of the machinery. Where it
deviates, the table above says which skill to edit - then re-run
`python3 tools/selfcheck.py`, bump `version` in `plugin.json`, and reinstall.
