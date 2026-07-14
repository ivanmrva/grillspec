# Area profile — template (thin; the engine does the heavy lifting)

A profile is a thin layer on a shared engine. **Declare only what VARIES for this area** — the engine
(`grill-engine.md` / `derive-engine.md` / `exec-engine.md`) already owns everything universal: the
interview/derive/build method, the `<!-- scope | excludes | format -->` file header, the tight
no-walls-of-prose house style, ADR placement, and the rule that the output never names a skill or tool.
**Never restate an engine rule, and never say the same thing twice** (the description, the rules, and the
output table must not each re-list the same content — the output table is the single enumeration).

```
---
name: grill-<id>
description: >-
  <ONE-LINE HOOK — what it captures + when to use it, at a glance (NOT a restatement of every output
  file). Ends with "Loads the shared <grill|derive|exec> engine.">
disable-model-invocation: true
argument-hint: <what to hand it>
---

# grill-<id>

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>.md` first and follow it.** This skill applies that
method to **<Area>** — <one-line scope>.

## Method        ← OPTIONAL. The area's question order / approach — ONLY if it's a real sequence beyond
                   "fill in the files". If the process is just the list of things to capture, omit it:
                   the Output tree below IS the coverage.

## Rules         ← OPTIONAL. ONLY area-specific bars the engine doesn't carry — a gating trigger
                   ("GATED on real features to price"), a judgment rule ("authz is DEFAULT-DENY"), a
                   caveat ("coarse & revisable — don't over-ask"). NOT the file header, NOT "tight/no
                   prose", NOT output content restated as a rule.

## Output        Heading is just `## Output` (no path in it). A lead-in `Written under `<folder>/`:` then a
                   markdown TABLE — the single place the outputs are enumerated:
                     | File | Captures | Format |
                   File = the `filename` (or path, for nested trees) · Captures = what it holds (plain prose)
                   · Format = its row/shape (the table columns · `Mermaid` · `numbered steps` · `—`). Below
                   the table as plain lines: `ADRs → adr/ADR-<AREA>-NNN.md`, any `glossary.md`/`actors.md` owned.
   Consumes: ...  ← OPTIONAL one line — the upstream artifacts it reads, named as CONCEPTS, never skills
                   ("the domain model", "the quality NFRs"). Omit for foundation areas with no upstream.

## Excludes      The scope fence — what belongs to other areas, named as concepts (→ compliance, → the
                 architecture), never as skills.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>.md`   (+ any other loadable file, e.g. examples.md)
```

Exec profiles (build/verify skills) keep their `## Process` steps and their `never pass on` / `verdict` /
`Done` lines — those are area-specific, not engine duplicates — and their Output is code/records, not a
spec artifact.
