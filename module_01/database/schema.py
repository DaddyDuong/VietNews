"""
Database schema definitions
"""

CREATE_NEWS_TABLE = """
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    rss TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    date TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_LINK_INDEX = """
CREATE INDEX IF NOT EXISTS idx_link ON news_articles(link);
"""

CREATE_DATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_date ON news_articles(date);
"""

CREATE_RSS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_rss ON news_articles(rss);
"""

ALL_SCHEMA_COMMANDS = [
    CREATE_NEWS_TABLE,
    CREATE_LINK_INDEX,
    CREATE_DATE_INDEX,
    CREATE_RSS_INDEX
]
