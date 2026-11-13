# Operator map — how to drive this system (one page)

## Start here
The user drives everything through `grill-spec-conductor`. It reads the state of the spec and offers the few sensible next moves; nobody has to memorise the skills. The loop: open a session and ask the conductor what is next → it names one area or task → the user answers its questions, or it derives → it carries the change to whatever depends on it. Any skill can also be run directly, for example to see an artifact early.

One principle sizes everything: an area, a file, a rule or a gate earns its place by having a reader — a later step, a tool, or a person who will act on it. What has no reader is not written.

## Project settings
Two settings in `.grillspec/project.json`, asked once by the conductor and read by the tools that scale with them (print them with `python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py`). With no file the tools assume `regulated` and `pr`.

| `profile` | Spec the project carries | For |
|---|---|---|
| `lite` | problem · vision · constraints · domain · functional spec · quality · architecture · conventions · tasks | a solo or pre-launch product |
| `standard` | `lite` plus goals · system context · data · security · compliance · entitlements · integration · ML (AI products) · design system and UX (UI products); each further solution area as a short decision record | personal data, money, paid tiers, or an AI capability whose quality must be gated |
| `regulated` | every area, the solution areas written in full | the documents are themselves a deliverable (an auditor, a regulator, another team) |

Recommend the smallest profile that fits and say what would justify the next one. Raising it later is cheap; carrying spec nobody reads is not. Market, customer discovery, monetization, go-to-market and growth are optional at every profile and run only when the user asks.

| `delivery` | Work lands | Verification | CI |
|---|---|---|---|
| `trunk` | on the default branch | local: the project's one gate before a push | deploys and smokes; other jobs on dispatch |
| `pr` | a branch and pull request per task | the local gate, then the full gate on the pull request | full gate, merge on green, deploy on merge |

`trunk` suits a solo, pre-production project; `pr` a product with users or more than one contributor.

## The flow
Square brackets mark what `standard` adds to `lite`.

