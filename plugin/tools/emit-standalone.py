#!/usr/bin/env python3
"""Bundle one or more source skills into a self-contained standalone plugin.

In the conductor-free model the SOURCE `SKILL.md` is already the shippable form: each
worker loads its shared method via `${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>-engine.md`.
This tool copies the requested skill(s) + every shared file they (transitively) reference
+ plugin.json/LICENSE into a self-contained plugin folder. No content transformation.

Usage:
  python3 tools/emit-standalone.py grill-ddd                 -> dist/standalone/grill-ddd/
  python3 tools/emit-standalone.py --public grill-ddd        -> dist/public/grill-ddd/
  python3 tools/emit-standalone.py --public --name post3 implement-task conformance-review run-tests
"""
import sys, json, shutil, re, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # the grillspec/ plugin root
SHARED_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/([A-Za-z0-9_-]+\.md)")
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

def resolve_shared(seed_files):
    """Transitively collect every grill-shared/*.md a set of files references."""
    need, seen = set(seed_files), set()
    while need - seen:
        f = (need - seen).pop(); seen.add(f)
        p = ROOT / "grill-shared" / f
        if p.exists():
            need |= shared_refs(p.read_text(encoding="utf-8"))
    return sorted(seen)

def bundle(skills, outdir, name, public=False):
    outdir = Path(outdir)
    if outdir.exists(): shutil.rmtree(outdir)
    (outdir / ".claude-plugin").mkdir(parents=True)
    shared_seed = set()
    for s in skills:
        src = ROOT / "skills" / s
        if not (src / "SKILL.md").exists():
            sys.exit(f"ERROR: no such skill: {s}")
        dst = outdir / "skills" / s; dst.mkdir(parents=True)
        for fn in ("SKILL.md", "examples.md"):
            if (src / fn).exists(): shutil.copy2(src / fn, dst / fn)
        shared_seed |= shared_refs((src / "SKILL.md").read_text(encoding="utf-8"))
    shared = resolve_shared(shared_seed)
    if shared:
        (outdir / "grill-shared").mkdir(parents=True)
        for f in shared:
            sp = ROOT / "grill-shared" / f
            if sp.exists(): shutil.copy2(sp, outdir / "grill-shared" / f)
    (outdir / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": name, "version": "1.0.0",
        "description": f"Spec-driven engineering skill(s): {', '.join(skills)}.",
        "keywords": ["spec-driven", "ddd", "claude-code", "skills"],
        "license": "MIT" if public else "Apache-2.0",
    }, indent=2) + "\n", encoding="utf-8")
    if public:
        (outdir / "LICENSE").write_text(MIT_LICENSE, encoding="utf-8")   # public skills ship MIT (see RELEASING-PUBLICLY.md)
    elif (ROOT / "LICENSE").exists():
        shutil.copy2(ROOT / "LICENSE", outdir / "LICENSE")
    (outdir / "README.md").write_text(
        f"# {name}\n\nStandalone Claude Code skill bundle: **{', '.join(skills)}**.\n\n"
        f"Each skill loads its shared method from `grill-shared/`; "
        f"`${{CLAUDE_PLUGIN_ROOT}}` resolves that path once installed as a plugin.\n", encoding="utf-8")
    return outdir, shared

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
