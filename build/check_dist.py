#!/usr/bin/env python3
"""Validate generated dual-host release artifacts. Run after build/build.py."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
errors = []

def fail(message):
    errors.append(message)

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

print(f"release check: {len(standalone)} standalone skills, {len(bundled)} bundled skills")
for error in errors:
    print(f"  ERROR {error}")
print("VERDICT: PASS" if not errors else "VERDICT: FAIL")
sys.exit(1 if errors else 0)
