---
name: derive-conventions
description: >-
  Derive the coding agent's standards and runway from the architecture — style, boundary rules as fitness checks, workflow, build/run/test/lint commands, Definition of Done — and generate the root CLAUDE.md. Use when the architecture exists and you need the coding-agent setup. Loads the shared derive core.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-conventions

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Coding conventions & agent setup** — the instruction-set Claude Code follows to produce code, plus its entry point.

## Method
1. confirm language/framework (from the architecture) → naming/style/error-handling
2. layering & dependency (boundary) rules → test approach
3. engineering workflow (branch-per-task · MR · hooks · CI gates · review)
4. the exact commands → the Definition of Done
5. the CODE pre-commit hooks (incl. a fast SAST pass + a dependency-audit / lockfile-integrity step) + a commit-msg hook validating Conventional Commits + the build-provenance / artifact-signing convention + design-token pipeline governance → generate root `CLAUDE.md`

## Rules
- standards set; dependency/boundary rules explicit and expressed as **enforceable fitness rules**; **no unpinned deps, lockfile committed** is one such rule (audited in-hook)
- frontend/design-system conventions are fitness rules too: semantic/component tokens only (never primitives/raw hex/px), build only design-system components (their variants · sizes · states) per the implementation mapping, copy follows the voice guide; **design-token pipeline governance** — one token source-of-truth · a named transform tool · a token-pair **contrast** a11y check on every semantic foreground/background pairing
- workflow defined (trunk-based · branch per task, no direct commits to main · one MR/PR per task · Conventional Commits enforced by a commit-msg hook)
- **build provenance** — target a stated SLSA build level · artifacts signed · ≥2-person review / branch protection on the release path
- build/test/lint commands runnable; DoD includes 'merged via green CI'
- **CODE governance only** — the pre-commit hooks govern `src/`+`tests/` only (format · lint · type · secret-scan · fast unit · the mechanical conformance subset: boundary/dependency fitness functions + contract checks, on the changed scope). The *spec/docs* are governed by a **separate** framework-level enforcer (`lint_spec.py` + `guard_derived.py` over `spec/`, + the doc-site); scope the hooks by path even when co-located. The *checks* are not optional; the *release* decision stays the team's
- CLAUDE.md generated

## Output
Written under `delivery/conventions/`:

| File | Captures | Format |
|---|---|---|
| `coding-standards.md` | language · style · naming · error-handling (as enforceable fitness rules) | typed rule sections |
| `frontend-conventions.md` | design-system usage: semantic/component tokens only (no primitives/raw values) · DS components · voice — as fitness rules · design-token pipeline governance (source-of-truth · transform tool · token-pair contrast a11y check) | typed rule sections |
| `boundary-rules.md` | layering & dependency allow/deny list (arch boundaries as fitness rules) · no-unpinned-deps / lockfile-committed | explicit allow/deny list |
| `workflow.md` | branching (trunk-based · branch per task) · one MR/PR per task · Conventional Commits · build provenance (target SLSA build level · signed artifacts · ≥2-person review / branch protection) · Definition of Done + merge policy | prose |
| `pre-commit-hooks.md` | the CODE hooks (src/+tests/ only): format · lint · type · secret-scan · fast SAST · dependency-audit / lockfile-integrity · fast unit · mechanical conformance subset; + a commit-msg hook validating Conventional Commits | commands as code blocks |

Also emits root `CLAUDE.md` — the agent's entry point: spec map · conventions · workflow · task index · how to work a task · DoD; a tight pointer file
ADRs → `adr/ADR-CONV-NNN.md`
*(DERIVED & regenerate-only)*
Consumes: the architecture — its stack choice, layering, and boundaries; and the test strategy's two tiers.

## Excludes
the task list · the code & the actual hook/CI config files

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
