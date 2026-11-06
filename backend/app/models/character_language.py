from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CharacterLanguage(Base):
    __tablename__ = "character_languages"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="language_assignments",
    )

    language: Mapped["Language"] = relationship(
        "Language",
        back_populates="character_assignments",
    )

    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[int | None] = mapped_column()
