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

import urllib.request
import re

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
            for entry in feed.entries[:8]:  # Take latest 8 items
                published = entry.get("published", datetime.utcnow().isoformat())
                summary = entry.get("summary", entry.get("title", ""))
                # Strip HTML tags
                clean_summary = re.sub(r'<[^>]+>', '', summary).strip()[:500]

                record = {
                    "source_id": f"RSS-{abs(hash(entry.link)) % 1000000:06d}",
                    "source_title": entry.get("title", "Untitled"),
                    "publisher": publisher_name,
                    "published_at": published,
                    "url": entry.get("link", ""),
                    "excerpt": clean_summary,
                    "source_type": "rss_feed",
                    "trust_score": 0.90
                }
                records.append(record)
        except Exception as e:
            logger.warning(f"Could not fetch RSS feed {feed_url}: {e}")
        return records

    def fetch_trending_niche_signals(self) -> list[dict]:
        """
        Queries real-time developer and AI trending discussions from Hacker News Algolia API.
        Captures explosive signals in: AI Automation, Agentic Workflows, Developer Tools,
        and Content Distribution.
        """
        trending_records = []
        queries = [
            ("AI agent OR LLM OR workflow", "AI Tool Breakdown"),
            ("Claude OR Cursor OR autonomous coding", "Prompting & Workflow"),
            ("content engine OR solopreneur automation", "Marketing Psychology"),
            ("DeepSeek OR open weights OR local LLM", "Tech Industry Explainer")
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Autogram/2.5"
        }

        for q, pillar in queries:
            try:
                enc_query = urllib.parse.quote(q)
                url = f"https://hn.algolia.com/api/v1/search?query={enc_query}&tags=story&hitsPerPage=5"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=4) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                    hits = payload.get("hits", [])
                    for hit in hits:
                        title = hit.get("title")
                        link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                        points = hit.get("points") or 1

                        if not title:
                            continue

                        # Clean title of common prefixes if present
                        clean_title = re.sub(r'^(Show HN:\s*|Ask HN:\s*|Tell HN:\s*)', '', title).strip()

                        # Trust score scaled with social validation points
                        trust = min(0.96, 0.86 + (points / 500) * 0.1)

                        rec = {
                            "source_id": f"HN-{hit.get('objectID')}",
                            "source_title": clean_title,
                            "publisher": "Hacker News Developer Trends",
                            "pillar": pillar,
                            "published_at": hit.get("created_at", datetime.utcnow().isoformat()),
                            "url": link,
                            "excerpt": f"Trending community signal with {points} points and {hit.get('num_comments', 0)} comments: {clean_title}",
                            "source_type": "trending_community_signal",
                            "trust_score": round(trust, 2)
                        }
                        trending_records.append(rec)
            except Exception as e:
                logger.debug(f"Live trend query '{q}' skipped: {e}")

        logger.info(f"Discovered {len(trending_records)} real-time trending niche signals.")
        return trending_records

    def acquire_sources(self, live_fetch: bool = True) -> list[dict]:
        """
        Gathers source records from curated seed records, live RSS feeds,
        and real-time niche trend APIs. Persists all records to database.
        """
        all_sources = self.load_seed_records()
        seen_titles = {s.get("source_title", "").lower() for s in all_sources}

        if live_fetch:
            # 1. Fetch real-time trending niche discussions
            try:
                live_trends = self.fetch_trending_niche_signals()
                for t in live_trends:
                    if t.get("source_title", "").lower() not in seen_titles:
                        all_sources.append(t)
                        seen_titles.add(t.get("source_title", "").lower())
            except Exception as e:
                logger.warning(f"Live trend search warning: {e}")

            # 2. Ingest live RSS feeds
            if self.seed_file.exists():
                try:
                    data = json.loads(self.seed_file.read_text(encoding="utf-8"))
                    for feed_cfg in data.get("rss_feeds", []):
                        rss_items = self.fetch_rss_feed(feed_cfg["url"], feed_cfg["name"])
                        for r in rss_items:
                            if r.get("source_title", "").lower() not in seen_titles:
                                all_sources.append(r)
                                seen_titles.add(r.get("source_title", "").lower())
                except Exception as e:
                    logger.warning(f"Live RSS fetch skipped: {e}")

        # Persist to database
        for rec in all_sources:
            try:
                db.record_source(rec)
            except Exception as e:
                logger.debug(f"Source record persistence warning: {e}")

        logger.info(f"Acquired total {len(all_sources)} source records (live_fetch={live_fetch}).")
        return all_sources

fetcher = SourceFetcher()
