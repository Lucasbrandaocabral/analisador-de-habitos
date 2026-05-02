"""
Unit tests for service-layer logic (classifier, mock data, analytics).
"""

import pytest
from datetime import datetime, timezone
from app.services.classifier import classify_domain, seed_default_categories
from app.services.mock_data import generate_mock_history
from app.services.analytics import get_stats, get_productivity_score
from app.services.browser_reader import _extract_domain, _chromium_ts_to_datetime
from app.models.history import BrowsingLog
from app.models.category import Category


class TestClassifier:
    def test_known_domain_classified_correctly(self, db):
        cat = classify_domain("github.com", db)
        assert cat.name == "trabalho"

    def test_social_domain(self, db):
        cat = classify_domain("instagram.com", db)
        assert cat.name == "redes_sociais"

    def test_study_domain(self, db):
        cat = classify_domain("stackoverflow.com", db)
        assert cat.name == "estudo"

    def test_unknown_domain_falls_back_to_outros(self, db):
        cat = classify_domain("someobscuredomain.xyz", db)
        assert cat.name == "outros"

    def test_subdomain_classified(self, db):
        # docs.github.com should still match github.com keyword
        cat = classify_domain("docs.github.com", db)
        assert cat.name == "trabalho"

    def test_seed_idempotent(self, db):
        count_before = db.query(Category).count()
        seed_default_categories(db)  # second call — should do nothing
        count_after = db.query(Category).count()
        assert count_before == count_after


class TestMockData:
    def test_generates_entries(self):
        entries = generate_mock_history(days_back=3, entries_per_day=10)
        assert len(entries) == 30

    def test_entry_structure(self):
        entries = generate_mock_history(days_back=1, entries_per_day=5)
        for e in entries:
            assert "url" in e
            assert "title" in e
            assert "visited_at" in e
            assert "domain" in e
            assert e["source"] == "mock"
            assert isinstance(e["visited_at"], datetime)

    def test_entries_sorted_descending(self):
        entries = generate_mock_history(days_back=3, entries_per_day=20)
        timestamps = [e["visited_at"] for e in entries]
        assert timestamps == sorted(timestamps, reverse=True)


class TestAnalytics:
    def _add_logs(self, db, category_name: str, count: int):
        cat = db.query(Category).filter(Category.name == category_name).first()
        for i in range(count):
            db.add(BrowsingLog(
                url=f"https://example.com/{i}",
                title=f"Page {i}",
                domain="example.com",
                visited_at=datetime.now(timezone.utc),
                category_id=cat.id,
                source="mock",
            ))
        db.commit()

    def test_stats_counts(self, db):
        self._add_logs(db, "trabalho", 15)
        stats = get_stats(db, days_back=1)
        assert stats["total_accesses"] >= 15

    def test_time_by_category_positive(self, db):
        self._add_logs(db, "estudo", 10)
        stats = get_stats(db, days_back=1)
        assert "estudo" in stats["time_by_category_minutes"]
        assert stats["time_by_category_minutes"]["estudo"] > 0

    def test_productivity_all_work(self, db):
        self._add_logs(db, "trabalho", 20)
        result = get_productivity_score(db, days_back=1)
        assert result["score"] >= 50  # productive work → above neutral

    def test_productivity_all_social(self, db):
        self._add_logs(db, "redes_sociais", 20)
        result = get_productivity_score(db, days_back=1)
        assert result["score"] < 50  # social media → below neutral


class TestBrowserReader:
    def test_extract_domain_basic(self):
        assert _extract_domain("https://www.github.com/user/repo") == "github.com"

    def test_extract_domain_strips_port(self):
        assert _extract_domain("http://localhost:8000/api") == "localhost"

    def test_extract_domain_invalid(self):
        assert _extract_domain("not-a-url") is None or _extract_domain("not-a-url") == "not-a-url"

    def test_chromium_ts_conversion(self):
        # Chrome epoch + 0 microseconds = 1601-01-01 UTC
        dt = _chromium_ts_to_datetime(0)
        assert dt.year == 1601

    def test_chromium_ts_recent(self):
        # A realistic 2024 timestamp (microseconds since 1601-01-01)
        # 2024-01-01 00:00:00 UTC ≈ 13305600000000000 µs
        ts_2024 = 13305600000000000
        dt = _chromium_ts_to_datetime(ts_2024)
        assert dt.year >= 2024
