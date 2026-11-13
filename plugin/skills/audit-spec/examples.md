# audit-spec — worked example

Illustrative: it shows the shape of a pass and of a finding, not required content.

A subscription-billing product at the `standard` profile, with tasks written and nothing built yet. The user runs `audit-spec` with the defaults (`--depth full --scope all`, report-only).

## Phase 0 — mechanical baseline
```
project_config.py → profile: standard · delivery: trunk
lint_spec.py      → 0 errors, 5 warnings (3 coverage, 1 full-mode file, 1 dated statement)
spec_status.py    → 41 use-cases, 38 with criteria (93%) · 0 unresolved task gaps · 2 tasks blocked
```
No ERROR means the structure is sound, so the rest of the audit is about meaning. The five WARNs are candidates to confirm or dismiss, not findings to copy out.

## Profile — what is not a finding
`09-solution/api/` holds only `index.md` (the seam list and its policies) and no `openapi.yaml`. At `standard` that is correct: the seams and their versioning policy are decided, and the contract package in code will carry the shapes. Nothing to report.

`09-solution/test/levels.md` exists but its tier-contract table has no row for the contract tier, although `index.md` lists six seams. That is a missing decision:

→ `important · test strategy · levels.md · no contract tier is declared for the six seams in api/index.md · fix in the test strategy.`

## Phase 1 — a contradiction the linter cannot see
Both files resolve every ID.
- `06-requirements/data/retention.md`: `DATA-014 Invoice` — retention 7 years.
- `06-requirements/compliance/obligations.md`: `OBL-003`, the same invoice data — purge after 24 months.

→ `blocking · DATA-014 vs OBL-003 · the same data has two retention periods (7 years, 24 months) · fix in the data and compliance requirements, then re-read what impact.py lists for both IDs.`

## Phase 2 — leanness
The linter flagged `09-solution/data/schema.md` as a full-mode file under `standard`. Reading confirms it: 14 tables restated from the migrations folder, already out of step on two columns.

→ `important · to remove · 09-solution/data/schema.md · restates the migrations and has drifted from them · keep the store and tenancy decisions in storage.md, delete the file.`

## Phase 3 — a missing branch
The blind model of billing lists the failed-payment path: trial → active → past-due → grace → suspended → cancelled → reactivated. The domain model gives `Subscription` only active and cancelled.

→ `important · 04-domain/ddd · Subscription has no past-due, grace, suspended or reactivated state, so no use-case, criterion or task exists for failed payments · fix in the domain model; the functional spec and tasks follow.`

The money lens adds: `important · proration on a mid-cycle plan change is unspecified · needs-domain-validation against the billing rules.`

## Verdict (in `spec-audit-report.md` at the project root)
```
CODE-GEN READINESS: NOT-READY  (1 blocking, 4 important)
profile: standard · depth: full · commit: 9f3c1a2
architecture-readiness: NOT MET — the DATA-014 / OBL-003 contradiction sits upstream of the solution
Top fixes, in dependency order:
  1. settle invoice retention (data + compliance) → storage.md, T-031 → lint clean
  2. model the failed-payment lifecycle (domain) → use-cases, criteria, new tasks
  3. specify mid-cycle proration (quality or domain; a spike if the rule is unclear)
  4. delete schema.md; add the contract tier to levels.md
```
At `--depth consistency` the same audit stops after Phase 2 with the contradiction and the two solution-layer findings. Once those are fixed, its best verdict is `CONSISTENT (domain not assessed)`: a consistency pass does not declare readiness, so a clean one is not mistaken for "the right thing is specified".
