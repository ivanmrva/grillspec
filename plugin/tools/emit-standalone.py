#!/usr/bin/env python3
"""Bundle one or more source skills into a self-contained dual-host plugin.

The canonical source uses plugin-root references. This installed-plugin-safe emitter rewrites
them into portable relative references/scripts and adds Agent Skills metadata plus both Claude
Code and Codex plugin manifests.

Usage:
  python3 tools/emit-standalone.py grill-ddd                 -> dist/standalone/grill-ddd/
  python3 tools/emit-standalone.py --public grill-ddd        -> dist/public/grill-ddd/
  python3 tools/emit-standalone.py --public --name post3 implement-task conformance-review run-tests
"""
import sys, json, shutil, argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # the grillspec/ plugin root
SHARED = ROOT / "grill-shared"
SKILLS = ROOT / "skills"
TOOLS = ROOT / "tools"
SHARED_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/([A-Za-z0-9_-]+\.(?:md|json))")
SHARED_PREFIX = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/")
TOOL_PREFIX = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/tools/")
DOC_PREFIX = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/docs/")
PORTABLE_TOOLS = (
    "check_freshness.py", "check_orphan_tests.py", "check_task_record.py", "gate_exec.py",
    "guard_derived.py", "impact.py", "install_exec_gates.py", "lint_spec.py",
    "plugin_feedback.py", "tier_contract.py",
)
MIT_LICENSE = (
    "MIT License\n\nCopyright (c) 2026 Ivan Mrva\n\n"
    "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
    "of this software and associated documentation files (the \"Software\"), to deal\n"
    "in the Software without restriction, including without limitation the rights\n"
    "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
    "copies of the Software, and to permit persons to whom the Software is\n"
    "furnished to do so, subject to the following conditions:\n\n"
    "The above copyright notice and this permission notice shall be included in all\n"
    "copies or substantial portions of the Software.\n\n"
    "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
    "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
    "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
    "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
    "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
    "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
    "SOFTWARE.\n")

def shared_refs(text):
    return set(SHARED_REF.findall(text))


def transitive_shared(seeds):
    need, seen = set(seeds), set()
    while need - seen:
        filename = (need - seen).pop()
        seen.add(filename)
        path = SHARED / filename
        if path.exists():
            need |= shared_refs(path.read_text(encoding="utf-8"))
    return sorted(seen)


def portable_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return text
    out = [lines[0]]
    for index in range(1, len(lines)):
        line = lines[index]
        if line == "---":
            out.extend(lines[index:])
            return "\n".join(out) + ("\n" if text.endswith("\n") else "")
        if not re.match(r"^(argument-hint|disable-model-invocation):", line):
            out.append(line)
    return text


def portable_text(text):
    text = portable_frontmatter(text)
    text = SHARED_PREFIX.sub("references/", text)
    text = TOOL_PREFIX.sub("scripts/", text)
    return DOC_PREFIX.sub("references/", text)


def resource_note(text):
    marker = "<!-- grillspec-portable-resources -->"
    if marker in text:
        return text
    match = re.match(r"^(---\n.*?\n---\n)", text, re.S)
    if not match:
        return text
    note = ("\n" + marker + "\n"
            "> Resource paths in this skill are relative to this installed skill directory. "
            "Resolve `references/...` and `scripts/...` from that directory, not from the project "
            "working directory; use an absolute path when executing a bundled script.\n")
    return text[:match.end()] + note + text[match.end():]


