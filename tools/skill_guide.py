#!/usr/bin/env python3
"""
skill_guide.py - build an accurate per-skill user guide from the skill's OWN fields.

Single source of truth for guide text, imported by both gen-guides.py (writes docs/skills/)
and emit-standalone.py (ships a README.md beside each standalone skill). The guide is generated,
never hand-written, so it stays in sync with the skill - and reading it is the verification:
purpose, input, output and "what good looks like" all come straight from the profile.
"""
import re

def _frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""

def _description(text):
    fm = _frontmatter(text)
    m = re.search(r"description:\s*(?:>-|\|-?|>)?\s*\n?(.*?)(?:\n\w[\w-]*:|\Z)", fm, re.S)
    if not m:
        return ""
    d = re.sub(r"\s+", " ", m.group(1)).strip()
    return re.sub(r"\s*Loads the shared [a-z ]+ (?:engine|core)\.?$", "", d).strip()

def _family(text):
    m = re.search(r"(grill|derive|exec)-engine\.md", text)
    return m.group(1) if m else "grill"

def _title(text):
    m = re.search(r"\*\*([^*]+?)\*\*\s*\(stage:", text)
    return m.group(1).strip() if m else ""

def _stage(text):
    m = re.search(r"\(stage:\s*([^·)]+)", text)
    return m.group(1).strip() if m else ""

def _fields(text):
    f = {}
    for m in re.finditer(r"\n-\s*\*\*([^*]+?)\*\*\s*(.*?)(?=\n-\s*\*\*|\n\n|\n##|\n---|\Z)", text, re.S):
        f[m.group(1).strip().rstrip(":").strip()] = re.sub(r"\s+", " ", m.group(2)).strip()
    return f

def _standalone(text):
    m = re.search(r"\*\*Standalone default\*\*[^:]*:\s*write your artifact under `([^`]+)`", text)
    if m:
        return ("folder", m.group(1).rstrip("/"))
    m = re.search(r"\*\*Standalone default\*\*[^:]*:\s*write (.+?);", text)
    if m:
        return ("target", m.group(1).strip())
    m = re.search(r"##\s*Output[\s\S]*?under \*\*`([^`]+)`\*\*", text)
    return ("output", m.group(1).rstrip("/")) if m else (None, None)

def _example(text):
    m = re.search(r"## Worked example\s*\n(.*?)(?=\n## |\n\*\*Standalone default|\Z)", text, re.S)
    return m.group(1).strip() if m else ""

FAMILY_LABEL = {
    "grill":  "Interview skill — it asks you questions and writes a spec artifact",
    "derive": "Derivation skill — it generates an artifact from recorded input (no interview)",
    "exec":   "Build / verify skill — it does work in your repo (no interview)",
}

def build_guide(name, text, public=False):
    fam = _family(text); F = _fields(text)
    title = _title(text) or name
    stage = _stage(text)
    desc = _description(text)
    kind, where = _standalone(text)
    up = F.get("upstream"); IN = F.get("IN") or F.get("input") or F.get("In scope"); OUT = F.get("OUT")
    coverage = F.get("coverage") or F.get("Complete when"); seams = F.get("seams")
    never = F.get("never pass on"); verdict = F.get("verdict"); do = F.get("do")

    L = [f"# {title} — user guide", ""]
    if public:
        L += [f"**Invoke:** `/{name}`", ""]
    else:
        _inv = f"**Invoke:** `/{name}`  (plugin: `/grillspec:{name}`)"
        if stage: _inv += f"  ·  **Stage:** {stage}"
        L += [_inv, ""]
    L += [f"*{FAMILY_LABEL[fam]}.*", ""]
    if desc:
        if public:
            desc = re.sub(r"\s*\bThe hub:\s*", " ", desc).strip()
            desc = re.sub(r"\.\s+([a-z])", lambda m: ". " + m.group(1).upper(), desc)
        L += ["## What it does", desc, ""]

    # input
    L += ["## What it needs (input)"]
    if fam == "grill":
        L += ["A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. "
              "If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input."]
        if up and not public:  L += ["", f"*Upstream it draws on when present (uses what exists, flags what's missing):* {up}"]
        if IN:  L += ["", f"*What it elicits:* {IN}"]
    elif fam == "derive":
        L += ["The **recorded source artifacts** — it derives from them and does **not** interview you for facts. "
              "Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented."]
        if up and not public:  L += ["", f"*Upstream it reads:* {up}"]
        if IN:  L += ["", f"*What it produces from them:* {IN}"]
    else:
        L += [F.get("input") or do or "A task package and the code it touches."]
        if do and F.get("input"): L += ["", f"*What it does:* {do}"]
    L += [""]

    # output
    L += ["## What it produces (output)"]
    if public:
        if where:
            L += [f"Writes its output under **`{where}/`** — see the **Output** section in the skill for the complete file tree. "
                  f"Not every file is always produced; create one only when the work needs it."]
        else:
            L += ["See the **Output** section in the skill for the complete file tree — not every file is always produced."]
    elif kind == "target":
        L += [f"Writes **{where}**."]
    elif where:
        L += [f"Writes its artifact under **`{where}/`**, and its ADRs to the shared **`adr/`** folder (prefixed with its area code). "
              f"There are no shared companion files; the conductor reconciles cross-area views (glossary, actors, bets) by reading outputs."]
    else:
        L += [F.get("output →", "Writes its artifact.")]
    if OUT and not public:
        L += ["", f"*Out of scope (lives downstream):* {OUT}"]
    L += [""]

    # how to run
    if public:
        L += ["## How to use it",
              f"Copy the `{name}/` folder into `~/.claude/skills/` (for all your projects) or a project's `.claude/skills/`, then run `/{name}`. Everything it needs is in this one folder - edit any of it to fit your project.",
              ""]
    else:
        L += ["## How to run it",
              f"- **In the bundle plugin:** `/grillspec:{name}`",
              f"- **Standalone:** copy the `{name}/` folder into `~/.claude/skills/`, then run `/{name}`. It works on its own and composes with sibling skills, each writing to its own output folder.",
              ""]

    # verification (the point Ivan cares about)
    L += ["## How to tell it did its job  *(verification)*"]
    if fam in ("grill", "derive") and coverage:
        L += [f"It has done its job when **every one of these holds** — read the output against this list:", "", coverage, ""]
    if never:
        L += [f"**It must never pass on:** {never}", ""]
    if verdict:
        L += [f"**Gate signal:** {verdict}", ""]
    if not (coverage or never or verdict):
        L += ["Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).", ""]

    if fam == "grill":
        L += ["> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks "
              "(not quiz you on the obvious), and **never speak its internal jargon** at you.", ""]

    ex = _example(text)
    if ex:
        L += ["## Example", ex, ""]

    if not public and (up or seams):
        L += ["## Where it sits in the system"]
        if up:    L += [f"- **Upstream (feeds it):** {up}"]
        if seams: L += [f"- **Connects to:** {seams}"]
        L += [""]

    return title, "\n".join(L).rstrip() + "\n"
