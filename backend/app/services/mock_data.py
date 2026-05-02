"""
Generates realistic mock browsing history for development and testing.
Used automatically when no real browser history is accessible.
"""

import random
from datetime import datetime, timedelta, timezone

MOCK_SITES = [
    # (domain, title_template, category_hint)
    ("github.com", "GitHub · {}", "trabalho"),
    ("stackoverflow.com", "Stack Overflow - {}", "trabalho"),
    ("docs.python.org", "Python Docs - {}", "estudo"),
    ("developer.mozilla.org", "MDN Web Docs - {}", "estudo"),
    ("youtube.com", "YouTube · {}", "entretenimento"),
    ("netflix.com", "Netflix - {}", "entretenimento"),
    ("twitter.com", "Twitter / {}", "redes_sociais"),
    ("instagram.com", "Instagram · {}", "redes_sociais"),
    ("linkedin.com", "LinkedIn - {}", "trabalho"),
    ("notion.so", "Notion - {}", "trabalho"),
    ("figma.com", "Figma - {}", "trabalho"),
    ("reddit.com", "Reddit - {}", "entretenimento"),
    ("udemy.com", "Udemy - {}", "estudo"),
    ("medium.com", "Medium - {}", "estudo"),
    ("twitch.tv", "Twitch - {}", "entretenimento"),
    ("facebook.com", "Facebook - {}", "redes_sociais"),
    ("whatsapp.com", "WhatsApp Web", "redes_sociais"),
    ("google.com", "Google Search", "outros"),
    ("gmail.com", "Gmail - Inbox", "trabalho"),
    ("trello.com", "Trello - {}", "trabalho"),
]

TITLE_NOUNS = [
    "Build faster",
    "Dashboard",
    "Settings",
    "Profile",
    "Feed",
    "Messages",
    "Notifications",
    "Home",
    "Search",
    "Explore",
]


def generate_mock_history(days_back: int = 7, entries_per_day: int = 60) -> list[dict]:
    """Return a list of realistic-looking browsing entries for the last `days_back` days."""
    now = datetime.now(timezone.utc)
    entries: list[dict] = []

    for day_offset in range(days_back):
        day_start = now - timedelta(days=day_offset + 1)
        # More activity during work hours (9–18) and evenings (20–23)
        timestamps = _generate_timestamps(day_start, entries_per_day)

        for ts in timestamps:
            domain, title_tpl, _ = random.choice(MOCK_SITES)
            title = title_tpl.format(random.choice(TITLE_NOUNS))
            url = f"https://{domain}/{random.randint(1000, 9999)}"
            entries.append({
                "url": url,
                "title": title,
                "visited_at": ts,
                "domain": domain,
                "source": "mock",
            })

    entries.sort(key=lambda e: e["visited_at"], reverse=True)
    return entries


def _generate_timestamps(day_start: datetime, count: int) -> list[datetime]:
    """Produce `count` timestamps biased toward work and evening hours."""
    timestamps = []
    for _ in range(count):
        # Pick a bucket: work (60%), evening (25%), other (15%)
        roll = random.random()
        if roll < 0.60:
            hour = random.randint(9, 17)
        elif roll < 0.85:
            hour = random.randint(19, 22)
        else:
            hour = random.randint(0, 23)

        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ts = day_start.replace(hour=hour, minute=minute, second=second, microsecond=0)
        timestamps.append(ts)
    return timestamps
