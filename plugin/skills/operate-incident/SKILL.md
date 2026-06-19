---
name: operate-incident
description: >-
  Triage a production incident via runbooks, mitigate, and capture every learning as a new assumption or gap that propagates upstream. Use during or just after an incident. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a production incident to work
---

# operate-incident

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **operate an incident on real systems**.

## Process
1. **Intake & triage first.** A signal arrives — a firing alert **or** a human report (support escalation, user complaint, product feedback). Triage it: a **live incident** (user/data/revenue impact *now*) continues here; a **non-urgent bug** routes to the backlog as a task (or the diagnosis loop if hard); a **feature-gap** routes to discovery; an **invalidated bet** routes to bets/risks. Only a true incident proceeds below — the rest propagate upstream like any learning.
2. **Classify severity & stabilize.** **Severity first** (sev1..sevN by user/data/revenue impact → paging, comms cadence, status-page), then **stop the bleeding to restore service** via the runbook (roll back · fail over · flag off; for data loss, the backup/DR procedure). **Mitigation restores service — it is not the root fix.**
3. **Stand up incident-command roles for sev1/sev2** — a **commander** (decides), **scribe** (keeps the timeline), **comms-lead** (status-page/stakeholders), and **SME(s)** (hands-on). One person may double up on lower sevs; the commander is not the one debugging.
4. **Run the timeline + comms log as you go.** Stamp **detected · acknowledged · mitigated · recovered**; keep a **comms log** (channel · timestamp · message) for every external/stakeholder update.
5. **Security-incident branch.** If it is a security/data breach, switch to **containment → eradication → forensics → evidence-preservation** (distinct from an availability incident — preserve evidence before you clean up) and **start the compliance clock now** — the breach-notification `OBL-` (regulator/data-subject timelines, e.g. 72h) triggers here, not after the postmortem.
6. **Find the root cause, then fix it as a task.** Once stable, hand the root-cause hunt to the disciplined diagnosis loop (hypothesise → fix → regression-test) rather than ad-hoc poking; the **durable fix lands as a normal tested task** (a slice), never a hot patch left behind in the incident.
7. **Blameless postmortem — capture the learning:** focus on systems/contributing factors, never individuals. Every root cause becomes a new assumption or `GAP` (a missing rule, NFR, or runbook) and propagates upstream via the standard machinery — a postmortem is a focused change, not a dead document. Record **action items as owned + tracked** (owner · tracking-ref · status), never free text.

## Rules
- The postmortem is **blameless** — systems and contributing factors, not people.
- **Action items are owned + tracked** (owner · tracking-ref · status); a free-text "we should…" is not an action item.
- **Error-budget consumed** (SLO-ref · %) is recorded every incident; **above the agreed threshold, a postmortem is mandatory** (not at the team's discretion).
- The reported **acknowledge** and **recovery** durations (from the timestamps) are raw inputs to a higher-level rollup — this skill does not compute or own a running average.
- **customer-signal intake is first-class (the qualitative loop back):** the step-1 triage routes a user-reported problem upstream (→ discovery / bets / risks), the same propagation as an incident learning — so real-user signal reaches the spec, not just analytics.
- **Never pass on:** an incident with no postmortem · a recurring failure with no new runbook/rule · a learning that doesn't reach the spec.

## Output
Written under `12-operate/`:

| File / target | Captures | Format |
|---|---|---|
| `incident-<id>.md` | incident record + **blameless** postmortem: severity · roles (commander/scribe/comms-lead/SME) · timeline (**detected · acknowledged · mitigated · recovered**) · comms log (channel · timestamp · message) · impact · **error-budget consumed (SLO-ref · %)** · root cause · action items (**owner · tracking-ref · status**) · learnings → new bets/gaps/risks (fed to discovery) · security branch (containment/eradication/forensics/evidence) where applicable | — |

(timeline stamps yield acknowledge + recovery durations as inputs to an upstream rollup; over the error-budget threshold the postmortem is mandatory)

ADRs → `adr/ADR-INC-NNN.md`
(no spec/code changes)
Consumes: the firing alert + its linked `SLO-` and runbook (`09-solution/observability/`) + the DR/backup procedures (`09-solution/infra-ops/`).

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
