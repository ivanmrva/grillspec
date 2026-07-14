#!/usr/bin/env python3
# check_migration_real.py - a coarse, high-precision tripwire against FAKE / EMPTY schema migrations.
#
# Why it exists (the third sibling, after check_no_fakes.py for src/ and check_deploy_real.py for the deploy
# surface): a schema/data change is production too, and the same adherence gap that fakes a deploy fakes a
# migration - a `-- TODO: write the real migration`, an empty Django `operations = []`, a `.sql` file with no
# DDL, a `pass`-only `up()`. The slice's data dimension reports done, the table never changes, and the next
# environment's deploy fails on a column that isn't there. The conformance review already blocks a schema change
# with NO migration; THIS makes "the migration that IS there actually does something" mechanical.
#
# It is deliberately conservative (a noisy gate gets `--no-verify`d): it scans only files under a migration home
# and flags only the clear fakes.
#
# ERROR (a placeholder migration - it doesn't really migrate):
#   - a TODO/FIXME/placeholder/"not implemented"/"fill in"/"replace me"/"fake|stub|dummy" marker in a migration.
# WARN (an empty migration - review; a no-op data migration can be legitimate, hence not a hard block):
#   - a `.sql` migration with no DDL/DML statement; an `operations = []`; a migration with no recognized
#     migration statement whose only body is `pass`/empty.
# Suppress with an inline `migration-real: allow <reason>` comment, or a path/substring entry in
# `.claude/migration-real-allow.txt`. `--strict` promotes WARN -> ERROR.
#
# EXTENSIBLE: a non-standard migration-home path fragment (e.g. `db/changesets/`) added to
# `.claude/migration-real-dirs.txt` (one per line) is recognised as a migration home + scanned.
#
# An empty DOWN / rollback migration is treated as a legitimate no-op (an irreversible change with no rollback) -
# emptiness there is not flagged; a placeholder in it still is.
#
# No-ops cleanly when no migration file exists (an early project). Run from the project root:
#   python3 tools/check_migration_real.py [project_root] [--strict]
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
STRICT = "--strict" in sys.argv

# a file is a MIGRATION when it lives under a migration home and is a sql/code file. We do NOT guess from name
# alone (a `migrate_users.py` service isn't a migration) - the migration HOME is the signal.
MIG_PATH = re.compile(r"(?:^|/)(?:migrations?|migrate)(?:/|$)|alembic/versions/|prisma/migrations/", re.I)
MIG_EXT = {".sql", ".py", ".rb", ".js", ".ts", ".go"}
SKIP = ("/node_modules/", "/.git/", "/vendor/", "/dist/", "/build/", "/.venv/", "/venv/")

# a real DDL/DML statement (sql) - presence means the .sql migration actually changes something.
SQL_STMT = re.compile(
    r"(?i)\b(?:create|alter|drop|truncate|rename)\s+"
    r"(?:table|index|unique|view|schema|sequence|type|database|materialized|trigger|function|extension|constraint|column|role|policy)"
    r"|\b(?:insert\s+into|update\s+\w+\s+set|delete\s+from|grant\s|revoke\s|comment\s+on|add\s+column|add\s+constraint|copy\s+\w)")
# a real ORM/framework migration operation (Django/Rails/Alembic/knex/sequelize/typeorm).
ORM_STMT = re.compile(
    r"(?i)\b(?:create_table|drop_table|add_column|remove_column|change_column|rename_column|add_index|"
    r"add_reference|add_foreign_key|change_table|createTable|dropTable|addColumn|alterTable|removeColumn|"
    r"queryInterface\.\w+|knex\.schema|migrations\.(?:CreateModel|DeleteModel|AddField|RemoveField|AlterField|"
    r"RenameField|RunSQL|RunPython|AddIndex|RemoveIndex|AlterModelTable|AddConstraint)|"
    r"op\.(?:create_table|drop_table|add_column|drop_column|alter_column|create_index|drop_index|execute|bulk_insert|rename_table))\b")
