# audit-build — user guide

**Invoke:** `/audit-build`  (plugin: `/grillspec:audit-build`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
The whole-build audit — the independent, release-time attestation that the BUILD was done according to the spec's own process, not just that each task self-reported PASS. It judges the built system against the spec the way the whole-spec audit judges the spec. Owns the three things no per-task review can see: the evidence-ledger itself (did every gate really run, is every recorded VERDICT backed), cross-task emergent properties (suite shape vs the declared distribution, an AC- whose covering test a later task weakened, aggregate coverage/mutation), and the operate-ledger reconciliation. Distrusts the accumulated per-task verdicts on purpose. The judgment phases run as a parallel read-only multi-lens fan-out; report-only with NO fix/loop mode by design — fixes route to the task machinery and a fresh re-audit follows them.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-build`
- **Standalone:** copy the `audit-build/` folder into `~/.claude/skills/`, then run `/audit-build`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
