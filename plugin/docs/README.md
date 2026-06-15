# Grill Spec System — documentation

Documentation for the **`grillspec`** Claude Code plugin. New here? Start with the plugin [README](../README.md), then come back for depth.

## Contents

- **[`skills/`](skills/README.md)** — a user guide for every skill (purpose, input, output, and how to verify it), plus the full catalog. The fastest way to see what each skill does and how to invoke it.
- **[`HOW-IT-WORKS.md`](HOW-IT-WORKS.md)** — the pipeline end to end: the stages, the three shared engines, the `spec/` tree, the deterministic tools, and the build loop.
- **[`WORKING.md`](WORKING.md)** — working efficiently: how change-propagation works, the autonomous build loop, per-stage throughput, and model routing.
- **[`LIVE-TEST.md`](LIVE-TEST.md)** — a 20-minute protocol to confirm a live agent actually follows the system, and that the plugin resolves correctly after install.

## The short version

You drive a product from an idea to an implementation-ready, internally consistent specification — and on to spec-conformant code — through relentless, plain-language, scoped interviews and derivations. Two things make it more than a document generator:

- **Two orthogonal dashboards.** *Spec health* = is the spec consistent and complete enough. *Bet health* = does anyone want it, does the business work (`assumptions.md` + kill-criteria + PMF signals). A green spec next to a red bet is the point: the system de-risks the **build** and makes the **bet legible** — only the market can make the bet safe.
- **Discovery runs first and never closes.** The riskiest assumptions are named and given test plans up front; an *invalidated* critical assumption ripples upstream (the pivot loop) and can re-open scope, vision, even the domain model.
