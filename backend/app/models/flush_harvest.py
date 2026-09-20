from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlushHarvest(Base):
    __tablename__ = "flush_harvests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flush_no: Mapped[int] = mapped_column(Integer, nullable=False)
    # BUG: weight/grade nullable so partial commit survives
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    operator_name: Mapped[str] = mapped_column(String(64), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="flush_harvests")
