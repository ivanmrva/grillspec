---
name: operate-incident
description: >-
  Work a production incident — triage, restore service by the runbook, keep the timeline, find the root cause, and turn what was learned into a fix and a spec change. Use during or just after an incident. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: a production incident to work
---

# operate-incident

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill works an incident on a real system: restore service first, understand it second, and make sure the system and its spec are different afterwards.

## Process
1. **Triage the signal.** It may be a firing alert or a human report (a support escalation, a complaint). Only a live incident — users, data or revenue affected now — continues here. The rest is routed like any other learning:

   | It is | Goes to |
   |---|---|
   | a bug that can wait | an ordinary fix, or `diagnose` if the cause is not obvious |
   | a missing capability | the product or discovery area |
   | evidence against a product bet | the area that owns the bet |
2. **Set the severity, then stabilize.** Severity follows impact on users, data and revenue, and decides paging, how often stakeholders hear from you, and whether the status page changes. Then stop the damage by the runbook: roll back, fail over, turn a flag off; for data loss, the backup and recovery procedure. Mitigation restores service. It is not the fix, and the hunt for the cause waits until the system is stable.
3. **Name who does what, for a severe incident.** Someone decides (the commander), someone keeps the timeline, someone talks to stakeholders, and someone has hands on the system. On a small team one person holds several roles; what matters is that the person deciding is not also the one debugging.
4. **Keep the timeline and the communications log as you go.** Record the four times — detected, acknowledged, mitigated, recovered — and each external or stakeholder update with its channel, time and message. Reconstructing them afterwards is unreliable.
5. **For a security incident or data breach, switch procedure.** Contain, then eradicate, and preserve evidence before cleaning anything up, since forensic evidence is destroyed by the same steps that restore service. Start the compliance clock at detection: a breach-notification obligation (an `OBL-` with a deadline to the regulator or the people affected) runs from then, not from the postmortem.
6. **Find the root cause, then fix it properly.** Once stable, hand the hunt to `diagnose`. The durable fix lands as normal tested work under the engine's rules — a failing test first — because a hot patch left behind from the incident is untested production code.
7. **Write the blameless postmortem.** It describes systems and contributing factors and names no one as the cause. Each root cause becomes a change: a new or corrected rule, quality target or runbook in the spec area that owns it, or a recorded gap where the answer is the user's to give. Action items carry an owner, a tracking reference and a status, so they can be followed up.

## What closes an incident
- The record below is complete, with all four times and every action item owned.
- The learning has reached the spec or the runbooks. A recurring failure with no new rule or runbook will recur again.
- Where the project has objectives, the share of the error budget the incident consumed is recorded against its `SLO-`. Above the threshold the team agreed, a postmortem is required; below it, write one when there is something to learn.

The acknowledge and recovery durations come straight from the recorded times. A project that tracks delivery metrics rolls them up elsewhere; this skill only records them.

## Output
One dated record per incident, under `12-operate/`. Its readers are the people who ask later what happened, what was decided and what is still open, so write for them and leave out what they would not use.

| File | Captures | Format |
|---|---|---|
| `incident-<id>.md` | severity · who held which role · timeline (detected · acknowledged · mitigated · recovered) · communications log · impact · error budget consumed (`SLO-` and share), where the project has objectives · root cause · action items (owner · tracking reference · status) · what changed in the spec or runbooks · for a security incident, containment, eradication and the evidence preserved | a `field \| value` table, then a short blameless narrative |
| `adr/ADR-INC-NNN.md` | a costly-to-reverse decision the incident forced | ADR |

Reads: the alert or report, the objective and runbook linked to it (`09-solution/observability/`, where the project has them), and the backup and recovery procedures.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
