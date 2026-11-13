# derive-tasks — worked example

Illustrative. One brief for a `critical` UI slice, then a credential-gated one.

```markdown
# T-014 — Pay an order

| field | value |
|---|---|
| tier | critical — money path |
| phase | MVP · afk: eligible |
| status | todo |
| outcome | a buyer pays an open order and sees a receipt |
| behavior | UC-014 pay an order<br>AC-014a — Given an open order, when the buyer pays its exact total, then the payment is accepted and a receipt is shown<br>AC-014b — Given an open order, when the amount is zero or exceeds the total, then the payment is rejected with a clear error and nothing is charged |
| touches | MOD-billing (api · app · domain · infra) · API-Pay · EVT-OrderPaid · the payments table · SCR-05 checkout |
| rules | SEC-03 — only the Owner or Billing role may pay; a Viewer's attempt is denied<br>ENTL-04 — paying is a paid-tier capability; a lapsed subscription is refused<br>DATA-03 — payment records are kept seven years<br>NFR-002 — p95 under 300 ms |
| non-goals | refunds · partial payments · saved cards |
| tests | unit for the amount rules · integration for the payment record and the provider adapter including its timeout path · contract on API-Pay · one e2e for the happy path |
| ux | JRN-07 on SCR-05 — states: confirm · processing · receipt · error · permission-denied → prototypes/ui/pay.html |
| a11y | keyboard: tab to confirm, focus trapped in the dialog · SC 2.4.7 · SC 3.3.1 |
| prototype-review | frozen — prototypes/ui/pay.html |
| design | design-first — 10-delivery/impl-design/T-014-pay.md |
| review | pending |
| depends | T-002 |
```

The brief can be built without opening another file: each criterion says what must happen, each rule says what it requires, and the non-goals mark the edge. The IDs let `check_task.py` hold the task to a `@covers AC-014a` and `@covers AC-014b` test and a `@state:` test for each of the five states, and let a later change to `SEC-03` find this task.

## A credential-gated slice

```
| phase | MVP · afk: blocked — external credential (STRIPE_SECRET_KEY pending) |
| human-prereq | Stripe API key → `STRIPE_SECRET_KEY`, set in the CI and platform secret stores |
```

The credential's live state is the spec-root `_provisioning.md` register:

| key | owner | consumed-by | state | evidence |
|---|---|---|---|---|
| `STRIPE_SECRET_KEY` | human | T-014, T-021 | pending | — |
| `RESEND_KEY` | human | T-046 | provisioned | CI secret and the staging environment |

`T-046` may be `afk: eligible` because its key is provisioned; `T-014` waits, and an unattended run sets it aside before starting rather than discovering the missing key halfway through.
