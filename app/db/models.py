from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PieceRecord(Base):
    __tablename__ = "pieces"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    symbolic_json = Column(Text, nullable=False)


class ProjectRecord(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    user_id = Column(String(128), nullable=True)
