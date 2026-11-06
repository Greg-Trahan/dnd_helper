import sys
from pathlib import Path

# Make the backend application importable.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import app.models

from sqlalchemy.orm import configure_mappers
from app.database.base import Base


configure_mappers()

mappers = sorted(
    Base.registry.mappers,
    key=lambda mapper: mapper.class_.__name__,
)

errors = []
warnings = []

print("=" * 65)
print("1. BIDIRECTIONAL RELATIONSHIP AUDIT")
print("=" * 65)

relationship_count = 0

for mapper in mappers:
    model_name = mapper.class_.__name__

    for relationship in mapper.relationships:
        relationship_count += 1

        target_name = relationship.mapper.class_.__name__
        reverse_name = relationship.back_populates

        if reverse_name is None:
            print(
                f"  UNPAIRED: {model_name}.{relationship.key}"
                f" -> {target_name}"
            )
            warnings.append(
                f"{model_name}.{relationship.key} has no back_populates"
            )
            continue

        reverse_relationship = relationship.mapper.relationships.get(
            reverse_name
        )

        if reverse_relationship is None:
            errors.append(
                f"{model_name}.{relationship.key}: "
                f"{target_name}.{reverse_name} does not exist"
            )
            print(f"  FAIL: {model_name}.{relationship.key}")
            continue

        if reverse_relationship.mapper.class_ is not mapper.class_:
            errors.append(
                f"{model_name}.{relationship.key}: "
                f"reverse relationship targets the wrong model"
            )
            print(f"  FAIL: {model_name}.{relationship.key}")
            continue

        if reverse_relationship.back_populates != relationship.key:
            errors.append(
                f"{model_name}.{relationship.key}: "
                f"reverse relationship does not point back"
            )
            print(f"  FAIL: {model_name}.{relationship.key}")
            continue

print(f"\nRelationships inspected: {relationship_count}")

if not errors:
    print("PASS: All declared back_populates relationships are consistent.")


print()
print("=" * 65)
print("2. ORM DELETE CASCADE AUDIT")
print("=" * 65)

delete_cascade_count = 0

for mapper in mappers:
    model_name = mapper.class_.__name__

    for relationship in mapper.relationships:
        cascade = relationship.cascade

        if cascade.delete or cascade.delete_orphan:
            delete_cascade_count += 1

            details = []
            if cascade.delete:
                details.append("delete")
            if cascade.delete_orphan:
                details.append("delete-orphan")

            message = (
                f"{model_name}.{relationship.key} "
                f"-> {relationship.mapper.class_.__name__}: "
                f"{', '.join(details)}"
            )

            print(f"  REVIEW: {message}")

            # Character-owned association records are intentional.
            if model_name != "Character":
                errors.append(
                    "Unexpected ORM delete cascade on "
                    + message
                )

print(f"\nRelationships with ORM delete cascades: {delete_cascade_count}")

if delete_cascade_count == 0:
    print("PASS: No ORM delete cascades found.")
elif not any(
    error.startswith("Unexpected ORM delete cascade")
    for error in errors
):
    print(
        "PASS: Delete cascades are limited to "
        "Character-owned association collections."
    )


print()
print("=" * 65)
print("3. AUDIT SUMMARY")
print("=" * 65)

if warnings:
    print(f"Relationships without back_populates: {len(warnings)}")
    for warning in warnings:
        print(f"  REVIEW: {warning}")
else:
    print("No unpaired relationships.")

if errors:
    print(f"\nFAIL: {len(errors)} issue(s) found:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)

print("\nPASS: No relationship consistency or unexpected delete-cascade errors.")
