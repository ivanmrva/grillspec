# Live test — checking that the system runs as designed

The repository is checked statically: the skill files, the tools and their regression suites. What a static check cannot show is whether a live agent follows the skills end to end. This 20-minute protocol shows that, in Claude Code and in Codex, and also confirms that each host resolves the installed package correctly.

## Setup (a throwaway repository)

```bash
mkdir /tmp/grillspec-livetest && cd /tmp/grillspec-livetest && git init -q
# Put a real, messy input document in the repository root: a product brief or
# a few requirement notes. A real document tests more than a clean prompt.
cp ~/path/to/brief.md .
```

Install the plugin in the host under test.

Claude Code (project scope, then reload):

```
/plugin marketplace add ivanmrva/grillspec     # or your fork, or a local path
/plugin install grillspec@ivanmrva --scope project
/reload-plugins
/plugin details grillspec                      # what it loaded, and its context cost
```

Codex:

```bash
codex plugin marketplace add ivanmrva/grillspec
```

Open `/plugins` in the Codex CLI (or Settings > Plugins in the IDE), install Grill Spec from that marketplace, then start a new trusted session in the throwaway repository.

## Packaging checks (do these first)

These break only when the system runs as an installed plugin and not from a source checkout.

1. **The engine loads.** Invoke a worker skill directly: `/grillspec:grill-ddd` in Claude Code, `$grillspec:grill-ddd` in Codex. It should read its shared engine before it starts. If it behaves like a bare skill with no interview method, a shared-engine reference did not resolve; inspect `/plugin details` and `claude --debug` in Claude Code, or the installed package in Codex.
2. **The tools run.** Ask the agent to lint the spec. It should run the installed `lint_spec.py` against the project's `spec/` and report `N error(s), M warning(s)`. "File not found" means the tool path or the working directory is wrong.
3. **The settings are written once.** After the first conductor session, `.grillspec/project.json` exists and holds a `profile` and a `delivery` value.
4. **Hooks are project-local.** The plugin installs no global hooks. Once the walking-skeleton task has run, `git commit` of a broken `spec/` file is blocked by the pre-commit hook, and no other repository is affected.
5. **Both hosts share one edit hook.** After the first build session, `.claude/settings.json` and `.codex/hooks.json` both point at `.grillspec/tools/gate_exec.py`, and neither host folder holds a copy of the tools.

## Behaviour checks

Start the way a user would — invoke the conductor, or describe the feature and let it engage — and watch where the live agent departs from the design. Each row names the file to tighten when it does.

| # | Watch for | Pass | If it fails, look at |
|---|---|---|---|
| 1 | Does it work through the conductor? | the conductor drives; areas come in dependency order | the conductor's session-start section |
| 2 | Does it settle the two settings? | it asks profile and delivery once, recommends the smallest profile with a reason, and writes them | the conductor's first-session section |
| 3 | Does it question the input document? | open questions and contradictions are raised; confident prose is not taken as fact | the grill engine's ingestion section and the area skill |
| 4 | Does it normalise foreign IDs? | a "compliance NFR" becomes an `OBL-`, a `REQ-` constraint becomes a decision | the grill engine's ingestion section |
| 5 | Does it stay lean? | no optional area is offered unasked; at `standard` the solution areas are short decision records with no schema or OpenAPI file | the derive engine and the area skill |
| 6 | Does it wait for readiness? | it recommends finishing inconsistent requirements before deriving the solution, and says what unblocks it | the conductor's readiness section |
| 7 | Does it build test-first? | each behaviour has a failing test before its code, tagged `@covers` | the exec engine and `implement-task` |
| 8 | Does the edit hook hold? | asking it to skip a failing test is denied at the edit; the test stays red or the task is marked blocked | `install_exec_gates.py` wiring; the exec engine |
| 9 | Is done read from the tree? | a task is marked done only after the project's gate is green and `check_task.py --task` passes | the exec engine's Done section |

## Output check

Open the generated `spec/` tree. It should read as the project's own documentation:

- no skill or tool names, and no account of how a file was produced;
- no dates or change notes ("previously", "this round");
- tables with short cells, and prose where reasons matter.

`lint_spec.py` flags the first two mechanically. A leak points at the house rules or at the area skill that wrote the file.

## What a clean run looks like

The conductor routes and settles the two settings. The input document is questioned: real open questions, foreign IDs normalised, no invented contradictions. The spec stays at the size its profile calls for. `lint_spec.py` reports no errors on what was produced. Tasks are built test-first, and each is marked done only when the tree backs it. `spec/` shows no trace of the machinery.

Where the run departs from this, the table above says which file to edit. Then run `python3 plugin/tools/selfcheck.py plugin`, raise the version in both host manifests, rebuild, and reinstall in both hosts.
