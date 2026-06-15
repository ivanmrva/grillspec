# grill-ml-reqs — user guide

**Invoke:** `/grill-ml-reqs`  (plugin: `/grillspec:grill-ml-reqs`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the requirements for an AI/ML feature — what the model must do and how well, its evaluation criteria (the acceptance tests for model behaviour), the training/feedback data it needs, confidence/fallback bars, human-in-the-loop points, and responsible-AI obligations. Use when the product embeds an ML or LLM capability that classical functional/quality requirements don't capture.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-ml-reqs`
- **Standalone:** copy the `grill-ml-reqs/` folder into `~/.claude/skills/`, then run `/grill-ml-reqs`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