`problem-validation` → `product-vision` → `constraints` [`goals` · `system-context`] → `ddd` → `derive-functional` → `quality` [`data-reqs` · `security-reqs` · `compliance` · `entitlements` · `integration-reqs` · `ml-reqs` for an AI product] [`design-system` → `ux-reqs` for a UI product] → *architecture-readiness* → `derive-architecture` [the seven further solution areas] → *implementation-readiness* → `derive-conventions` → `derive-tasks` → *delivery-readiness* → per task: `implement-task` (→ `conformance-review` for a `critical` task), or every ready task unattended (the exec engine's queue rules) → before a release: `audit-build` → `deploy-release` → operate (`migrate-data` when stored data changes).

Available at any point: `audit-spec`.

The three gates in italics are readiness signals, not locks, and count only in-profile areas. They tell the user when downstream work can be trusted; a skill run early still produces an ordinary artifact that later changes will update.

## Ways in
- **From scratch** — from an idea: settle the two settings, then walk the in-profile areas in order.
- **Ongoing work** — the normal mode once a product exists: size the change by tier, amend only what it alters, build it. No scan, no menu.
- **Adoption** — existing code or documents, or a project built with an earlier major version: done once (`migrate_project.py` for the latter), then ongoing work. Documents are grilled like interview answers, not filed.

## Which skills, when
A skill runs when its situation arises. Most are never loaded in a given week, and none costs anything while unused.

| Skill | From scratch | Ongoing work |
|---|---|---|
| `grill-spec-conductor` | drives every step | the intake: sizes the change and routes it |
| `grill-problem-validation` · `grill-product-vision` · `grill-constraints` · `grill-ddd` · `grill-quality` | once, in order (`lite` and up) | amended when a change alters scope, a domain rule, a constraint or a target |
| `grill-goals` · `grill-system-context` · `grill-data-reqs` · `grill-security-reqs` · `grill-compliance` · `grill-entitlements` · `grill-integration-reqs` | once, from `standard` | amended when a change brings a new rule of that kind |
| `grill-ml-reqs` · `grill-design-system` · `grill-ux-reqs` | once, for an AI or a UI product | amended when a change adds a model capability, a component or a screen |
| `grill-customer-discovery` · `grill-market` · `grill-monetization` · `grill-go-to-market` · `grill-growth` | only on request | only on request |
| `derive-functional` | once, after the domain model | amended for each `feature` or `critical` change (its acceptance criteria) |
| `derive-architecture` | once | amended when a change adds a module, a seam or a costly-to-reverse choice |
| the seven further `derive-*` solution skills | one session, decision records, from `standard` | amended when a change alters one of their decisions |
| `derive-conventions` | once | rarely: a new gate, a changed delivery mode |
| `derive-tasks` | the build order and the first briefs | one brief per `feature` or `critical` change |
| `derive-impl-design` · `conformance-review` | for each `critical` task | for each `critical` change |
| `implement-task` | every task; also the whole ready queue, unattended | every change |
| `generate-ui-prototype` | each new screen | each new or reshaped screen |
| `migrate-data` · `deploy-release` | when a slice changes stored data; at each promotion | the same |
| `audit-spec` · `audit-build` | before the build starts; before a release | after adoption or when the spec has drifted; before a release |

## Tasks, tiers and done
A task is one brief, `spec/10-delivery/tasks/T-NNN.md`: a `field | value` table an agent can build from without chasing IDs, because its acceptance criteria carry their text.

| Tier | What it is | What it owes |
|---|---|---|
| `routine` | a fix, tweak, refactor or dependency bump with no new behaviour | no brief: a failing test first, the fix, the gate |
| `feature` | new behaviour inside an existing module | the brief, test-first, the gate |
| `critical` | a new aggregate or context, a migration, an authorization, erasure or billing path, a model seam, any one-way door | the brief, a short design note, the gate, one fresh-context conformance review |

Done is read from the tree, not from a record. `check_task.py` computes each task's status and checks a done-claim: every criterion in the brief has a `@covers` test, every named UI state a `@state:` test, no unresolved gap, and for a `critical` task `review | PASS`, written by the reviewer. A dependency not marked done is shown as a note. The only stored progress is the brief's `status` row.

## Where a fact belongs
| The fact | Where it goes |
|---|---|
| a settled choice | the artifact that owns it, plus an ADR in `adr/` when it is costly to reverse |
| not settled yet | the same artifact, as an open point or deferred with the trigger that reopens it |
| a bet or a risk | inline in the artifact, with its status |
| a domain term · an actor | the area's `glossary.md` · `actors.md` |
| something only a human can supply | `spec/_human-input.md`; a credential in `spec/_provisioning.md`; the task marked `blocked` |
| what changed, and when | git history |

When unsure, record it as an open point in the artifact it concerns; the conductor re-routes it on its next pass.

## Changing something already specified or built
Every file under `spec/` is an authored document that states what is true now. The skill that owns an area edits it in place: the smallest change in meaning, re-authored so the file reads as written in one pass. A problem found while coding is fixed in the area that owns the fact, in the same session as the code.

The reference graph carries the change: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/impact.py <IDs>` (or `--since <ref>`) lists every spec file, task and test that depends on the changed IDs, upstream first. Re-work that set and nothing else. A changed behaviour that is already built becomes a task, so the code follows the spec.

## Parallel sessions
One area per session. Each area owns its output folder and each ADR is its own file, so sessions on different areas do not collide; re-read an artifact before writing it. In `pr` delivery use a branch per session, and tasks may run in parallel, one branch or worktree each. In `trunk` delivery build tasks run one after another. After a merge the conductor recomputes the state from the repository.

## Who checks what
| Check | What it covers | When |
|---|---|---|
| the project's gate | format, lint, types, tests, coverage and mutation bars, architecture fitness functions | before a push; in `pr` also on the pull request |
| the edit hook (`gate_exec.py`) | an edit that adds a skipped test or a fake in production code | as the edit is made |
| the pre-commit hook | spec lint · contract IDs · done-claims · tests with no spec driver | each commit |
| `conformance-review` | one task's code against its brief, by a reviewer that did not write it | each `critical` task |
| `audit-spec` | the spec itself: consistency, fit to the profile, leanness, buildability | before a build, or on demand |
| `audit-build` | the whole build from the tree; in `trunk` it also runs the dispatch-only CI jobs once | before a release |
| the smoke check | that the deploy shipped | after each deploy |
| the agent host's own code review | general correctness and security | when wanted; not part of the pipeline |

Code and spec are governed separately even in one repository. The project's conventions and `AGENTS.md` (with `CLAUDE.md` containing exactly `@AGENTS.md`) govern how code is written; the linter and the pre-commit hook govern `spec/`. Project gates start as a small core — boundaries, no fakes, no skipped tests, config drift — and grow when an incident shows a rule was needed.
