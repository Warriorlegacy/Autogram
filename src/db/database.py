"""
Database layer for Autogram engine.
Supports local SQLite (default) and PostgreSQL with schema initialization.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from src.config import settings

DB_FILE = Path(__file__).parent.parent.parent / "autopilot.db"

class Database:
    def __init__(self, db_path: Path | str = DB_FILE):
        self.db_path = str(db_path)
        self.init_schema()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        """Initializes tables matching Section 13 of the Autopilot blueprint."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. brand_config
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brand_config (
                id TEXT PRIMARY KEY,
                brand_name TEXT NOT NULL,
                positioning TEXT,
                audience TEXT,
                voice_rules TEXT,
                banned_phrases TEXT,
                preferred_ctas TEXT,
                design_version TEXT,
                posting_timezone TEXT,
                posting_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 2. source_records
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_records (
                id TEXT PRIMARY KEY,
                source_url TEXT,
                title TEXT,
                publisher TEXT,
                published_at TIMESTAMP,
                source_type TEXT,
                content_hash TEXT UNIQUE,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trust_score REAL,
                raw_excerpt TEXT
            )
            """)

            # 3. content_items
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id TEXT PRIMARY KEY,
                publication_date TEXT,
                topic TEXT,
                pillar TEXT,
                angle TEXT,
                hook TEXT,
                content_json TEXT,
                caption TEXT,
                status TEXT DEFAULT 'IDEA',
                prompt_version TEXT,
                design_version TEXT,
                source_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                instagram_media_id TEXT
            )
            """)

            # 4. post_metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                instagram_media_id TEXT,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reach INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                profile_visits INTEGER DEFAULT 0,
                follows INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                FOREIGN KEY (content_id) REFERENCES content_items(id)
            )
            """)

            # 5. experiments
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                content_id TEXT,
                variable TEXT,
                variant TEXT,
                hypothesis TEXT,
                result TEXT,
                winner BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # 6. auto_dm_log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_dm_log (
                comment_id TEXT PRIMARY KEY,
                media_id TEXT,
                username TEXT,
                comment_text TEXT,
                keyword TEXT,
                public_reply_id TEXT,
                dm_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()

    def record_source(self, record: dict):
        """Save an ingested source record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO source_records (
                id, source_url, title, publisher, published_at, source_type,
                content_hash, trust_score, raw_excerpt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("source_id"),
                record.get("url"),
                record.get("source_title"),
                record.get("publisher"),
                record.get("published_at"),
                record.get("source_type"),
                record.get("url"),  # use url as unique content hash
                record.get("trust_score", 0.9),
                record.get("excerpt")
            ))
            conn.commit()

    def save_content_item(self, item: dict, status: str = "DRAFTING"):
        """Save or update a generated content item."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO content_items (
                id, publication_date, topic, pillar, angle, hook,
                content_json, caption, status, source_ids
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                content_json = excluded.content_json,
                caption = excluded.caption
            """, (
                item.get("content_id"),
                item.get("publication_date"),
                item.get("topic"),
                item.get("pillar"),
                item.get("angle"),
                item.get("hook"),
                json.dumps(item),
                item.get("caption"),
                status,
                json.dumps(item.get("source_ids", []))
            ))
            conn.commit()

    def update_publication_status(self, content_id: str, media_id: str, status: str = "PUBLISHED"):
        """Mark item published with Instagram media ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE content_items 
            SET status = ?, published_at = CURRENT_TIMESTAMP, instagram_media_id = ?
            WHERE id = ?
            """, (status, media_id, content_id))
            conn.commit()

    def get_recent_topics(self, limit: int = 30) -> list[dict]:
        """Fetch recent published topics to prevent repetition."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, topic, pillar, hook, publication_date, status 
            FROM content_items 
            ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

db = Database()
