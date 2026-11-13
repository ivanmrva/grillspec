# Grill Spec System — documentation

Documentation for the `grillspec` plugin for Claude Code and Codex. If you are new, read the plugin [README](../README.md) first, then come back here.

## Contents

| Page | Read it for |
|---|---|
| [HOW-IT-WORKS.md](HOW-IT-WORKS.md) | the whole system: profiles and delivery modes, the stages, task briefs and tiers, how done is decided, the tools |
| [WORKING.md](WORKING.md) | working fast: how a change travels, what is installed where, unattended building, tips by stage |
| [SPEC-CHECKS.md](SPEC-CHECKS.md) | every automated check, tool by tool, with its severity |
| [skills/](skills/README.md) | a guide for each skill: purpose, input, output, how to tell it did its job |
| [DEPENDENCY-GRAPH.md](DEPENDENCY-GRAPH.md) | what each area reads and produces; generated from `grill-shared/dependencies.json` |
| [LIVE-TEST.md](LIVE-TEST.md) | a 20-minute protocol to confirm a live agent follows the system after install |

## The short version

The system takes a product from an idea to a specification a coding agent can build from, and then to code that matches it. It does so through scoped interviews in plain language, derivations from what the interviews recorded, and a test-first build loop.

Three things set it apart from a document generator:

- **It stays small.** A project carries one of three profiles (`lite`, `standard`, `regulated`), and the conductor recommends the smallest that fits. An area, a file, a rule or a gate is written only when something reads it.
- **Spec health and bet health are reported separately.** Spec health asks whether the spec is consistent and complete enough. Bet health asks whether anyone wants the product and whether the business works: the bets recorded in the spec, each with a status, plus the kill-criteria. A consistent spec beside an untested bet is a result worth seeing. The system makes the build safer and the bet visible; only the market can settle the bet.
- **Done is read from the code.** A task is done when its acceptance criteria have tests that prove them and the project's gate is green. A tool checks that against the tree; nobody fills in a completion record.
