#!/usr/bin/env python3
"""
selfcheck.py - source-integrity check for the grillspec plugin.

Run this after editing skills, engines, hooks, or manifests. It validates the
*authoring* source (not a project's spec/ - that is what lint_spec.py does at
runtime). It catches the silent breakage modes of hand-editing 44 skill files:
malformed frontmatter, a missing/typo'd engine-load reference, a stale
`.claude/...` path that won't resolve once installed from the plugin cache,
broken manifest/hook JSON, a hook pointing at a missing or non-executable
script, or a tool that no longer compiles.

Usage:
    python3 tools/selfcheck.py            # checks the plugin rooted at CWD's parent of tools/
    python3 tools/selfcheck.py <plugin-dir>

Exit code 0 = PASS, 1 = FAIL. Stdlib only; no spec/ required.
"""
import sys, os, json, re, py_compile, pathlib

def find_plugin_root(arg):
    if arg:
        return pathlib.Path(arg)
    here = pathlib.Path(__file__).resolve().parent          # .../<plugin>/tools
    if (here.parent / ".claude-plugin" / "plugin.json").exists():
        return here.parent
    return pathlib.Path.cwd()

ROOT = find_plugin_root(sys.argv[1] if len(sys.argv) > 1 else None)
errs, warns = [], []
def err(m): errs.append(m)
def warn(m): warns.append(m)

# --- 1. manifest -----------------------------------------------------------
mani = ROOT / ".claude-plugin" / "plugin.json"
if not mani.exists():
    err(f"no manifest at {mani} - is {ROOT} a plugin root?")
else:
    try:
        m = json.loads(mani.read_text())
        if "name" not in m or not m["name"]:
            err("plugin.json: required field 'name' is missing/empty")
        elif " " in m["name"]:
            err(f"plugin.json: 'name' must be kebab-case, no spaces (got {m['name']!r})")
        if "version" not in m:
            warn("plugin.json: no 'version' - updates will key on git SHA (every commit = update)")
        if isinstance(m.get("keywords"), str):
            err("plugin.json: 'keywords' must be an array, not a string (load error)")
    except json.JSONDecodeError as e:
        err(f"plugin.json: invalid JSON - {e}")

# only plugin.json belongs in .claude-plugin/
cp = ROOT / ".claude-plugin"
if cp.exists():
    stray = [p.name for p in cp.iterdir() if p.name != "plugin.json"]
    if stray:
        err(f".claude-plugin/ must contain ONLY plugin.json; found also: {stray} "
            "(move components to the plugin root)")

# components must be at the plugin root, not inside .claude-plugin/
for d in ("skills", "agents", "hooks", "tools", "grill-shared"):
    if (cp / d).exists():
        err(f".claude-plugin/{d}/ is in the wrong place - move it to the plugin root")

# --- 2. skills -------------------------------------------------------------
skills_dir = ROOT / "skills"
if not skills_dir.is_dir():
    err("no skills/ directory at the plugin root")
    skills = []
else:
    skills = sorted(skills_dir.glob("*/SKILL.md"))
    if not skills:
        err("skills/ has no <name>/SKILL.md entries")

FM = re.compile(r"^---\n(.*?)\n---", re.S)
ENGINE_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/grill-shared/(grill|derive|exec)-engine\.md")
for sk in skills:
    name = sk.parent.name
    txt = sk.read_text()
    fm = FM.match(txt)
    if not fm:
        err(f"{name}: SKILL.md has no YAML frontmatter block")
        continue
    head = fm.group(1)
    if not re.search(r"^\s*name\s*:", head, re.M):
        err(f"{name}: frontmatter missing 'name:'")
    if not re.search(r"^\s*description\s*:", head, re.M):
        err(f"{name}: frontmatter missing 'description:'")
    # every worker skill must load a shared engine via a resolving ref; the conductor is exempt.
    is_conductor = "conductor" in name
    if not is_conductor and not ENGINE_REF.search(txt):
        warn(f"{name}: no resolved ${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>.md "
             "reference - a worker skill must load its shared engine")

