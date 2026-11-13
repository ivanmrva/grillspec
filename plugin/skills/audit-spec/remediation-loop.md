# audit-spec `--loop` — repeat until a pass finds nothing

Loaded only in `--loop` mode. The loop repeats full-depth audit passes and fixes everything each pass finds, until fresh, independent auditors report nothing new twice in a row. The phases in `SKILL.md` define what a pass judges. This file is the harness around them: who audits, how findings are merged, how fixes are applied, and how each fix is carried through everything that depends on it.

A loop spends several parallel agents per round. It pays for itself on a `standard` or `regulated` spec before a build. For a `lite` spec one `--fix` pass is usually enough; when asked to loop a small spec, say so, and if the loop is still wanted run each round with one auditor per track.

## One round
The steps depend on each other, so keep the order.

1. **Baseline.** Run the Phase 0 tools and record the counts. The baseline stays green for the whole loop; it is the floor, not the goal.

2. **Audit, on two tracks, in parallel.** The two kinds of audit work behave differently, so they run separately. Give every auditor the list of findings already seen and the list of settled non-defects (below). Spawn every auditor read-only (the `Explore` agent type, with no Edit or Write): it returns a table of findings and edits nothing. An auditor that edits changes the tree other auditors are reading and the files you are about to ground findings against.

   - **Track A — domain and usage completeness. Whole spec, every round.** Phase 3 is a blind re-derivation, and each independent run notices different gaps, so a later run finds what an earlier one missed even after a clean round. Buy coverage with independent samples rather than more rounds: three auditors, each reading the whole spec through a different lens so they do not converge on the same findings.

     | Lens | Looks for |
     |---|---|
     | entity lifecycle | every entity's states, above all the abnormal endings (cancel, refund, dispute, expire, suspend, merge, erase, archive, fraud hold) |
     | rule collisions and edge generators | two rules meeting; money, time, identity, quantity, concurrency and dependents applied to the model |
     | persona journeys | each real journey through its unglamorous steps (empty state, abandon and return, permission changed mid-action, at scale, hitting a limit, blocked by another actor) |

   - **Track B — consistency and fit. Scoped after round 1.** The Phase 0–2 work: contradictions, scope, decisions, typed facts that disagree, reference direction, profile fit, leanness, drift. In round 1 it covers the whole spec, split across about three non-overlapping bundles (the domain and cross-area consistency · the requirements and the solution layer · the functional spec, UX, design system, discovery and any optional areas present). From round 2 it covers only the files the previous round changed and everything that references them, which `impact.py` computes. Files no fix went near were checked in round 1 and have not moved.

   Each auditor returns a grounded table (severity · `file:line` or ID · what is wrong · the recommended fix) or the words `ZERO FINDINGS`.

3. **Merge, ground, then fix.** Union the tables and drop anything already in the seen list (key: location plus rule), so a finding that was fixed, or judged and rejected, does not return. What remains is this round's work. Read the artifact for each finding and confirm it at its `file:line` or ID before editing; drop what you cannot confirm. Then fix every confirmed finding, nits and suggestions included.

4. **Carry each fix through now, not next round.** Fix each defect in the area that owns the fact, as `SKILL.md` describes. Then run `impact.py` over the IDs you changed and work through everything it lists, to the end of the order: the task briefs, the conventions and the design notes of touched modules. Re-read the root `AGENTS.md` whenever the conventions change; it sits outside `spec/`, so the tool does not list it. Leaving that tail for the next round's auditors to rediscover costs a whole round, and Track B's narrow scope assumes it has been done.

5. **Verify.** Run the mechanical baseline again and return it to green.

6. **Log and clean up.** Append the round's fixes to `audit-fixes-log.md` at the project root, increase the round count, and delete `spec-audit-report.md`.

7. **Count.** Add the round's new findings to the seen list. If every Track A auditor and Track B reported nothing new, increase the dry-round counter; otherwise reset it to zero.

8. **Stop when all three hold:** two consecutive dry rounds; a green mechanical baseline; and a final independent whole-spec sweep of the classes that recur (a stated ID range against the highest ID in use, enumerations in a contract or schema against the aggregate's states, reference direction) that comes back clean. One dry round is not enough, because a sampling auditor can miss on one run and hit on the next.

## What one fix usually touches
`impact.py` is the authority; this is what to expect from it. A changed command, state or rule in the domain model typically reaches the use-cases and criteria, the data and API decisions, the screens and journeys, the actor list and the authorization rule, and then the task briefs (which quote criteria text), the conventions when the change moves an architectural or testing fact (with `AGENTS.md` after them), and the design notes of touched modules. At `lite`, where most solution areas are not written, the tail is shorter. A feature's tail often takes a round or two to settle; that is normal convergence.

## What keeps the loop converging
- Auditors read; only the orchestrating session edits, and only after confirming each finding itself.
- One loop per repository at a time. Two loops, or a loop beside another session that edits the spec, overwrite each other. Confirm nothing else is editing the spec before you start.
- Check rejections as well as findings. When an auditor dismisses a candidate, spot-check the classes where a real defect hides behind a plausible excuse; a stale ID-range claim is the usual one.
- A fix in an upstream file may not cite a downstream ID (for example a use-case or acceptance-criterion ID inside the domain model). The linter flags every such mention as a downward reference, so use domain language there.
- When an edit pushes a passage past the linter's dense-prose threshold, give the item its own short section or a table row. Do not leave the WARN.
- Keep the list of settled non-defects across rounds (documented deferrals, deliberate numbering schemes, intentional gaps) and hand it to every auditor.
- A marker such as `deferred`, `accepted-risk`, `needs-counsel` or `needs-domain-validation` records a decision. It is not a defect to fix.
- A new ID brings obligations with it. A new command needs an authorization rule (or an explicit system mark) and a reachable, terminating state machine; a published event needs a seam entry or a recorded exclusion; a new threat needs a linked control.
- A fix removes as readily as it adds. A leanness finding is closed by deleting the duplicate or the excess file, and the round's log says what was removed.

## Decisions only the user can make
When a finding turns on a fact only the user, the organisation or counsel holds (a phasing or go-to-market call, a legal, tax or finance specific, a visual choice): apply a defensible default so the spec stays consistent, record it in `human-decisions-needed.md` (the finding · the default applied · what to confirm or change), and continue with everything else. Decide whatever engineering or domain merit settles, per the engine's decision classes; park only what is a real user-owned fact or one-way door.

## Tools
All under `python3 ${CLAUDE_PLUGIN_ROOT}/tools/`: the baseline (`lint_spec.py`, `spec_status.py`, `check_contracts.py`, `project_config.py`) and the propagation set (`impact.py`). In a project that vendors the tools, use the project's own copy.

## Limits
- Commit only when the user asks, and then the way the project's delivery mode says work lands.
- Edit `spec/`, the root `AGENTS.md` when a fix changes what it states, and the three report files. Code is out of scope for this mode.
- The three root files (`spec-audit-report.md`, `audit-fixes-log.md`, `human-decisions-needed.md`) are transient and git-ignored.
- If interrupted, resume from the working tree and the fixes log, not from git history.
