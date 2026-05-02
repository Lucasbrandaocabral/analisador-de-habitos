from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database.connection import get_db
from app.models.history import BrowsingLog
from app.services.collector import collect_and_store

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("")
def get_logs(
    days_back: int = Query(7, ge=1, le=90, description="Número de dias para buscar"),
    domain: Optional[str] = Query(None, description="Filtrar por domínio"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    query = db.query(BrowsingLog).filter(BrowsingLog.visited_at >= cutoff)

    if domain:
        query = query.filter(BrowsingLog.domain.ilike(f"%{domain}%"))
    if category:
        from app.models.category import Category
        query = query.join(Category).filter(Category.name == category)

    logs = query.order_by(BrowsingLog.visited_at.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "url": log.url,
            "title": log.title,
            "domain": log.domain,
            "visited_at": log.visited_at.isoformat(),
            "category": log.category.name if log.category else "outros",
            "source": log.source,
        }
        for log in logs
    ]


@router.post("/collect")
def trigger_collection(
    days_back: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Manually trigger a history collection cycle."""
    result = collect_and_store(db, days_back=days_back)
    return result
