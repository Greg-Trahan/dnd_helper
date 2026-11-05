from sqlalchemy import inspect

import app.models
from app.database.base import Base
from app.database.session import engine


inspector = inspect(engine)
metadata = Base.metadata
schema = "public"

db_tables = set(inspector.get_table_names(schema=schema))
db_tables.discard("alembic_version")

model_tables = set(metadata.tables.keys())

issues = []


def type_signature(column_type):
    return column_type.compile(dialect=engine.dialect).upper()


def fk_signature(columns, referred_table, referred_columns, ondelete):
    return (
        tuple(columns),
        referred_table,
        tuple(referred_columns),
        (ondelete or "").upper(),
    )


print("\n=== 1. TABLE COVERAGE ===")
print(f"Database tables: {len(db_tables)}")
print(f"ORM models:      {len(model_tables)}")

for table in sorted(db_tables - model_tables):
    issues.append(f"Missing ORM model: {table}")

for table in sorted(model_tables - db_tables):
    issues.append(f"ORM table missing from database: {table}")


print("\n=== 2. COLUMN AUDIT ===")

for table_name in sorted(db_tables & model_tables):
    db_columns = {
        col["name"]: col
        for col in inspector.get_columns(table_name, schema=schema)
    }

    orm_table = metadata.tables[table_name]
    orm_columns = {col.name: col for col in orm_table.columns}

    for name in sorted(set(db_columns) - set(orm_columns)):
        issues.append(f"{table_name}.{name}: missing from ORM")

    for name in sorted(set(orm_columns) - set(db_columns)):
        issues.append(f"{table_name}.{name}: missing from database")

    for name in sorted(set(db_columns) & set(orm_columns)):
        db_col = db_columns[name]
        orm_col = orm_columns[name]

        db_type = type_signature(db_col["type"])
        orm_type = type_signature(orm_col.type)

        if db_type != orm_type:
            issues.append(
                f"{table_name}.{name}: type mismatch "
                f"(DB={db_type}, ORM={orm_type})"
            )

        if db_col["nullable"] != orm_col.nullable:
            issues.append(
                f"{table_name}.{name}: nullability mismatch "
                f"(DB={db_col['nullable']}, ORM={orm_col.nullable})"
            )


print("\n=== 3. PRIMARY KEY AUDIT ===")

for table_name in sorted(db_tables & model_tables):
    db_pk = inspector.get_pk_constraint(
        table_name, schema=schema
    ).get("constrained_columns") or []

    orm_pk = [
        col.name
        for col in metadata.tables[table_name].primary_key.columns
    ]

    if set(db_pk) != set(orm_pk):
        issues.append(
            f"{table_name}: primary key mismatch "
            f"(DB={db_pk}, ORM={orm_pk})"
        )


print("\n=== 4. FOREIGN KEY AUDIT ===")

for table_name in sorted(db_tables & model_tables):
    db_fks = set()

    for fk in inspector.get_foreign_keys(table_name, schema=schema):
        db_fks.add(
            fk_signature(
                fk["constrained_columns"],
                fk["referred_table"],
                fk["referred_columns"],
                fk.get("options", {}).get("ondelete"),
            )
        )

    orm_fks = set()

    for fk in metadata.tables[table_name].foreign_key_constraints:
        orm_fks.add(
            fk_signature(
                [element.parent.name for element in fk.elements],
                fk.referred_table.name,
                [element.column.name for element in fk.elements],
                fk.ondelete,
            )
        )

    for fk in db_fks - orm_fks:
        issues.append(f"{table_name}: foreign key missing from ORM: {fk}")

    for fk in orm_fks - db_fks:
        issues.append(f"{table_name}: extra ORM foreign key: {fk}")


print("\n=== 5. UNIQUE CONSTRAINT AUDIT ===")

for table_name in sorted(db_tables & model_tables):
    db_uniques = {
        (tuple(uc["column_names"]))
        for uc in inspector.get_unique_constraints(
            table_name, schema=schema
        )
    }

    orm_uniques = {
        tuple(col.name for col in constraint.columns)
        for constraint in metadata.tables[table_name].constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    for unique in db_uniques - orm_uniques:
        issues.append(f"{table_name}: unique constraint missing from ORM: {unique}")

    for unique in orm_uniques - db_uniques:
        issues.append(f"{table_name}: extra ORM unique constraint: {unique}")


print("\n=== 6. INDEX AUDIT ===")

for table_name in sorted(db_tables & model_tables):
    db_indexes = set()

    for index in inspector.get_indexes(table_name, schema=schema):
        if index.get("duplicates_constraint"):
            continue

        db_indexes.add(
            (
                tuple(index["column_names"] or []),
                bool(index["unique"]),
            )
        )

    orm_indexes = {
        (
            tuple(col.name for col in index.columns),
            bool(index.unique),
        )
        for index in metadata.tables[table_name].indexes
    }

    for index in db_indexes - orm_indexes:
        issues.append(f"{table_name}: index missing from ORM: {index}")

    for index in orm_indexes - db_indexes:
        issues.append(f"{table_name}: extra ORM index: {index}")


print("\n=== AUDIT RESULTS ===")

if issues:
    print(f"Found {len(issues)} issue(s):\n")
    for issue in issues:
        print(f" - {issue}")
else:
    print("PASS: No mismatches found in the audited schema details.")

engine.dispose()
