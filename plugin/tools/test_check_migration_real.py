#!/usr/bin/env python3
# test_check_migration_real.py - regression tests for check_migration_real.py (the fake/empty-migration tripwire).
#
# Each scenario writes a tiny project, runs the tool, asserts which findings fire (must=) and which do NOT
# (forbid=) - locking the precision so a later edit can't make it noisier or blind. Stdlib only; no network.
# Run:  python3 tools/test_check_migration_real.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_migration_real.py"

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="migtest_"))
    try:
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args], capture_output=True, text=True)
        return out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

PASS = FAIL = 0
def expect(name, output, must=(), forbid=()):
    global PASS, FAIL
    probs = [("missing: " + s) for s in must if s not in output] + \
            [("unexpected: " + s) for s in forbid if s in output]
    if probs:
        FAIL += 1; print("FAIL  " + name)
        for pr in probs: print("        " + pr)
        print("        --- output ---\n" + "\n".join("        " + l for l in output.splitlines()))
    else:
        PASS += 1; print("ok    " + name)

# a real SQL migration (has DDL) is clean
expect("real-sql-clean", run({"migrations/001_users.sql": "CREATE TABLE users (id serial primary key);\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# a real Django migration (has operations) is clean
expect("real-django-clean", run({"app/migrations/0001_initial.py":
        "from django.db import migrations, models\n"
        "class Migration(migrations.Migration):\n"
        "    operations = [migrations.CreateModel(name='User', fields=[])]\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# a placeholder migration is an ERROR
expect("placeholder-sql", run({"migrations/002_orders.sql": "-- TODO: write the real migration\n"}),
       must=["ERROR", "placeholder"])

# an empty SQL migration (no DDL/DML) is a WARN
expect("empty-sql-warn", run({"migrations/003_noop.sql": "-- just a comment, nothing here\n"}),
       must=["WARN", "empty migration"], forbid=["ERROR"])

# an empty Django operations list is a WARN
expect("empty-django-ops", run({"app/migrations/0002_empty.py":
        "from django.db import migrations\n"
        "class Migration(migrations.Migration):\n"
        "    dependencies = [('app', '0001_initial')]\n"
        "    operations = []\n"}),
       must=["WARN", "empty migration"], forbid=["ERROR"])

# a pass-only Rails-ish migration (no recognized op) is a WARN
expect("pass-only-warn", run({"db/migrate/004_change.rb":
        "class Change < ActiveRecord::Migration[7.0]\n  def change\n    # nothing yet\n  end\nend\n"}),
       must=["WARN", "empty migration"], forbid=["ERROR"])

# a real Alembic migration (op.create_table) is clean
expect("real-alembic-clean", run({"alembic/versions/abc_init.py":
        "def upgrade():\n    op.create_table('t')\n\ndef downgrade():\n    op.drop_table('t')\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# --strict promotes the empty-migration WARN to ERROR
expect("empty-strict", run({"migrations/005_noop.sql": "-- nothing\n"}, args=("--strict",)),
       must=["ERROR"])

# a non-migration file under src/ (NOT a migration home) is left alone
expect("non-migration-ignored", run({"src/migrate_users.py": "def migrate_users():\n    pass\n"}),
       must=["nothing to scan"], forbid=["ERROR", "WARN"])

# inline waiver suppresses a placeholder finding
expect("inline-waiver", run({"migrations/006.sql": "-- TODO later  -- migration-real: allow tracked in TICKET-1\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allowlist file suppresses by path substring
expect("allowlist-file", run({"migrations/007.sql": "-- TODO\n", ".claude/migration-real-allow.txt": "migrations/007.sql\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# an empty DOWN/rollback migration is a legitimate no-op — not flagged
expect("empty-down-ok", run({"migrations/008_thing.down.sql": "-- irreversible: no rollback\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])
# but a placeholder in a down migration IS still flagged
expect("placeholder-down-still-errors", run({"migrations/009_thing.down.sql": "-- TODO write rollback\n"}),
       must=["ERROR", "placeholder"])

# a migration with an unrecognized-but-present operation is NOT flagged (it's not empty) — no config needed
expect("unrecognized-op-not-empty", run({"db/migrate/010_x.rb": "class X < Migration\n  def change\n    mycorp_morph :users\n  end\nend\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])
# a non-standard migration home is scanned once added to config
expect("config-extends-dirs", run({"db/changesets/011.sql": "-- TODO\n",
        ".claude/migration-real-dirs.txt": "db/changesets/\n"}),
       must=["ERROR", "placeholder"])

# no migration at all = clean no-op (early project)
expect("no-migration-noop", run({"src/app.py": "print('hi')\n"}),
       must=["nothing to scan"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
