import sys
from pathlib import Path

# Locate the project and backend directories.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

# Make the backend application importable.
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import inspect

import app.models
from app.database.base import Base
from app.database.session import engine


SCHEMA = "public"
inspector = inspect(engine)
metadata = Base.metadata

db_tables = set(inspector.get_table_names(schema=SCHEMA))
db_tables.discard("alembic_version")

orm_tables = set(metadata.tables.keys())

issues = []


def report_issue(message):
    issues.append(message)


def type_signature(column_type):
    return column_type.compile(dialect=engine.dialect).upper()


def foreign_key_signature(columns, referred_table, referred_columns, ondelete):
    return (
        tuple(columns),
        referred_table,
        tuple(referred_columns),
        (ondelete or "").upper(),
    )


# ---------------------------------------------------------
# 1. TABLE COVERAGE
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("1. TABLE COVERAGE")
print("=" * 65)

print(f"Database tables: {len(db_tables)}")
print(f"ORM tables:      {len(orm_tables)}")

for table in sorted(db_tables - orm_tables):
    report_issue(f"Missing ORM model: {table}")

for table in sorted(orm_tables - db_tables):
    report_issue(f"ORM table missing from database: {table}")


# ---------------------------------------------------------
# 2. COLUMN AUDIT
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("2. COLUMN AUDIT")
print("=" * 65)

for table_name in sorted(db_tables & orm_tables):
    db_columns = {
        column["name"]: column
        for column in inspector.get_columns(table_name, schema=SCHEMA)
    }

    orm_table = metadata.tables[table_name]
    orm_columns = {column.name: column for column in orm_table.columns}

    for name in sorted(set(db_columns) - set(orm_columns)):
        report_issue(f"{table_name}.{name}: missing from ORM")

    for name in sorted(set(orm_columns) - set(db_columns)):
        report_issue(f"{table_name}.{name}: missing from database")

    for name in sorted(set(db_columns) & set(orm_columns)):
        db_column = db_columns[name]
        orm_column = orm_columns[name]

        db_type = type_signature(db_column["type"])
        orm_type = type_signature(orm_column.type)

        if db_type != orm_type:
            report_issue(
                f"{table_name}.{name}: type mismatch "
                f"(DB={db_type}, ORM={orm_type})"
            )

        if db_column["nullable"] != orm_column.nullable:
            report_issue(
                f"{table_name}.{name}: nullability mismatch "
                f"(DB={db_column['nullable']}, ORM={orm_column.nullable})"
            )


# ---------------------------------------------------------
# 3. PRIMARY KEY AUDIT
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("3. PRIMARY KEY AUDIT")
print("=" * 65)

for table_name in sorted(db_tables & orm_tables):
    db_pk = inspector.get_pk_constraint(
        table_name, schema=SCHEMA
    ).get("constrained_columns") or []

    orm_pk = [
        column.name
        for column in metadata.tables[table_name].primary_key.columns
    ]

    if db_pk != orm_pk:
        report_issue(
            f"{table_name}: primary key mismatch "
            f"(DB={db_pk}, ORM={orm_pk})"
        )


# ---------------------------------------------------------
# 4. FOREIGN KEY AUDIT
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("4. FOREIGN KEY AUDIT")
print("=" * 65)

for table_name in sorted(db_tables & orm_tables):
    db_fks = set()

    for fk in inspector.get_foreign_keys(table_name, schema=SCHEMA):
        db_fks.add(
            foreign_key_signature(
                fk["constrained_columns"],
                fk["referred_table"],
                fk["referred_columns"],
                fk.get("options", {}).get("ondelete"),
            )
        )

    orm_fks = set()

    for fk in metadata.tables[table_name].foreign_key_constraints:
        orm_fks.add(
            foreign_key_signature(
                [element.parent.name for element in fk.elements],
                fk.referred_table.name,
                [element.column.name for element in fk.elements],
                fk.ondelete,
            )
        )

    for fk in db_fks - orm_fks:
        report_issue(f"{table_name}: foreign key missing from ORM: {fk}")

    for fk in orm_fks - db_fks:
        report_issue(f"{table_name}: extra ORM foreign key: {fk}")


# ---------------------------------------------------------
# 5. UNIQUE CONSTRAINT AUDIT
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("5. UNIQUE CONSTRAINT AUDIT")
print("=" * 65)

for table_name in sorted(db_tables & orm_tables):
    db_uniques = {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints(
            table_name, schema=SCHEMA
        )
    }

    orm_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in metadata.tables[table_name].constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    for unique in db_uniques - orm_uniques:
        report_issue(
            f"{table_name}: unique constraint missing from ORM: {unique}"
        )

    for unique in orm_uniques - db_uniques:
        report_issue(
            f"{table_name}: extra ORM unique constraint: {unique}"
        )


# ---------------------------------------------------------
# 6. INDEX AUDIT
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("6. INDEX AUDIT")
print("=" * 65)

for table_name in sorted(db_tables & orm_tables):
    db_indexes = set()

    for index in inspector.get_indexes(table_name, schema=SCHEMA):
        # Unique constraints are represented separately.
        if index.get("duplicates_constraint"):
            continue

        db_indexes.add(
            (
                index["name"],
                tuple(index["column_names"] or []),
                bool(index["unique"]),
            )
        )

    orm_indexes = {
        (
            index.name,
            tuple(column.name for column in index.columns),
            bool(index.unique),
        )
        for index in metadata.tables[table_name].indexes
    }

    for index in db_indexes - orm_indexes:
        report_issue(f"{table_name}: index missing from ORM: {index}")

    for index in orm_indexes - db_indexes:
        report_issue(f"{table_name}: extra ORM index: {index}")


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("AUDIT RESULTS")
print("=" * 65)

if issues:
    print(f"\nFound {len(issues)} issue(s):\n")

    for issue in issues:
        print(f"  - {issue}")
else:
    print("\nPASS: No mismatches found in the audited schema details.")

engine.dispose()
