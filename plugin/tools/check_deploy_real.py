#!/usr/bin/env python3
# check_deploy_real.py - a coarse, high-precision tripwire against FAKE deployment in the shipping path.
#
# Why it exists (the sibling of check_no_fakes.py for the deploy/release surface): the same adherence gap that
# lets a stub reach src/ lets a *deploy script* be quietly faked or skipped - a CI job that `echo "deploying"`s
# and exits 0, a workflow with the deploy step commented out or `if: false`, a `# TODO: implement deploy`
# placeholder - so the task reports "done · deployed" while nothing ever ships. The accountability gate
# (check_task_record.py) makes the deploy a CARRIED obligation; THIS makes "the artifact is real" mechanical.
# It is the cross-stack backstop that fires even before a project authors its own pipeline test.
#
# It is deliberately conservative (a noisy gate gets `--no-verify`d): it scans only deploy-INTENT artifacts and
# flags the signals that are almost always a fake.
#
# ERROR (a placeholder in a deploy artifact - the deploy doesn't really deploy):
#   - a TODO/FIXME/placeholder/"not implemented"/"coming soon"/"fill in"/"replace me"/"fake|stub deploy"/no-op
#     marker on a line of a deploy-intent file.
# WARN (a likely-skipped deploy - review, don't necessarily block):
#   - a disabled deploy job/step (`if: false`, `when: never`);
#   - a deploy-intent script/workflow that invokes NO recognized deploy/IaC command (echo-only "deployment").
# Suppress a finding with an inline `deploy-real: allow <reason>` comment on the line, or a path/substring entry
# in `.claude/deploy-real-allow.txt`. `--strict` promotes WARN -> ERROR.
#
# EXTENSIBLE: the built-in deploy-command list can't name every tool. Add a niche / in-house deployer (one
# literal token per line) to `.claude/deploy-real-commands.txt` and a deploy that uses it counts as real.
#
# LIMITATION (by design): this confirms a real deploy COMMAND runs - it does NOT verify the command targets the
# *ratified* environment (the right cluster/project/account). That is the behavioural check's job: the e2e/smoke
# against the real deployed env (authoritative) + the conformance reviewer confirming the target. This is the
# cheap static backstop for the window before that behavioural run can execute, not a substitute for it.
#
# No-ops cleanly when no deploy artifact exists (an early project hasn't wired CI yet). Run from project root:
#   python3 tools/check_deploy_real.py [project_root] [--strict]
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
STRICT = "--strict" in sys.argv

# a file is a DEPLOY-INTENT artifact when its path/name signals deploy/release, it sits under a deploy home, or
# (for a CI config) its CONTENT shows deploy intent. We do NOT scan all CI configs (a test/lint-only job has no
# deploy command and would false-positive) and do NOT scan all IaC (terraform/k8s rarely "fake") - only the
# artifacts that mean to deploy. Coverage: shell deploy scripts, GitHub/GitLab/Circle/Azure/Bitbucket/Drone/
# Cloud-Build/Jenkins CI configs, Dockerfiles, and the `deploy`-ish scripts/targets in package.json + Makefile.
DEPLOY_DIR = re.compile(r"(?:^|/)(?:deploy|release|cd|ci-cd|cicd)(?:/|$)", re.I)
DEPLOY_NAME = re.compile(r"(?:deploy|release|promote|rollout|rollback|ship)", re.I)
CI_FILE = re.compile(
    r"/(?:\.github/workflows/[^/]+\.ya?ml|\.gitlab-ci\.yml|\.circleci/config\.yml|"
    r"azure-pipelines\.ya?ml|bitbucket-pipelines\.yml|\.drone\.yml|cloudbuild\.ya?ml)$", re.I)
SCRIPT_EXT = {".sh", ".bash", ".zsh", ".ps1"}
WF_EXT = {".yml", ".yaml"}