# --- 3. stale paths (would break once installed from the cache) -----------
STALE = re.compile(r"(?<!\$\{CLAUDE_PLUGIN_ROOT\})\.claude/(grill-shared|tools|agents|skills|hooks)/")
for sub in ("skills", "grill-shared", "hooks", "agents"):
    base = ROOT / sub
    if not base.exists():
        continue
    for p in list(base.rglob("*.md")) + list(base.rglob("*.sh")) + list(base.rglob("*.json")):
        for ln in STALE.findall(p.read_text()):
            err(f"{p.relative_to(ROOT)}: stale '.claude/{ln}/...' path - "
                "use ${CLAUDE_PLUGIN_ROOT}/ so it resolves from the plugin cache")
            break

# --- 4. hooks --------------------------------------------------------------
hj = ROOT / "hooks" / "hooks.json"
if hj.exists():
    try:
        hooks = json.loads(hj.read_text())
        refs = re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/(\S+?\.sh)", json.dumps(hooks))
        for r in sorted(set(refs)):
            sp = ROOT / r.strip('"')
            if not sp.exists():
                err(f"hooks.json references {r} which does not exist")
            elif not os.access(sp, os.X_OK):
                warn(f"hook script {r} is not executable (chmod +x)")
    except json.JSONDecodeError as e:
        err(f"hooks/hooks.json: invalid JSON - {e}")

# --- 4b. ID-prefix drift: every type-prefix a skill declares must be known to the linter ---------
# Catches the silent failure where a skill gains a new ID type (`VO-`, `ML-`, …) but lint_spec.py's
# prefix tables aren't updated, so the linter can't register/check it. The linter's TYPES= line is the
# single source of truth; a declared-but-unknown prefix is flagged here so it never ships unchecked.
lint = ROOT / "tools" / "lint_spec.py"
if lint.exists():
    mt = re.search(r'^TYPES\s*=\s*"([^"]+)"', lint.read_text(), re.M)
    if not mt:
        warn("lint_spec.py: no single-line TYPES= constant found - cannot verify ID-prefix coverage")
    else:
        known = set(mt.group(1).split("|")) | {"ADR"}
        DECL = re.compile(r"`([A-Z][A-Z0-9]{1,4})-`")          # a declared bare type prefix, e.g. `AGG-`
        declared = {}
        for sk in skills:
            for pre in set(DECL.findall(sk.read_text())):
                declared.setdefault(pre, set()).add(sk.parent.name)
        for pre in sorted(set(declared) - known):
            warn(f"ID-prefix '{pre}-' is declared by {sorted(declared[pre])} but is UNKNOWN to "
                 f"lint_spec.py (add it to TYPES + ID_LAYER + PREFIX_OWNER, or stop emitting it) - "
                 "the linter cannot register or check it")

# --- 4c. dependency graph: valid + the rendered doc is in sync -------------
# Runs gen_depgraph.py --check: validates dependencies.json (prefixes known to the linter and owned by
# the right folder, edges resolve, acyclic) AND that docs/DEPENDENCY-GRAPH.md matches a fresh render.
import subprocess
dg = ROOT / "tools" / "gen_depgraph.py"
if dg.exists():
    r = subprocess.run([sys.executable, str(dg), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        for line in (r.stdout + r.stderr).strip().splitlines():
            err(f"dependency-graph: {line.strip()}")

# --- 5. tools compile ------------------------------------------------------
tools_dir = ROOT / "tools"
if tools_dir.is_dir():
    for py in sorted(tools_dir.glob("*.py")):
        if py.name == "selfcheck.py":
            continue
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as e:
            err(f"tools/{py.name}: does not compile - {e}")

# --- report ----------------------------------------------------------------
print(f"grillspec selfcheck - {len(skills)} skill(s) at {ROOT}")
for w in warns:
    print(f"  WARN  {w}")
for e in errs:
    print(f"  ERROR {e}")
print(f"\n{len(errs)} error(s), {len(warns)} warning(s).")
print("VERDICT: PASS" if not errs else "VERDICT: FAIL")
sys.exit(1 if errs else 0)
