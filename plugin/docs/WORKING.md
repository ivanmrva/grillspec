# Working efficiently with this system

How to move fast at each stage, in Claude Code, Codex or another host that runs Agent Skills. What the system is and how its parts fit is in [HOW-IT-WORKS.md](HOW-IT-WORKS.md); this page is about throughput.

## Start small

Choose the smallest profile that fits (`lite` for a solo or pre-launch product) and `trunk` delivery until the product has users or a second contributor. Both can be raised later: ask the conductor, or run the plugin's settings tool from the project root.

```
python3 <plugin>/tools/project_config.py --set profile=standard --set delivery=pr
```

`<plugin>` is the installed plugin folder.

Spec that nobody reads still has to be kept consistent, so the cheapest spec is the one that holds only what a later step, a tool or a person will act on. Ask for the optional areas (market, customer discovery, monetization, go-to-market, growth) only when you want them.

## How a change travels

A change touches the areas it actually changes and nothing else. Two parts cooperate:

- **The tool finds the set.** `impact.py <ID>` walks the spec's reference graph and prints every spec file, task and test that depends on that ID, upstream first. It is complete and repeatable, which unaided recall over a large spec is not.
- **The agent re-works each member.** For every file in the set, the skill that owns the area applies the change in place: the smallest change in meaning, with the passage rewritten so the file still reads as one document.

You rarely need to run it yourself. The conductor does so whenever an ID changes. By hand, from the project root:

```
python3 <plugin>/tools/impact.py AC-101a        # one ID
python3 <plugin>/tools/impact.py --since HEAD   # everything changed since the last commit
```

When a change reaches a task that is already built, it becomes work: the brief is updated, the listed tests are re-run, and the code under them follows.

## What is installed, and where

The plugin itself is passive. It adds skills, method files and tools, and acts only when you invoke a skill. It installs no global hooks.

Into your project, and only there, the build installs two hooks:

| Hook | Runs | Blocks |
|---|---|---|
| git pre-commit (`spec_governance_hook.sh`) | on `git commit` | a spec lint error · a contract that references an undefined ID · a task marked done that the tree does not back · a test with no spec driver |
| edit hook (`gate_exec.py`, wired into `.claude/settings.json` and `.codex/hooks.json`) | before each file edit | an edit that adds a skipped test, or a fake in production code |

Both run from one copy of the tools under `.grillspec/tools/`. `install_exec_gates.py` puts the edit hook there with the done-claim and orphan-test checkers; the walking-skeleton task adds the spec tools and installs the pre-commit hook. Commit that folder and both hook configurations so every checkout and worktree has them. Emergency overrides: `git commit --no-verify` and `GRILLSPEC_GATE_OFF=1`.

What you add yourself is the host's permission policy for unattended runs: allow the in-project commands your stack needs, deny destructive ones, and grant no write access outside the project. The plugin cannot make that trust decision for you.

Two helper roles keep the main session's context clean. The Claude Code bundle ships them as agents; in Codex, dispatch the same roles through its subagent facilities.

| Helper | Use |
|---|---|
| `test-runner` | runs the suites while you implement and returns failures as `file:line — reason`, keeping logs out of the main context |
| `explorer` (read-only) | context-heavy lookups |

## Building unattended

Ask for the ready tasks to be built unattended and the agent takes every task that is eligible and whose dependencies are done, and runs each through the same loop a single task follows. There is no separate mode for this: the exec engine's queue rules say what counts as ready and how tasks are ordered.

**The loop per task.** One behaviour at a time: a failing test, the smallest real code that passes, refactor on green. Then the project's whole gate (format, lint, types, build, the test tiers the slice touches, the coverage and mutation bars, the architecture checks) and `check_task.py --task T-NNN`. Anything that fails is fixed in the code and the gate is run again. A `critical` task also gets a design note before coding and one review in a fresh context.

**Where the work lands** follows the delivery mode. In `trunk`, tasks run one after another on the default branch and CI deploys each push. In `pr`, tasks can run in parallel, one branch each, and merge when the pull-request gate is green.

**What keeps a green run honest.** The loop fixes the code, not the measure. It does not weaken or delete a test, lower a threshold, add a skip, put a fake in production code, cross a module boundary to get a test passing, or disable a hook or a check. When the spec is wrong or unclear it is corrected in the area that owns it, or escalated; it is not bent to match the code. The edit hook and the checkers catch the mechanical forms of these shortcuts. If the set of failures has not shrunk for two rounds, the loop stops and escalates.

**Where you are still needed.** A task is eligible for unattended work only when it has no unresolved gap and needs none of: a visual or UX decision, a product or strategy call, a legal sign-off, an external credential, or a choice that is purely your preference. To keep those round trips few:

- the asks are batched in `spec/_human-input.md`, so you clear them in one sitting and start the run again;
- for a visual or product decision the system proposes a concrete default for you to confirm or adjust;
- the run keeps working on everything that is not blocked.

The limit on autonomy is the spec, not the coding. A brief whose criteria carry their text, whose rules are listed and whose gaps are closed can be built without a person; a vague one cannot.

## By stage

**Spec work (interviews and derivations)**
- Enter through the conductor and ask what is next.
- Use the host's plan or read-only mode for interviews: the work is reading and reasoning, and you see the plan before anything is written.
- Run independent areas in parallel sessions or subagents (for example quality and integration); keep chains (discovery → vision → domain) in order.
- Change the upstream fact and let the impact set drive the downstream edits. Do not hunt for them by hand.

**Code**
- Get the walking skeleton green first; every later task is a vertical slice on rails that exist.
- While iterating, run the tests the change touches. Before a push, run the project's one gate.
- In `trunk` delivery, push a batch that is green locally, since each push costs a deploy. Do not push to make CI check something a local run can show.
- Tasks marked `afk: eligible` can run headless (`claude -p`, `codex exec`); a blocked task needs you.

**Release and operate**
- Run `audit-build` before a release. In `trunk` delivery this is also when the CI jobs that do not run on every push (security scan, accessibility, visual baseline, mutation) are run once.
- `generate-docs` builds the documentation site from the spec; rebuild it when the spec changes.
- After a deploy, the smoke check against the deployed environment is the signal that it shipped.

## Models and cost

Use the strongest reasoning model you have for interviews, derivations and reviews, and a faster one for the bounded helper roles. The workflow does not depend on a particular model name.

Interactive, headless, subagent and CI usage may be metered differently by your host. Check its current limits before starting a long unattended run.
