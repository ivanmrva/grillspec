#!/usr/bin/env python3
"""Validate generated dual-host release artifacts. Run after build/build.py."""
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
errors = []

def fail(message):
    errors.append(message)

if (DIST / "full-system").exists():
    fail("retired dist/full-system directory survived the build; release surface is stale")

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: {exc}")
        return {}

source_claude = load(ROOT / "plugin" / ".claude-plugin" / "plugin.json")
source_codex = load(ROOT / "plugin" / ".codex-plugin" / "plugin.json")
if source_claude.get("version") != source_codex.get("version"):
    fail("source Claude Code and Codex plugin versions differ")

market = DIST / "marketplace"
claude_market = load(market / ".claude-plugin" / "marketplace.json")
codex_market = load(market / ".agents" / "plugins" / "marketplace.json")
plugin = market / "plugins" / "grillspec"
claude_plugin = load(plugin / ".claude-plugin" / "plugin.json")
codex_plugin = load(plugin / ".codex-plugin" / "plugin.json")
versions = {source_claude.get("version"), source_codex.get("version"),
            claude_plugin.get("version"), codex_plugin.get("version")}
if len(versions) != 1:
    fail(f"release plugin versions differ: {sorted(str(v) for v in versions)}")

try:
    if claude_market["plugins"][0]["source"] != "./plugins/grillspec":
        fail("Claude marketplace does not point at the shared plugin folder")
    if codex_market["plugins"][0]["source"]["path"] != "./plugins/grillspec":
        fail("Codex marketplace does not point at the shared plugin folder")
except (KeyError, IndexError, TypeError):
    fail("one or both marketplace manifests have an invalid plugin entry")

standalone = sorted((DIST / "skills").glob("*/SKILL.md"))
bundled = sorted((plugin / "skills").glob("*/SKILL.md"))
if len(standalone) != 46:
    fail(f"standalone skill count is {len(standalone)}, expected 46 workers")
if len(bundled) != 47:
    fail(f"marketplace skill count is {len(bundled)}, expected conductor + 46 workers")

