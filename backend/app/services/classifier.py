"""
Classifies a domain into a category by matching against keyword rules
stored in the database. Falls back to "outros" if no match is found.
"""

from sqlalchemy.orm import Session
from app.models.category import Category, CategoryKeyword

# Built-in seed categories with keywords and productivity weights.
# Loaded into the DB on first run via seed_default_categories().
DEFAULT_CATEGORIES: list[dict] = [
    {
        "name": "trabalho",
        "productivity_weight": 2.0,
        "color": "#3B82F6",
        "keywords": [
            "github.com", "gitlab.com", "bitbucket.org",
            "notion.so", "trello.com", "asana.com", "jira",
            "slack.com", "zoom.us", "meet.google.com",
            "figma.com", "linear.app", "confluence",
            "gmail.com", "outlook.com", "office.com",
            "linkedin.com", "docs.google.com", "sheets.google.com",
        ],
    },
    {
        "name": "estudo",
        "productivity_weight": 1.5,
        "color": "#10B981",
        "keywords": [
            "stackoverflow.com", "docs.python.org", "developer.mozilla.org",
            "udemy.com", "coursera.org", "alura.com.br", "medium.com",
            "dev.to", "wikipedia.org", "freecodecamp.org",
            "w3schools.com", "roadmap.sh", "npmjs.com", "pypi.org",
        ],
    },
    {
        "name": "redes_sociais",
        "productivity_weight": -1.5,
        "color": "#F59E0B",
        "keywords": [
            "twitter.com", "x.com", "instagram.com", "facebook.com",
            "tiktok.com", "snapchat.com", "pinterest.com",
            "whatsapp.com", "telegram.org", "discord.com",
            "threads.net", "reddit.com",
        ],
    },
    {
        "name": "entretenimento",
        "productivity_weight": -0.5,
        "color": "#EF4444",
        "keywords": [
            "youtube.com", "netflix.com", "twitch.tv", "hulu.com",
            "primevideo.com", "disneyplus.com", "hbomax.com",
            "globoplay.globo.com", "crunchyroll.com", "spotify.com",
            "deezer.com", "soundcloud.com",
        ],
    },
    {
        "name": "noticias",
        "productivity_weight": 0.0,
        "color": "#8B5CF6",
        "keywords": [
            "g1.globo.com", "uol.com.br", "r7.com", "bbc.com",
            "cnn.com", "folha.uol.com.br", "estadao.com.br",
            "reuters.com", "theguardian.com", "techcrunch.com",
        ],
    },
    {
        "name": "outros",
        "productivity_weight": 0.0,
        "color": "#6B7280",
        "keywords": [],
    },
]


def seed_default_categories(db: Session) -> None:
    """Insert default categories if the table is empty."""
    if db.query(Category).count() > 0:
        return

    for cat_data in DEFAULT_CATEGORIES:
        category = Category(
            name=cat_data["name"],
            productivity_weight=cat_data["productivity_weight"],
            color=cat_data["color"],
            is_default=True,
        )
        db.add(category)
        db.flush()  # get category.id before adding keywords

        for kw in cat_data["keywords"]:
            db.add(CategoryKeyword(category_id=category.id, keyword=kw))

    db.commit()


def classify_domain(domain: str, db: Session) -> Category:
    """
    Return the Category that best matches `domain`.
    Matches by checking whether any stored keyword is a substring of the domain
    or the domain is a substring of the keyword (handles subdomains).
    """
    keywords = (
        db.query(CategoryKeyword)
        .join(Category)
        .all()
    )

    for kw_obj in keywords:
        kw = kw_obj.keyword.lower()
        if kw in domain or domain in kw:
            return kw_obj.category

    # Default to "outros"
    outros = db.query(Category).filter(Category.name == "outros").first()
    if not outros:
        outros = Category(name="outros", productivity_weight=0.0, color="#6B7280", is_default=True)
        db.add(outros)
        db.commit()
        db.refresh(outros)
    return outros