EMPTY_OPS = re.compile(r"(?i)\boperations\s*=\s*\[\s*\]")

PLACEHOLDER = re.compile(
    r"(?i)\b(?:TODO|FIXME|XXX|placeholder|not[ _-]?implemented|coming[ _-]?soon|"
    r"fill[ _-]?in|replace[ _-]?me|fake[ _-]?migration|stub(?:bed)?[ _-]?migration|dummy[ _-]?migration)\b")
COMMENT = re.compile(r"(?m)^\s*(?:--|#|//).*$|/\*.*?\*/", re.S)

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

allow = load_list("migration-real-allow.txt")
# project-extensible recognition: a non-standard migration-home path fragment (e.g. `db/changesets/`) added here
# is still scanned. (Extra *statement* tokens aren't needed: emptiness is judged by `body_is_trivial`, which only
# fires when the file has no real body at all - an unrecognised-but-present operation is already not flagged.)
EXTRA_DIRS = load_list("migration-real-dirs.txt")

def has_real_stmt(text):
    return bool(SQL_STMT.search(text) or ORM_STMT.search(text))

# a DOWN / rollback migration that is intentionally empty (an irreversible change with no rollback) is a
# legitimate no-op, not a fake - recognise it by name so emptiness there isn't flagged (a placeholder still is).
DOWN_MIG = re.compile(r"(?:\.down\.|[._-]down[._-]|[._-]down$|/down/|rollback|revert|undo)", re.I)

def allowed(where, msg):
    return any(a in where or a in msg for a in allow)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    if not allowed(where, msg):
        F.append((sev, where, msg))

def body_is_trivial(text):
    """The migration's real body is empty - strip comments + structural boilerplate, see if anything's left."""
    stripped = COMMENT.sub("", text)
    real = []
    for ln in stripped.splitlines():
        s = ln.strip()
        if not s:
            continue
        # ignore imports + structural scaffolding that carry no migration logic.
        if re.match(r"^(?:from |import |package |require\(|const \w+ = require|use |class |def |module |end$|"
                    r"exports\.|module\.exports|@?\w+ = |\{|\}|\)|\(|\];?|dependencies\s*=|revision\s*=|"
                    r"down_revision\s*=|depends_on\s*=|public |func )", s):
            continue
        if s in ("pass", "return", "return nil", "{", "}", "begin", "commit;", "begin;"):
            continue
        real.append(s)
    return not real

migs = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or p.suffix not in MIG_EXT:
        continue
    posix = "/" + p.relative_to(ROOT).as_posix()
    if any(s in posix for s in SKIP):
        continue
    if not MIG_PATH.search(posix) and not any(d in posix for d in EXTRA_DIRS):
        continue
    migs.append(p)

if not migs:
    print("check_migration_real: no migration file found under %s - nothing to scan." % ROOT)
    sys.exit(0)

for p in migs:
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8", errors="replace")
    has_stmt = has_real_stmt(text)
    placed = False
    for n, line in enumerate(text.splitlines(), 1):
        if "migration-real: allow" in line:
            continue
        if PLACEHOLDER.search(line):
            add("ERROR", "%s:%d" % (rel, n), "a placeholder in a migration — it doesn't really migrate.")
            placed = True
    # an empty DOWN/rollback migration is a legitimate no-op (irreversible-by-design) - don't flag emptiness
    # there; a placeholder (above) is still an ERROR regardless.
    if not has_stmt and not placed and not DOWN_MIG.search(rel):
        if EMPTY_OPS.search(text) or body_is_trivial(text):
            add("WARN", "%s:1" % rel,
                "an empty migration — it defines no schema/data change (no DDL/DML or migration operation).")

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-40s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d migration(s)." % (e, w, len(migs)))
sys.exit(1 if e else 0)