portable_roots = [DIST / "skills", plugin]
portable_roots.extend(p for p in (DIST / "plugins").glob("*") if p.is_dir())
frontmatter = re.compile(r"^---\n(.*?)\n---", re.S)
for root in portable_roots:
    for skill in root.glob("skills/*/SKILL.md") if root.name != "skills" else root.glob("*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        rel = skill.relative_to(ROOT)
        if "${CLAUDE_PLUGIN_ROOT}" in text:
            fail(f"{rel}: retains a plugin-root reference")
        match = frontmatter.match(text)
        if not match:
            fail(f"{rel}: missing frontmatter")
            continue
        if re.search(r"^(argument-hint|disable-model-invocation):", match.group(1), re.M):
            fail(f"{rel}: retains host-specific frontmatter")
        if not skill.parent.joinpath("agents", "openai.yaml").is_file():
            fail(f"{rel}: missing agents/openai.yaml")
        for folder, pattern in (("references", r"`references/([^`\s]+)"),
                                ("scripts", r"`scripts/([^`\s]+)")):
            for target in re.findall(pattern, text):
                target = target.rstrip(".,;:)")
                if not skill.parent.joinpath(folder, target).exists():
                    fail(f"{rel}: unresolved {folder}/{target}")

# Project-state compatibility across every generated artifact. Host directories may contain their native
# adapters/catalogs, but GrillSpec-owned tools, locks, waivers, and gate state are always neutral.
legacy_state = re.compile(
    r"\.(?:claude|codex)/(?:tools/|(?:derived|freshness)\.lock|grillspec-gate\.json|"
    r"[A-Za-z0-9_-]+-allow\.txt|deploy-real-commands\.txt|migration-real-dirs\.txt)")
text_suffixes = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt"}
for path in DIST.rglob("*"):
    if (not path.is_file() or path.suffix.lower() not in text_suffixes or
            path.name in {"CHANGELOG.md", "selfcheck.py"} or path.name.startswith("test_")):
        continue
    match = legacy_state.search(path.read_text(encoding="utf-8", errors="replace"))
    if match:
        fail(f"{path.relative_to(ROOT)}: generated legacy project-state path {match.group(0)!r}")

# Release ZIPs are a separate generated surface: clear stale archives in build.py, then verify the
# archive inventory and contents instead of assuming they mirror the unpacked directories.
archives = sorted(DIST.glob("grillspec-*.zip"))
if archives:
    expected = {
        "grillspec-claude-plugin.zip", "grillspec-codex-plugin.zip",
        "grillspec-full-system.zip", "grillspec-marketplace.zip", "grillspec-skills.zip",
    }
    plugins_dir = DIST / "plugins"
    if plugins_dir.is_dir():
        expected.update(f"grillspec-plugin-{path.name}.zip"
                        for path in plugins_dir.iterdir() if path.is_dir())
    actual = {path.name for path in archives}
    for name in sorted(expected - actual):
        fail(f"missing release archive: dist/{name}")
    for name in sorted(actual - expected):
        fail(f"stale/unexpected release archive: dist/{name}")
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as bundle:
                for info in bundle.infolist():
                    name = info.filename
                    if name.startswith("full-system/"):
                        fail(f"{archive.name}: retired full-system directory is archived")
                    if "/.claude/tools/" in "/" + name or "/.codex/tools/" in "/" + name:
                        fail(f"{archive.name}: host-specific project tools are archived at {name}")
                    path = Path(name)
                    if (info.is_dir() or path.suffix.lower() not in text_suffixes or
                            path.name in {"CHANGELOG.md", "selfcheck.py"} or
                            path.name.startswith("test_")):
                        continue
                    match = legacy_state.search(bundle.read(info).decode("utf-8", errors="replace"))
                    if match:
                        fail(f"{archive.name}:{name}: legacy project-state path {match.group(0)!r}")
        except (OSError, zipfile.BadZipFile) as exc:
            fail(f"{archive.relative_to(ROOT)}: unreadable release archive ({exc})")

installers = list(DIST.rglob("install_exec_gates.py"))
if not installers:
    fail("release contains no install_exec_gates.py")
for path in installers:
    text = path.read_text(encoding="utf-8")
    for required in (
        '$CLAUDE_PROJECT_DIR/.grillspec/tools/gate_exec.py',
        '$(git rev-parse --show-toplevel)/.grillspec/tools/gate_exec.py',
        'root / ".grillspec" / "tools"',
    ):
        if required not in text:
            fail(f"{path.relative_to(ROOT)}: shared hook/tool invariant missing {required!r}")

guards = list(DIST.rglob("guard_derived.py"))
if not guards:
    fail("release contains no guard_derived.py")
for path in guards:
    text = path.read_text(encoding="utf-8")
    if 'LOCK = os.path.join(".grillspec", "derived.lock")' not in text:
        fail(f"{path.relative_to(ROOT)}: derived lock is not under .grillspec")
    if 'CLAUDE_IMPORT = "@AGENTS.md\\n"' not in text:
        fail(f"{path.relative_to(ROOT)}: import-only CLAUDE.md invariant is absent")

derive_guides = list(DIST.rglob("skills/derive-conventions/SKILL.md"))
if not derive_guides:
    fail("release contains no derive-conventions skill")
for path in derive_guides:
    text = path.read_text(encoding="utf-8")
    if "`CLAUDE.md` with exactly `@AGENTS.md`" not in text:
        fail(f"{path.relative_to(ROOT)}: does not generate canonical AGENTS.md + CLAUDE import")

packaged_selfcheck = plugin / "tools" / "selfcheck.py"
if packaged_selfcheck.is_file():
    checked = subprocess.run(
        [sys.executable, str(packaged_selfcheck), str(plugin)],
        capture_output=True, text=True)
    if checked.returncode:
        fail("generated marketplace plugin fails its bundled selfcheck:\n" +
             (checked.stdout + checked.stderr).strip())
else:
    fail("generated marketplace plugin contains no bundled selfcheck.py")

print(f"release check: {len(standalone)} standalone skills, {len(bundled)} bundled skills")
for error in errors:
    print(f"  ERROR {error}")
print("VERDICT: PASS" if not errors else "VERDICT: FAIL")
sys.exit(1 if errors else 0)
