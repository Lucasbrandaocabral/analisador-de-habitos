"""
Orchestrates data collection: reads browser history (or mock data),
classifies each entry, and persists new records to the database.

Deduplication: an entry is considered duplicate if the same (url, visited_at)
pair already exists in the database.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.history import BrowsingLog
from app.services.browser_reader import read_browser_history
from app.services.mock_data import generate_mock_history
from app.services.classifier import classify_domain, seed_default_categories


def collect_and_store(db: Session, days_back: int = 7, use_mock_fallback: bool = True) -> dict:
    """
    Main collection entry point.

    Returns a summary dict: {inserted, skipped, source}.
    """
    seed_default_categories(db)

    raw_entries = read_browser_history(limit=1000, days_back=days_back)
    source = "browser"

    if not raw_entries and use_mock_fallback:
        raw_entries = generate_mock_history(days_back=days_back)
        source = "mock"

    inserted = 0
    skipped = 0

    for entry in raw_entries:
        # Check for duplicate by exact (url, visited_at) match
        exists = (
            db.query(BrowsingLog)
            .filter(
                BrowsingLog.url == entry["url"],
                BrowsingLog.visited_at == entry["visited_at"],
            )
            .first()
        )
        if exists:
            skipped += 1
            continue

        category = classify_domain(entry["domain"], db)

        log = BrowsingLog(
            url=entry["url"],
            title=entry["title"],
            domain=entry["domain"],
            visited_at=entry["visited_at"],
            category_id=category.id,
            source=entry.get("source", source),
        )
        db.add(log)
        inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped, "source": source}
