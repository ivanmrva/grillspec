# Live test - verifying the system runs as designed

Everything in this repo is verified statically (skill logic, the deterministic
linters, the spec backbone). The one thing static checks cannot prove is whether
a live agent actually *follows* the skills end to end - routes through the conductor,
grills instead of rubber-stamping, respects the gates, and keys the autorun loop on
the verdict. Run this 20-minute protocol in Claude Code and Codex to confirm both the
behavior and each host's installed-package resolution.

## Setup (throwaway repo)

```bash
mkdir /tmp/grillspec-livetest && cd /tmp/grillspec-livetest && git init -q
# put a real, messy input doc in the repo root - e.g. a product brief, an
# existing CONTEXT.md, or a few requirement notes. Real docs beat a clean prompt.
cp ~/path/to/CONTEXT.md .
```

Install the plugin in the host under test.

Claude Code (project scope, then reload):

```
/plugin marketplace add ivanmrva/grillspec     # or your fork / local path
/plugin install grillspec@ivanmrva --scope project
/reload-plugins
```

Confirm it loaded and see its real context cost:

```
/plugin details grillspec     # lists skills/agents/hooks + always-on token cost
```

Codex:

```bash
codex plugin marketplace add ivanmrva/grillspec
```

Open `/plugins` in Codex CLI (or Settings > Plugins in the IDE), install Grill Spec from that
marketplace, then start a new trusted session in the throwaway repo.

## Plugin-resolution checks (do these first - they prove the packaging)

These are the things that only break once the system is a *cache-installed*
plugin rather than a source checkout:

1. **Engine loads.** Invoke a worker skill directly: `/grillspec:grill-ddd` in Claude Code or
   `$grillspec:grill-ddd` in Codex.
   It must read its shared engine. If it behaves like a bare profile with no
   engine discipline (no three-bucket intake, no output-hygiene), an installed
   shared-engine reference did not resolve. Inspect `/plugin details` and
   `claude --debug` in Claude Code, or the installed skill/package details in Codex.
2. **Tools run.** Ask the agent to lint the spec. It should execute
   the installed `lint_spec.py` against the project's `spec/` and return
   `N error(s), M warning(s)`. Claude resolves the plugin-root tool; Codex resolves
   the script bundled with its installed skill. A "file not found" means the tool
   path or working directory is wrong.
3. **Spec governance is project-local.** The plugin installs no global hooks. The
   walking-skeleton (`derive-tasks`, `T-001`) installs `spec_governance_hook.sh`
   as the project's spec **git pre-commit hook**: `git commit` a broken `spec/`
   file and the commit is blocked by `lint_spec.py`/`guard_derived.py` (override
   with `--no-verify`). It runs only in that repo, never on other projects.
4. **Both host adapters share one gate.** After entering the execution loop,
   `.claude/settings.json` and `.codex/hooks.json` must both target
   `.grillspec/tools/gate_exec.py`; neither host directory may contain a tools copy.

## The five deviation signals (the actual behavioural test)

Start the system the way a user would - `/grillspec:grill-spec-conductor` in Claude Code,
`$grillspec:grill-spec-conductor` in Codex, or just describe the feature and let it
engage - and watch for where the live agent *diverges* from the design. Each signal
maps to the skill that needs tightening.

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
`python3 plugin/tools/selfcheck.py plugin`, bump both host manifest versions, rebuild,
and reinstall in both hosts.
