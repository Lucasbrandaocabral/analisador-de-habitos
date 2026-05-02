"""
Computes statistics and the productivity score from stored browsing logs.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.history import BrowsingLog
from app.models.category import Category

# Assumed average dwell time per page visit (seconds).
# Without actual tab-close events we estimate based on category.
DWELL_ESTIMATE: dict[str, int] = {
    "trabalho": 180,
    "estudo": 240,
    "redes_sociais": 90,
    "entretenimento": 300,
    "noticias": 120,
    "outros": 60,
}
DEFAULT_DWELL = 90


def get_stats(db: Session, days_back: int = 7) -> dict:
    """Return aggregated stats for the last `days_back` days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    logs = (
        db.query(BrowsingLog)
        .filter(BrowsingLog.visited_at >= cutoff)
        .all()
    )

    total_accesses = len(logs)
    if total_accesses == 0:
        return {
            "total_accesses": 0,
            "top_sites": [],
            "time_by_category": {},
            "accesses_by_category": {},
            "days_analyzed": days_back,
        }

    # Top 10 domains by visit count
    domain_counter: Counter = Counter(log.domain for log in logs)
    top_sites = [
        {"domain": domain, "visits": count}
        for domain, count in domain_counter.most_common(10)
    ]

    # Time and access count per category
    time_by_category: dict[str, float] = defaultdict(float)
    accesses_by_category: dict[str, int] = defaultdict(int)

    for log in logs:
        cat_name = log.category.name if log.category else "outros"
        dwell = DWELL_ESTIMATE.get(cat_name, DEFAULT_DWELL)
        time_by_category[cat_name] += dwell
        accesses_by_category[cat_name] += 1

    # Convert seconds to minutes
    time_by_category_minutes = {
        cat: round(secs / 60, 1) for cat, secs in time_by_category.items()
    }

    return {
        "total_accesses": total_accesses,
        "top_sites": top_sites,
        "time_by_category_minutes": time_by_category_minutes,
        "accesses_by_category": dict(accesses_by_category),
        "days_analyzed": days_back,
    }


def get_productivity_score(db: Session, days_back: int = 7) -> dict:
    """
    Calculate a productivity score from 0 to 100.

    Algorithm:
    - Each log contributes its category's productivity_weight × dwell_estimate.
    - Raw score is normalized against the theoretical maximum (all time in
      "trabalho") and scaled to 0–100.
    - A baseline of 50 is added so a neutral day (all "outros") lands at 50.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    logs = (
        db.query(BrowsingLog)
        .filter(BrowsingLog.visited_at >= cutoff)
        .all()
    )

    if not logs:
        return {
            "score": 50,
            "label": "Sem dados",
            "breakdown": {},
            "message": "Nenhum dado coletado para o período.",
        }

    max_weight = 2.0  # trabalho weight — used for normalization

    raw_score = 0.0
    max_possible = 0.0
    breakdown: dict[str, dict] = {}

    for log in logs:
        cat_name = log.category.name if log.category else "outros"
        weight = log.category.productivity_weight if log.category else 0.0
        dwell = DWELL_ESTIMATE.get(cat_name, DEFAULT_DWELL)

        contribution = weight * dwell
        raw_score += contribution
        max_possible += max_weight * dwell

        if cat_name not in breakdown:
            breakdown[cat_name] = {"visits": 0, "contribution": 0.0}
        breakdown[cat_name]["visits"] += 1
        breakdown[cat_name]["contribution"] += round(contribution, 2)

    # Normalize: shift so that a neutral session (all weight=0) gives 50
    if max_possible > 0:
        normalized = (raw_score / max_possible) * 50 + 50
    else:
        normalized = 50.0

    score = max(0, min(100, round(normalized)))

    label = _score_label(score)

    return {
        "score": score,
        "label": label,
        "breakdown": breakdown,
        "message": _score_message(score),
    }


def _score_label(score: int) -> str:
    if score >= 80:
        return "Muito Produtivo"
    if score >= 65:
        return "Produtivo"
    if score >= 45:
        return "Neutro"
    if score >= 30:
        return "Distraído"
    return "Muito Distraído"


def _score_message(score: int) -> str:
    messages = {
        (80, 101): "Excelente! Você está aproveitando bem seu tempo online.",
        (65, 80): "Bom trabalho. Leve equilíbrio entre foco e lazer.",
        (45, 65): "Dia equilibrado, mas há espaço para melhorar o foco.",
        (30, 45): "Atenção: redes sociais e entretenimento estão consumindo muito tempo.",
        (0, 30): "Alto índice de distração. Considere usar um bloqueador de sites.",
    }
    for (low, high), msg in messages.items():
        if low <= score < high:
            return msg
    return ""
