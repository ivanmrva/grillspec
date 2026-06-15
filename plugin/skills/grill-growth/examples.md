# grill-growth — worked example

Post-launch growth model for a collaborative whiteboard app, north-star = weekly active editors:
> **Claude:** Your compounding loop is the share link — every board invite pulls in a new editor who creates their own boards. I'd make **invite-driven acquisition** the primary loop, not paid. What's the earliest action that predicts a user sticks?
> **User:** People who invite at least one teammate in week one almost never churn.

Recorded:
- `growth-model.md` — funnel: visit → signup → first board → invite → weekly-active-editor. **Primary loop**: user creates board → shares invite link → invitee joins + edits → invitee creates own board (reinvested input). **Activation bar**: `board.shared` ≥ 1 within 7 days of signup; time-to-value target ≤ 10 min from signup to first shared board. **Retention**: weekly cohorts, plateau check at week-8 ≥ 38% retained editors; stickiness DAU/WAU ≥ 0.45 (high-frequency). Leading indicators: invites/activated-user, board-edit sessions/week.
- `experiments.md` — **EXP-001**: onboarding template gallery raises week-1 share rate. Primary metric: % activated in 7d. MDE +4pp (28%→32%); power 0.8, alpha 0.05; sample = 2,940/arm; min-runtime 14 days (2 weekly cohorts); guardrail: board-load p95 < 1.5s; stop-rule: fixed horizon, no peeking. **EXP-002**: invite-CTA in empty board state lifts invites/user (sequential, O'Brien-Fleming bounds declared).
- `analytics-events.md` — `user.signed_up` {plan, referrer} · `board.created` {template_id} · `board.shared` {invite_channel, invitee_count} · `board.edited` {duration_s} · `invite.accepted` {inviter_id}. Naming = object-action controlled vocab; each event owner = Growth PM. Classification: `referrer` and `invite_channel` = consented-analytics; `inviter_id` = pseudonymous-internal. Cohorts keyed on signup-week.

ADR: `adr/ADR-GRW-001.md` — named the invite link as the primary compounding loop.
