from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Edition(Base):
    __tablename__ = "editions"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="edition",
        passive_deletes=True,
    )

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
