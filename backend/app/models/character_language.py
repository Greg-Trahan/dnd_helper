from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

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

    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[int | None] = mapped_column()
