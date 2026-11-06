from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterProficiency(Base):
    __tablename__ = "character_proficiencies"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
    )

    proficiency_id: Mapped[int] = mapped_column(
        ForeignKey("proficiencies.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[int | None] = mapped_column()

    expertise: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="proficiency_assignments",
    )

    proficiency: Mapped["Proficiency"] = relationship(
        "Proficiency",
        back_populates="character_assignments",
    )
