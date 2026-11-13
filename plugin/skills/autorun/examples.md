# autorun — worked example

Illustrative. Two runs over the same build order, to show what the `delivery` setting changes. The spec is build-ready: briefs derived, the linter clean, no unresolved gap on the tasks below.

Ready set: T-014 reschedule-job (`feature`, Scheduling) and T-016 refund-payment (`critical`, Billing) are `afk: eligible` with their dependencies done. T-018 notify-on-reschedule depends on T-014 and turns on a product decision: whether a customer who already confirmed by SMS is notified again when the slot moves.

## Under `pr` delivery

T-014 and T-016 touch different modules, so they run as one wave, each in its own worktree and pull request. T-016 is reviewed by a separate subagent with one criterion held out; T-014 gets no reviewer, because its tier does not ask for one.

Final report:

Two tasks landed and one is waiting on a decision. The default branch is green after the wave.

| Task | State | Detail |
|---|---|---|
| T-014 reschedule-job | landed | gate and `check_task.py` green; pull request merged |
| T-016 refund-payment | landed | review passed on the second round (a context-boundary import was removed); held-out AC-016d passed; pull request merged |
| T-018 notify-on-reschedule | blocked | needs a product decision. Recommended default: notify again only when the appointment day changes. The ask is in `spec/_human-input.md`. |

Remaining: T-020 and T-021 are unlocked by this wave and will run next.

## Under `trunk` delivery

The same tasks run one after another on the default branch. T-014 is built, the gate run locally, pushed, and its deploy's smoke check read before T-016 starts. T-016 is built, reviewed in a fresh context, and pushed once the review passes. The report has the same shape; "landed" cites the smoke check instead of a merged pull request.

Had the smoke check gone red after T-014, the run would have stopped there and reported, leaving T-016 unstarted.
