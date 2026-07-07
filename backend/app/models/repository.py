from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import RepositoryStatus


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    github_url: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    local_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        default=RepositoryStatus.PENDING.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )