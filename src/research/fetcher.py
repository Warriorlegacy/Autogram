"""
Knowledge acquisition module (Layer A).
Ingests RSS feeds and curated seed sources into structured source records.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import feedparser

from src.db.database import db

logger = logging.getLogger(__name__)
SEED_FILE = Path(__file__).parent.parent.parent / "data" / "seed_sources.json"

class SourceFetcher:
    def __init__(self, seed_file: Path = SEED_FILE):
        self.seed_file = seed_file

    def load_seed_records(self) -> list[dict]:
        """Loads curated, verified seed source records."""
        if not self.seed_file.exists():
            return []
        try:
            data = json.loads(self.seed_file.read_text(encoding="utf-8"))
            return data.get("curated_records", [])
        except Exception as e:
            logger.error(f"Failed to load seed sources: {e}")
            return []

    def fetch_rss_feed(self, feed_url: str, publisher_name: str) -> list[dict]:
        """Fetches and parses a single RSS feed safely with error handling."""
        records = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # Take latest 5 items
                published = entry.get("published", datetime.utcnow().isoformat())
                summary = entry.get("summary", entry.get("title", ""))
                # Strip HTML tags simply if present
                clean_summary = summary.replace("<p>", "").replace("</p>", "").strip()[:500]

                record = {
                    "source_id": f"RSS-{abs(hash(entry.link)) % 1000000:06d}",
                    "source_title": entry.get("title", "Untitled"),
                    "publisher": publisher_name,
                    "published_at": published,
                    "url": entry.get("link", ""),
                    "excerpt": clean_summary,
                    "source_type": "rss_feed",
                    "trust_score": 0.88
                }
                records.append(record)
        except Exception as e:
            logger.warning(f"Could not fetch RSS feed {feed_url}: {e}")
        return records

    def acquire_sources(self, live_fetch: bool = False) -> list[dict]:
        """
        Gathers source records from seeds and optional live RSS feeds.
        Persists all gathered sources to database.
        """
        all_sources = self.load_seed_records()

        if live_fetch and self.seed_file.exists():
            try:
                data = json.loads(self.seed_file.read_text(encoding="utf-8"))
                for feed_cfg in data.get("rss_feeds", []):
                    rss_items = self.fetch_rss_feed(feed_cfg["url"], feed_cfg["name"])
                    all_sources.extend(rss_items)
            except Exception as e:
                logger.warning(f"Live RSS fetch skipped: {e}")

        # Persist to database
        for rec in all_sources:
            try:
                db.record_source(rec)
            except Exception as e:
                logger.debug(f"Source record persistence warning: {e}")

        logger.info(f"Acquired {len(all_sources)} source records.")
        return all_sources

fetcher = SourceFetcher()
