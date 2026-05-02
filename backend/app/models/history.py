from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class BrowsingLog(Base):
    __tablename__ = "browsing_logs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    domain = Column(String, nullable=False, index=True)
    visited_at = Column(DateTime, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    source = Column(String, default="browser")  # "browser" | "mock"

    category = relationship("Category", back_populates="logs")

    # SQLite doesn't enforce UNIQUE on DateTime easily, so deduplication
    # is handled at the service layer using (url, visited_at) as the key.
