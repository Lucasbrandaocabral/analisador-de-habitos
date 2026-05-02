from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.category import Category, CategoryKeyword

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryUpdate(BaseModel):
    productivity_weight: Optional[float] = None
    color: Optional[str] = None


class KeywordAdd(BaseModel):
    keyword: str


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "productivity_weight": cat.productivity_weight,
            "color": cat.color,
            "keywords": [kw.keyword for kw in cat.keywords],
        }
        for cat in categories
    ]


@router.patch("/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Edit productivity weight or color of an existing category."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if payload.productivity_weight is not None:
        cat.productivity_weight = payload.productivity_weight
    if payload.color is not None:
        cat.color = payload.color

    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "productivity_weight": cat.productivity_weight}


@router.post("/{category_id}/keywords")
def add_keyword(
    category_id: int,
    payload: KeywordAdd,
    db: Session = Depends(get_db),
):
    """Add a keyword to a category for domain classification."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    kw = CategoryKeyword(category_id=category_id, keyword=payload.keyword.lower().strip())
    db.add(kw)
    db.commit()
    return {"added": kw.keyword, "category": cat.name}


@router.delete("/{category_id}/keywords/{keyword}")
def remove_keyword(
    category_id: int,
    keyword: str,
    db: Session = Depends(get_db),
):
    kw = (
        db.query(CategoryKeyword)
        .filter(CategoryKeyword.category_id == category_id, CategoryKeyword.keyword == keyword)
        .first()
    )
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword não encontrada")
    db.delete(kw)
    db.commit()
    return {"removed": keyword}