# recognized real deploy / IaC / release verbs - presence means the artifact actually does something. Includes
# task-runner delegation (npm run / make / yarn / pnpm / just / task) so a deploy that hands off to a real
# target isn't mistaken for an empty one.
DEPLOY_CMD = re.compile(
    r"\b(?:kubectl|helm|helmfile|kustomize|skaffold|argocd|flux|kapp|"
    r"terraform|tofu|opentofu|pulumi|cdk|cdktf|sam|serverless|sls|sst|"
    r"ansible(?:-playbook)?|nomad|waypoint|"
    r"docker\s+(?:push|build|compose)|podman|buildah|nerdctl|skopeo|"
    r"aws|gcloud|az\b|azd|oc\b|openshift|"
    r"flyctl|fly\s+deploy|vercel|netlify|wrangler|supabase|firebase|amplify|"
    r"heroku|dokku|kamal|cap(?:istrano)?|mina|"
    r"rsync|scp|ssh|sftp|"
    r"gh\s+(?:release|workflow|deployment)|git\s+push|"
    r"npm\s+run|yarn\b|pnpm\b|bun\s+run|make\b|just\b|task\b|nx\b|turbo\b|mvn\b|gradle|"
    r"render|railway|fly|eb\b|elasticbeanstalk|ecs|eks|gke|aks)\b", re.I)

def is_noop_cmd(cmd):
    """A command string that does NOTHING real - empty, or only echo/printf/true/:/comment/`exit 0`, across all
    &&/;/|| -joined parts. Used for package.json scripts + Makefile recipes where a fake reads as `echo …`."""
    cmd = cmd.strip()
    if not cmd:
        return True
    for part in re.split(r"&&|\|\||;|\n", cmd):
        part = part.strip()
        if not part:
            continue
        if part.startswith("#") or part in ("true", ":", "exit 0") or re.match(r"^(?:echo|printf)\b", part):
            continue
        return False                                            # a real command part -> not a no-op
    return True

PLACEHOLDER = re.compile(
    r"(?i)\b(?:TODO|FIXME|XXX|HACK|placeholder|not[ _-]?implemented|coming[ _-]?soon|"
    r"fill[ _-]?in|replace[ _-]?me|fake[ _-]?deploy|stub(?:bed)?[ _-]?deploy|no[ _-]?op|dummy[ _-]?deploy)\b")
DISABLED = re.compile(r"(?i)\b(?:if\s*:\s*false|when\s*:\s*never|enabled\s*:\s*false)\b")

def load_list(name):
    """One token per line from .claude/<name> (blank lines + `#` comments ignored). Empty when absent."""
    out = []
    f = ROOT / ".claude" / name
    if f.exists():
        for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
            ln = ln.split("#", 1)[0].strip()
            if ln:
                out.append(ln)
    return out

allow = load_list("deploy-real-allow.txt")
# project-extensible recognition: a deploy tool the built-in DEPLOY_CMD list doesn't know (a niche/in-house
# deployer) is added here as a literal token, so a real deploy that uses it isn't mistaken for an empty one.
EXTRA_CMDS = [t.lower() for t in load_list("deploy-real-commands.txt")]

def has_real_deploy_cmd(text):
    return bool(DEPLOY_CMD.search(text)) or any(tok in text.lower() for tok in EXTRA_CMDS)

def allowed(where, msg):
    return any(a in where or a in msg for a in allow)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    if not allowed(where, msg):
        F.append((sev, where, msg))

def is_deploy_artifact(p, posix, text):
    # named/located as a deploy artifact -> always scanned (its job IS to deploy).
    if DEPLOY_NAME.search(p.name) or DEPLOY_DIR.search(posix):
        if p.suffix in WF_EXT:
            return "ci config"
        if p.suffix in SCRIPT_EXT or p.suffix == "":
            return "script"
    # a Dockerfile -> scanned for placeholders only (it has no deploy command; the no-op WARN doesn't apply).
    if p.name == "Dockerfile" or p.name.startswith("Dockerfile."):
        return "dockerfile"
    # a CI config (any provider) or a Jenkinsfile -> scanned ONLY when its CONTENT shows deploy intent (a deploy/
    # release job/step, or a real deploy command). A test/lint-only config is left alone (no false positives).
    if (CI_FILE.search(posix) or p.name == "Jenkinsfile") and (DEPLOY_NAME.search(text) or has_real_deploy_cmd(text)):
        return "ci config"
    return None

