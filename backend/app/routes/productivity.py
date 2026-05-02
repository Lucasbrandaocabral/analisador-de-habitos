from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.analytics import get_productivity_score

router = APIRouter(prefix="/productivity", tags=["productivity"])


@router.get("")
def productivity(
    days_back: int = Query(7, ge=1, le=90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
):
    """
    Returns a productivity score (0–100) with label, message, and per-category breakdown.

    Score logic:
    - trabalho/estudo → contribuição positiva
    - redes sociais   → contribuição negativa
    - entretenimento  → contribuição levemente negativa
    - noticias/outros → neutro
    - baseline 50 para sessões completamente neutras
    """
    return get_productivity_score(db, days_back=days_back)