def description(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return ""
    lines = match.group(1).splitlines()
    for index, line in enumerate(lines):
        found = re.match(r"^description:\s*(.*)$", line)
        if not found:
            continue
        rest = found.group(1).strip()
        if rest not in (">", ">-", ">+", "|", "|-", "|+", ""):
            return rest.strip('"').strip("'")
        values = []
        for candidate in lines[index + 1:]:
            if candidate[:1] not in (" ", "\t") and candidate.strip():
                break
            values.append(candidate.strip())
        return " ".join(value for value in values if value)
    return ""


def display_name(name):
    return " ".join(part.upper() if part in {"api", "ddd", "ml", "ui", "ux"}
                    else part.title() for part in name.split("-"))


def openai_yaml(name, summary, allow_implicit):
    plain = re.sub(r"[`*_#]", "", summary).strip()
    short = plain if len(plain) <= 61 else plain[:61].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
    if len(short) < 25:
        short = (short + " workflow for Grill Spec").strip()
    prompt = f"Use ${name} to {summary[:1].lower() + summary[1:]}"
    if len(prompt) > 180:
        prompt = prompt[:177].rsplit(" ", 1)[0] + "…"
    return ("interface:\n"
            f"  display_name: {json.dumps(display_name(name))}\n"
            f"  short_description: {json.dumps(short[:64])}\n"
            f"  default_prompt: {json.dumps(prompt)}\n"
            "policy:\n"
            f"  allow_implicit_invocation: {'true' if allow_implicit else 'false'}\n")


def build_portable_skill(name, out, license_text):
    src = SKILLS / name
    source_text = (src / "SKILL.md").read_text(encoding="utf-8")
    shared = transitive_shared(shared_refs(source_text))
    shared_text = "\n".join(
        (SHARED / filename).read_text(encoding="utf-8") for filename in shared
        if (SHARED / filename).is_file())
    combined = source_text + "\n" + shared_text + "\n" + "\n".join(
        path.read_text(encoding="utf-8") for path in src.rglob("*.md")
        if path.name != "SKILL.md")

    target = out / name
    target.mkdir(parents=True, exist_ok=True)
    (target / "SKILL.md").write_text(resource_note(portable_text(source_text)), encoding="utf-8")
    if shared:
        refs = target / "references"
        refs.mkdir()
        for filename in shared:
            source = SHARED / filename
            if source.is_file():
                (refs / filename).write_text(portable_text(source.read_text(encoding="utf-8")),
                                             encoding="utf-8")
    for extra in sorted(src.iterdir()):
        if extra.name in {"SKILL.md", "agents"}:
            continue
        destination = target / extra.name
        if extra.is_dir():
            shutil.copytree(extra, destination)
            for markdown in destination.rglob("*.md"):
                markdown.write_text(portable_text(markdown.read_text(encoding="utf-8")),
                                    encoding="utf-8")
        elif extra.suffix == ".md":
            destination.write_text(portable_text(extra.read_text(encoding="utf-8")),
                                   encoding="utf-8")
        else:
            shutil.copy2(extra, destination)
    if "${CLAUDE_PLUGIN_ROOT}/tools/" in combined:
        scripts = target / "scripts"
        scripts.mkdir()
        for filename in PORTABLE_TOOLS:
            shutil.copy2(TOOLS / filename, scripts / filename)
    if "${CLAUDE_PLUGIN_ROOT}/docs/DEPENDENCY-GRAPH.md" in combined:
        refs = target / "references"
        refs.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "docs" / "DEPENDENCY-GRAPH.md", refs / "DEPENDENCY-GRAPH.md")
    agents = target / "agents"
    agents.mkdir(exist_ok=True)
    existing_metadata = src / "agents" / "openai.yaml"
    if existing_metadata.is_file():
        shutil.copy2(existing_metadata, agents / "openai.yaml")
    else:
        allow_implicit = "disable-model-invocation: true" not in source_text
        (agents / "openai.yaml").write_text(
            openai_yaml(name, description(source_text), allow_implicit), encoding="utf-8")
    (target / "LICENSE").write_text(license_text, encoding="utf-8")
    residual = [path for path in target.rglob("*.md")
                if "${CLAUDE_PLUGIN_ROOT}" in path.read_text(encoding="utf-8")]
    if residual:
        sys.exit("ERROR: portable skill retains plugin-root references: %s" % residual)
    return shared


def codex_manifest(name, summary, license_id):
    return {
        "name": name, "version": "1.0.0", "description": summary,
        "author": {"name": "Ivan Mrva", "url": "https://github.com/ivanmrva"},
        "homepage": "https://github.com/ivanmrva/grillspec",
        "repository": "https://github.com/ivanmrva/grillspec",
        "license": license_id,
        "keywords": ["spec-driven", "domain-driven-design", "requirements", "architecture"],
        "skills": "./skills/",
        "interface": {
            "displayName": display_name(name),
            "shortDescription": "Spec-driven engineering skill bundle",
            "longDescription": summary,
            "developerName": "Ivan Mrva",
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "websiteURL": "https://github.com/ivanmrva/grillspec",
            "defaultPrompt": ["Use this Grill Spec skill bundle for the current task."],
        },
    }


def bundle(skills, outdir, name, public=False):
    outdir = Path(outdir)
    if outdir.exists():
        shutil.rmtree(outdir)
    (outdir / ".claude-plugin").mkdir(parents=True)
    (outdir / ".codex-plugin").mkdir(parents=True)
    shared = set()
    license_id = "MIT" if public else "Apache-2.0"
    license_text = (MIT_LICENSE if public else
                    (ROOT / "LICENSE").read_text(encoding="utf-8"))
    for skill in skills:
        src = ROOT / "skills" / skill
        if not (src / "SKILL.md").exists():
            sys.exit(f"ERROR: no such skill: {skill}")
        shared.update(build_portable_skill(skill, outdir / "skills", license_text))

    description = f"Spec-driven engineering skill(s): {', '.join(skills)}."
    (outdir / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": name, "version": "1.0.0",
        "description": description,
        "keywords": ["spec-driven", "ddd", "claude-code", "codex", "skills"],
        "license": license_id,
    }, indent=2) + "\n", encoding="utf-8")
    (outdir / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(codex_manifest(name, description, license_id), indent=2) + "\n",
        encoding="utf-8")
    (outdir / "LICENSE").write_text(license_text, encoding="utf-8")
    (outdir / "README.md").write_text(
        f"# {name}\n\nStandalone Claude Code and Codex skill bundle: **{', '.join(skills)}**.\n\n"
        "Each skill contains its required portable references, scripts, and Agent Skills metadata.\n",
        encoding="utf-8")
    invocations = "\n".join(
        f"- `/{name}:{skill}` in Claude Code or `${name}:{skill}` in Codex"
        for skill in skills)
    (outdir / "GUIDE.md").write_text(
        f"# {display_name(name)} - User Guide\n\n"
        "Install this directory as a plugin in Claude Code or Codex, then invoke a bundled skill:\n\n"
        f"{invocations}\n", encoding="utf-8")
    return outdir, sorted(shared)

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="+")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--name", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    name = a.name or (a.skills[0] if len(a.skills) == 1 else "grill-spec-bundle")
    base = ROOT / "dist" / ("public" if a.public else "standalone")
    out = Path(a.out) if a.out else base / name
    od, shared = bundle(a.skills, out, name, a.public)
    print(f"bundled {len(a.skills)} skill(s) -> {od}")
    print(f"  shared files included: {shared or '(none)'}")

if __name__ == "__main__":
    main(sys.argv[1:])