# package.json `scripts` + Makefile `deploy:` targets are handled structurally (a fake reads as an echo-only or
# placeholder script/recipe). Returns the count scanned so an early project with neither still no-ops cleanly.
SCRIPT_KV = re.compile(r'"((?:pre|post)?(?:deploy|release|promote|rollout|publish|ship)[\w:-]*)"\s*:\s*"((?:[^"\\]|\\.)*)"', re.I)
def scan_package_json(rel, text):
    n = 0
    in_scripts = False
    for i, line in enumerate(text.splitlines(), 1):
        if '"scripts"' in line:
            in_scripts = True
        if not in_scripts:
            continue
        m = SCRIPT_KV.search(line)
        if not m:
            if in_scripts and line.strip() == "}":   # crude end-of-scripts
                in_scripts = False
            continue
        n += 1
        key, val = m.group(1), m.group(2)
        if "deploy-real: allow" in line:
            continue
        where = "%s:%d" % (rel, i)
        if PLACEHOLDER.search(val):
            add("ERROR", where, "package.json script '%s' is a placeholder — this deploy does not really deploy." % key)
        elif is_noop_cmd(val):
            add("WARN", where, "package.json script '%s' is echo-only / empty — it deploys nothing." % key)
    return n

MAKE_TARGET = re.compile(r"^([A-Za-z0-9_.-]*(?:deploy|release|promote|rollout|publish|ship)[A-Za-z0-9_.-]*)\s*:(?!=)", re.I)
def scan_makefile(rel, text):
    lines = text.splitlines()
    n = 0
    i = 0
    while i < len(lines):
        m = MAKE_TARGET.match(lines[i])
        if not m:
            i += 1
            continue
        n += 1
        target, start = m.group(1), i
        recipe = []
        i += 1
        while i < len(lines) and (lines[i].startswith("\t") or lines[i].strip() == ""):
            if lines[i].startswith("\t"):
                recipe.append(lines[i].lstrip("\t").lstrip("@-"))
            i += 1
        body = "\n".join(recipe)
        if "deploy-real: allow" in body:
            continue
        where = "%s:%d" % (rel, start + 1)
        if PLACEHOLDER.search(body):
            add("ERROR", where, "Makefile target '%s' is a placeholder — this deploy does not really deploy." % target)
        elif is_noop_cmd(body) or not has_real_deploy_cmd(body):
            add("WARN", where, "Makefile target '%s' invokes no recognized deploy command — an echo-only / empty deploy." % target)
    return n

# discover deploy-intent artifacts; skip vendored / VCS trees.
SKIP = ("/node_modules/", "/.git/", "/vendor/", "/dist/", "/build/", "/.venv/", "/venv/")
artifacts = []
scanned = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    posix = "/" + p.relative_to(ROOT).as_posix()
    if any(s in posix for s in SKIP):
        continue
    rel = p.relative_to(ROOT).as_posix()
    name = p.name
    if name == "package.json":
        scanned += scan_package_json(rel, p.read_text(encoding="utf-8", errors="replace"))
        continue
    if name in ("Makefile", "makefile", "GNUmakefile") or p.suffix == ".mk":
        scanned += scan_makefile(rel, p.read_text(encoding="utf-8", errors="replace"))
        continue
    if p.suffix not in (WF_EXT | SCRIPT_EXT) and p.suffix != "" and name != "Jenkinsfile":
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    kind = is_deploy_artifact(p, posix, text)
    if kind:
        artifacts.append((p, kind, text))

scanned += len(artifacts)
if scanned == 0:
    print("check_deploy_real: no deploy/CI artifact found under %s - nothing to scan." % ROOT)
    sys.exit(0)

for p, kind, text in artifacts:
    rel = p.relative_to(ROOT).as_posix()
    has_real_cmd = has_real_deploy_cmd(text)
    for n, line in enumerate(text.splitlines(), 1):
        if "deploy-real: allow" in line:
            continue
        where = "%s:%d" % (rel, n)
        # a placeholder in a comment is still caught (that's the point); a commented-out real command
        # (`# kubectl apply`) reads as the disabled-deploy / no-real-command case, handled below.
        if PLACEHOLDER.search(line):
            add("ERROR", where, "a placeholder in a deploy artifact — this deploy does not really deploy.")
        if DISABLED.search(line):
            add("WARN", where, "a disabled deploy job/step (deploy turned off) — re-enable it or remove it.")
    if kind != "dockerfile" and not has_real_cmd:    # a Dockerfile has no deploy command - don't no-op-warn it
        add("WARN", "%s:1" % rel,
            "a deploy-intent %s that invokes no recognized deploy/IaC command — an echo-only / empty deploy." % kind)

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-40s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d deploy artifact(s)." % (e, w, scanned))
sys.exit(1 if e else 0)
