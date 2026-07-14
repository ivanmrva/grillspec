#!/usr/bin/env python3
"""
plugin_feedback.py - capture suggestions/fixes for the grillspec PLUGIN ITSELF.

A run (the conductor or any skill) sometimes hits friction that is a defect or gap in *this system*
- not in the user's project: a linter check that's demonstrably wrong, a skill instruction that
contradicts another or can't be satisfied, an ID type the schema needs but the linter rejects, a path
the structure won't allow that a skill is told to write, a stale doc reference. That signal has nowhere
to go today, so it's noticed by accident if at all. This tool is the sink: it appends a structured
entry to a SINGLE feedback file at the PROJECT ROOT (never under spec/ - the spec must stay free of any
awareness of this system). The plugin author harvests that file and ports fixes back to the plugin.

This is capture + route to a human, never self-patch: the plugin is read-only at runtime, and an LLM's
"is this a system bug?" over-fires - so every entry is a logged suggestion a person triages, not a
change. Keep the bar high: a deterministic contradiction or a rule that demonstrably can't be satisfied,
not "I'd have preferred...".

Usage:
    # append a finding (the normal path - called by a run when it identifies a system-level issue):
    python3 tools/plugin_feedback.py --add \
        --kind bug \
        --component tools/lint_spec.py \
        --summary "linter rejects _readiness.md which the conductor is told to write" \
        --detail  "allowed() whitelists only glossary/actors/adr/leaf-dirs; _readiness.md is read at line 130 but flagged 'outside structure'." \
        --suggest "whitelist spec-root _*.md in allowed()" \
        --evidence "spec/_readiness.md:1"

    # show the current file (path + entry count); creates an empty scaffold if absent:
    python3 tools/plugin_feedback.py [--root <project-root>]

--kind: bug | gap | improvement | docs   (default: improvement)
Exit 0 always (advisory). Stdlib only. Idempotent: an identical (kind, component, summary) is not
appended twice, so re-running a session doesn't duplicate entries.
"""
import sys, os, re, json, argparse, datetime, pathlib

FEEDBACK_FILE = "GRILLSPEC-FEEDBACK.md"          # at the PROJECT ROOT, a sibling of spec/ - NOT inside spec/
HEADER = (
    "# Grillspec plugin feedback\n\n"
    "Suggestions, fixes, and gaps for the **grillspec plugin itself** - surfaced by runs in this\n"
    "project. This file is NOT part of the spec; it has no bearing on the product. Each entry is a\n"
    "logged suggestion for the plugin author to triage and port back upstream - never an auto-applied\n"
    "change. Delete an entry once it's been actioned or dismissed.\n"
)


def plugin_version(root_hint):
    """Best-effort plugin version, for stamping which build a finding came from."""
    here = pathlib.Path(__file__).resolve().parent
    for base in (here.parent, root_hint):
        try:
            mani = base / ".claude-plugin" / "plugin.json"
            if mani.exists():
                return json.loads(mani.read_text()).get("version", "?")
        except Exception:
            pass
    return "?"


def find_project_root(arg):
    """The project root = where spec/ lives (or CWD). The feedback file sits here, beside spec/."""
    if arg:
        return pathlib.Path(arg).resolve()
    cwd = pathlib.Path.cwd()
    for d in (cwd, *cwd.parents):
        if (d / "spec").is_dir() or (d / ".git").is_dir():
            return d
    return cwd


def ensure_file(fp):
    if not fp.exists():
        fp.write_text(HEADER, encoding="utf-8")
    return fp.read_text(encoding="utf-8")


def already_present(body, kind, component, summary):
    # match on the entry's identifying line, normalized - keeps re-runs idempotent
    needle = f"- **kind:** {kind} · **component:** {component}"
    return needle in body and summary.strip()[:80] in body


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--add", action="store_true", help="append a finding")
    ap.add_argument("--kind", default="improvement", choices=["bug", "gap", "improvement", "docs"])
    ap.add_argument("--component", default="(unspecified)", help="skill/tool/engine the finding is about")
    ap.add_argument("--summary", default="", help="one-line summary of the finding")
    ap.add_argument("--detail", default="", help="what went wrong / why it's a system issue")
    ap.add_argument("--suggest", default="", help="proposed fix")
    ap.add_argument("--evidence", default="", help="file:line or ID that demonstrates it")
    ap.add_argument("--root", default="", help="project root (defaults to the spec/ or .git root above CWD)")
    a = ap.parse_args()

    root = find_project_root(a.root or None)
    fp = root / FEEDBACK_FILE
    body = ensure_file(fp)

    if not a.add:
        n = len(re.findall(r"^### ", body, re.M))
        print(f"{fp}  -  {n} entr{'y' if n == 1 else 'ies'}")
        return 0

    if not a.summary.strip():
        print("plugin_feedback: --add needs at least --summary", file=sys.stderr)
        return 0

    if already_present(body, a.kind, a.component, a.summary):
        print(f"plugin_feedback: already recorded - {a.summary[:60]}")
        return 0

    n = len(re.findall(r"^### ", body, re.M)) + 1
    day = datetime.date.today().isoformat()
    ver = plugin_version(root)
    entry = [f"\n### {n}. {a.summary.strip()}",
             f"- **kind:** {a.kind} · **component:** {a.component} · **plugin:** {ver} · **seen:** {day}"]
    if a.detail.strip():   entry.append(f"- **detail:** {a.detail.strip()}")
    if a.suggest.strip():  entry.append(f"- **suggested fix:** {a.suggest.strip()}")
    if a.evidence.strip(): entry.append(f"- **evidence:** {a.evidence.strip()}")
    entry.append("")
    with fp.open("a", encoding="utf-8") as f:
        f.write("\n".join(entry) + "\n")
    print(f"plugin_feedback: recorded #{n} -> {fp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
