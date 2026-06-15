# derive-conventions — worked example

From the architecture (TypeScript · ports-and-adapters · Scheduling and FieldWork contexts): the coding-agent's standards and runway. Boundary rules are written as *enforceable* fitness checks, not prose advice.

## Output
`delivery/conventions/boundary-rules.md` — one boundary rule, machine-checked:

```
RULE bnd-01  "Scheduling never imports FieldWork internals"
  deny   src/scheduling/**  ->  src/fieldwork/!(contracts)/**
  allow  src/scheduling/**  ->  src/fieldwork/contracts/**   # cross-context only via published contract
  check  dependency-cruiser rule `no-cross-context-internals` (CI + pre-commit)
RULE bnd-02  "domain depends on nothing outward"
  deny   src/*/domain/**  ->  src/*/{infra,adapter,api}/**
RULE dep-01  "no unpinned deps; lockfile committed"
  check  npm ci --frozen-lockfile  +  `npm audit --audit-level=high` (in-hook)
```

`delivery/conventions/pre-commit-hooks.md` — the CODE hooks (govern `src/` + `tests/` only; spec is governed by a separate framework-level enforcer):

```bash
# .pre-commit (changed scope only)
biome format --write          # format
biome lint                    # lint
tsc --noEmit                  # type
gitleaks protect --staged     # secret-scan
semgrep --config auto --error # fast SAST
npm ci --frozen-lockfile && npm audit --audit-level=high  # dependency-audit / lockfile-integrity
vitest related --run          # fast unit (changed)
depcruise --validate          # mechanical conformance subset: boundary fitness fns (bnd-01/02)
# commit-msg hook:
commitlint --edit "$1"        # Conventional Commits enforced
```

`delivery/conventions/frontend-conventions.md` — design-system usage as fitness rules:

```
RULE fe-01  "semantic/component tokens only — never primitives/raw hex/px"   check  stylelint design-token-only + CI scan of src/ui/**
RULE fe-02  "build only design-system components (variants · sizes · states), per the implementation mapping"
RULE fe-03  "token pipeline: one DTCG source-of-truth → Style Dictionary → CSS vars; token-pair contrast ≥ the WCAG target (CI)"
```

`delivery/conventions/workflow.md` — workflow + build provenance:
> trunk-based · branch per task · one MR/PR per task · Conventional Commits (commit-msg hook). **Provenance:** target **SLSA Build L3** · sign artifacts (cosign) · **≥2-person review + branch protection** on `main`. DoD: AC green · in-boundary · CI green · merged.

Root `CLAUDE.md` emitted: spec map · these conventions · trunk-based + branch-per-task workflow · task index · DoD ("merged via green CI"). The *checks* are non-optional; the *release* decision stays the team's.
