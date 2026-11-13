#!/usr/bin/env python3
"""project_config.py - the project's two Grillspec settings, in `.grillspec/project.json`.

    profile   lite | standard | regulated     how much spec the project carries
    delivery  trunk | pr                      how work lands

Both are facts only the project owner holds, so the conductor asks them once and records them here; every
tool that scales with them reads this one file. With no file the widest reading applies (`regulated` +
`pr`), so nothing is ever skipped by accident.

Usage:
    python3 tools/project_config.py                       # print the effective settings
    python3 tools/project_config.py --json                # ... as JSON
    python3 tools/project_config.py --set profile=standard --set delivery=trunk
    python3 tools/project_config.py --root <project-dir> ...

Importable: `load(root) -> {"profile": ..., "delivery": ..., "explicit": bool}`. Stdlib only.
"""
import json
import pathlib
import sys

PROFILES = ("lite", "standard", "regulated")
DELIVERY = ("trunk", "pr")
DEFAULTS = {"profile": "regulated", "delivery": "pr"}
ALLOWED = {"profile": PROFILES, "delivery": DELIVERY}
REL_PATH = pathlib.Path(".grillspec") / "project.json"


def config_path(root):
    return pathlib.Path(root) / REL_PATH


def load(root="."):
    """The effective settings. An absent, unreadable, or out-of-vocabulary value falls back to its default."""
    out = dict(DEFAULTS)
    explicit = False
    p = config_path(root)
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            data = {}
        if isinstance(data, dict):
            for key, allowed in ALLOWED.items():
                val = str(data.get(key, "")).strip().lower()
                if val in allowed:
                    out[key] = val
                    explicit = True
    out["explicit"] = explicit
    return out


def profile_rank(profile):
    """lite=0 < standard=1 < regulated=2; an unknown name ranks as the widest."""
    return PROFILES.index(profile) if profile in PROFILES else len(PROFILES) - 1


def save(root, updates):
    p = config_path(root)
    data = {}
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            data = {}
        if not isinstance(data, dict):
            data = {}
    data.update(updates)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def main(argv):
    root, sets, as_json = ".", {}, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]; i += 2; continue
        if a == "--set" and i + 1 < len(argv):
            key, _, val = argv[i + 1].partition("=")
            key, val = key.strip().lower(), val.strip().lower()
            if key not in ALLOWED:
                print("project_config: unknown setting %r - use %s" % (key, " | ".join(sorted(ALLOWED))))
                return 2
            if val not in ALLOWED[key]:
                print("project_config: %s must be one of %s (got %r)" % (key, " | ".join(ALLOWED[key]), val))
                return 2
            sets[key] = val; i += 2; continue
        if a == "--json":
            as_json = True; i += 1; continue
        print(__doc__.strip())
        return 0 if a in ("-h", "--help") else 2
    if sets:
        print("project_config: wrote %s" % save(root, sets))
    cfg = load(root)
    if as_json:
        print(json.dumps(cfg, sort_keys=True))
    else:
        note = "" if cfg["explicit"] else "  (no %s - defaults apply)" % REL_PATH.as_posix()
        print("profile: %s\ndelivery: %s%s" % (cfg["profile"], cfg["delivery"], note))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
