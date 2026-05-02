"""
Integration tests for all API endpoints.
No real browser history required — mock data is used automatically.
"""

import pytest
from datetime import datetime, timezone
from app.models.history import BrowsingLog
from app.models.category import Category


def _seed_logs(db, count: int = 20):
    """Insert synthetic logs into the test DB."""
    cat_work = db.query(Category).filter(Category.name == "trabalho").first()
    cat_social = db.query(Category).filter(Category.name == "redes_sociais").first()

    for i in range(count):
        cat = cat_work if i % 3 != 0 else cat_social
        log = BrowsingLog(
            url=f"https://github.com/page/{i}",
            title=f"Page {i}",
            domain="github.com" if i % 3 != 0 else "twitter.com",
            visited_at=datetime.now(timezone.utc),
            category_id=cat.id,
            source="mock",
        )
        db.add(log)
    db.commit()


class TestHealth:
    def test_root(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200


class TestLogs:
    def test_empty_logs(self, client):
        res = client.get("/logs")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_collect_trigger(self, client):
        res = client.post("/logs/collect")
        assert res.status_code == 200
        data = res.json()
        assert "inserted" in data
        assert "skipped" in data
        assert "source" in data

    def test_logs_after_collection(self, client, db):
        _seed_logs(db)
        res = client.get("/logs?limit=50")
        assert res.status_code == 200
        logs = res.json()
        assert len(logs) > 0
        first = logs[0]
        assert "url" in first
        assert "domain" in first
        assert "category" in first
        assert "visited_at" in first

    def test_logs_domain_filter(self, client, db):
        _seed_logs(db)
        res = client.get("/logs?domain=github.com")
        assert res.status_code == 200
        for log in res.json():
            assert "github" in log["domain"]

    def test_logs_category_filter(self, client, db):
        _seed_logs(db)
        res = client.get("/logs?category=trabalho")
        assert res.status_code == 200
        for log in res.json():
            assert log["category"] == "trabalho"


class TestStats:
    def test_stats_empty(self, client):
        res = client.get("/stats")
        assert res.status_code == 200
        data = res.json()
        assert "total_accesses" in data
        assert "top_sites" in data

    def test_stats_with_data(self, client, db):
        _seed_logs(db, count=30)
        res = client.get("/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["total_accesses"] > 0
        assert len(data["top_sites"]) > 0
        assert "time_by_category_minutes" in data
        # Top sites should be sorted descending
        visits = [s["visits"] for s in data["top_sites"]]
        assert visits == sorted(visits, reverse=True)


class TestProductivity:
    def test_productivity_no_data(self, client):
        res = client.get("/productivity")
        assert res.status_code == 200
        data = res.json()
        assert "score" in data
        assert 0 <= data["score"] <= 100

    def test_productivity_with_data(self, client, db):
        _seed_logs(db, count=30)
        res = client.get("/productivity")
        assert res.status_code == 200
        data = res.json()
        assert 0 <= data["score"] <= 100
        assert data["label"] != ""
        assert "breakdown" in data

    def test_productivity_score_range(self, client, db):
        # Flood with productive sites → score should be above neutral
        cat = db.query(Category).filter(Category.name == "trabalho").first()
        for i in range(50):
            db.add(BrowsingLog(
                url=f"https://github.com/{i}",
                title=f"Work {i}",
                domain="github.com",
                visited_at=datetime.now(timezone.utc),
                category_id=cat.id,
                source="mock",
            ))
        db.commit()
        res = client.get("/productivity")
        data = res.json()
        assert data["score"] >= 50


class TestCategories:
    def test_list_categories(self, client):
        res = client.get("/categories")
        assert res.status_code == 200
        cats = res.json()
        assert len(cats) > 0
        names = [c["name"] for c in cats]
        assert "trabalho" in names
        assert "redes_sociais" in names

    def test_update_category_weight(self, client, db):
        cat = db.query(Category).filter(Category.name == "entretenimento").first()
        res = client.patch(f"/categories/{cat.id}", json={"productivity_weight": -2.0})
        assert res.status_code == 200
        assert res.json()["productivity_weight"] == -2.0

    def test_add_and_remove_keyword(self, client, db):
        cat = db.query(Category).filter(Category.name == "trabalho").first()

        res = client.post(f"/categories/{cat.id}/keywords", json={"keyword": "newsite.com"})
        assert res.status_code == 200
        assert res.json()["added"] == "newsite.com"

        res = client.delete(f"/categories/{cat.id}/keywords/newsite.com")
        assert res.status_code == 200

    def test_update_nonexistent_category(self, client):
        res = client.patch("/categories/99999", json={"productivity_weight": 1.0})
        assert res.status_code == 404
