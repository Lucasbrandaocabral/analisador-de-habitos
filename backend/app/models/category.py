from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # productivity_weight: positive = productive, negative = distraction, 0 = neutral
    productivity_weight = Column(Float, default=0.0)
    color = Column(String, default="#6B7280")
    is_default = Column(Boolean, default=False)

    logs = relationship("BrowsingLog", back_populates="category")
    keywords = relationship("CategoryKeyword", back_populates="category", cascade="all, delete-orphan")


class CategoryKeyword(Base):
    __tablename__ = "category_keywords"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    keyword = Column(String, nullable=False)

    category = relationship("Category", back_populates="keywords")
