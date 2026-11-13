# derive-conventions — worked example

Illustrative. From the architecture (TypeScript · ports-and-adapters · Scheduling and FieldWork contexts), a `standard` profile, `trunk` delivery.

`delivery/conventions/boundary-rules.md` — boundaries as checks:

```
RULE bnd-01  Scheduling reaches FieldWork only through its contracts
  deny   src/scheduling/**  ->  src/fieldwork/!(contracts)/**
  allow  src/scheduling/**  ->  src/fieldwork/contracts/**
  check  dependency-cruiser `no-cross-context-internals`, part of `npm run verify`
RULE bnd-02  the domain depends on nothing outward
  deny   src/*/domain/**  ->  src/*/{infra,adapter,api}/**
RULE dep-01  dependencies are pinned
  check  `npm ci --frozen-lockfile` in `verify`
```

`delivery/conventions/workflow.md` — the delivery mode, the gate, the definition of done:

> **Delivery: `trunk`.** Work lands on `main`; related slices may share one push. Run the tests a change touches while iterating and `npm run verify` before a push. CI deploys `main` to staging and runs the smoke check; the security scan, the accessibility check and the mutation run are dispatch-only until the first production release.
>
> **Done:** every acceptance criterion in the brief has a `@covers` test; `npm run verify` is green; `check_task.py --task` is green; for a `critical` task the fresh-context review passed. Commits follow Conventional Commits.

```bash
npm run verify        # format · lint · types · unit · boundaries · no-fakes · no-skips · orphan-tests · config-drift
npm run test:int      # integration tier, against a local database
```

Root `AGENTS.md` — the agent guide, about 600 words: what the product is; where code and spec live; the two commands above; the delivery mode; three rules no gate enforces, each with its reason (for example: "no external call inside a database transaction — the database rolls back, the outside world does not"); where tasks are defined. Root `CLAUDE.md` contains only `@AGENTS.md`.
