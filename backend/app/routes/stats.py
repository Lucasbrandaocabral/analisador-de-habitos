from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.analytics import get_stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def stats(
    days_back: int = Query(7, ge=1, le=90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
):
    """
    Returns:
    - total de acessos no período
    - top 10 sites por número de visitas
    - tempo estimado por categoria (em minutos)
    - contagem de acessos por categoria
    """
    return get_stats(db, days_back=days_back)
