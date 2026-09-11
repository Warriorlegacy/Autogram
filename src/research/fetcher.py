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
        Queries real-time developer and FOSS trending discussions from Hacker News Algolia API.
        Captures explosive signals across all 6 FOSS and developer productivity pillars.
        """
        trending_records = []
        queries = [
            ("open source OR self-hosted OR alternative to", "FOSS SaaS Alternatives"),
            ("Show HN OR github repo OR new release", "Trending GitHub Spotlight"),
            ("Ollama OR local LLM OR DeepSeek OR vLLM", "Local AI & Edge Compute"),
            ("CLI tool OR terminal OR developer tool OR rust", "Developer Power Tools & CLI"),
            ("docker-compose OR homelab OR reverse proxy OR caddy", "Self-Hosted Architecture"),
            ("open source license OR AGPL OR MIT OR BSL", "Open Source Economics & Contrarian")
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Autogram/2.5"
        }

        for q, pillar in queries:
            try:
                enc_query = urllib.parse.quote(q)
                url = f"https://hn.algolia.com/api/v1/search?query={enc_query}&tags=story&hitsPerPage=4"
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
                            "publisher": "Hacker News FOSS Trends",
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

        logger.info(f"Discovered {len(trending_records)} real-time trending FOSS signals.")
        return trending_records

    def fetch_github_trending(self) -> list[dict]:
        """
        Discovers trending open source repositories from GitHub API.
        Captures newly starred FOSS tools, developer utilities, and local AI engines.
        """
        records = []
        try:
            url = "https://api.github.com/search/repositories?q=stars:>500+is:public+archived:false&sort=updated&order=desc&per_page=6"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Autogram/2.5",
                "Accept": "application/vnd.github+json"
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for repo in data.get("items", []):
                    name = repo.get("full_name", "")
                    desc = repo.get("description") or "High-leverage open source tool"
                    stars = repo.get("stargazers_count", 0)
                    lang = repo.get("language") or "Code"
                    topics = repo.get("topics", [])
                    license_name = (repo.get("license") or {}).get("spdx_id", "FOSS")

                    pillar = "Trending GitHub Spotlight"
                    desc_lower = (desc + " " + " ".join(topics)).lower()
                    if any(w in desc_lower for w in ["alternative", "replace", "saas", "workflow", "automation"]):
                        pillar = "FOSS SaaS Alternatives"
                    elif any(w in desc_lower for w in ["ai", "llm", "local", "model", "inference", "ollama"]):
                        pillar = "Local AI & Edge Compute"
                    elif any(w in desc_lower for w in ["cli", "terminal", "tool", "shell", "git"]):
                        pillar = "Developer Power Tools & CLI"
                    elif any(w in desc_lower for w in ["docker", "server", "host", "proxy", "cloud"]):
                        pillar = "Self-Hosted Architecture"

                    records.append({
                        "source_id": f"GH-{repo.get('id', 0)}",
                        "source_title": f"{name}: {desc[:90]}",
                        "publisher": f"GitHub Trending ({license_name})",
                        "pillar": pillar,
                        "published_at": repo.get("updated_at", datetime.utcnow().isoformat()),
                        "url": repo.get("html_url", ""),
                        "excerpt": f"Trending open source repository with {stars:,} stars ({lang}, {license_name}): {desc}",
                        "source_type": "github_repository",
                        "trust_score": 0.98
                    })
        except Exception as e:
            logger.debug(f"GitHub trending fetch skipped: {e}")
        return records

    def acquire_sources(self, live_fetch: bool = True) -> list[dict]:
        """
        Gathers source records from curated seed records, live RSS feeds,
        GitHub Trending Repos, and Hacker News FOSS signals.
        """
        all_sources = self.load_seed_records()
        seen_titles = {s.get("source_title", "").lower() for s in all_sources}

        if live_fetch:
            # 1. Fetch real-time trending Hacker News discussions
            try:
                live_trends = self.fetch_trending_niche_signals()
                for t in live_trends:
                    if t.get("source_title", "").lower() not in seen_titles:
                        all_sources.append(t)
                        seen_titles.add(t.get("source_title", "").lower())
            except Exception as e:
                logger.warning(f"Live trend search warning: {e}")

            # 2. Fetch real-time GitHub Trending Repositories
            try:
                gh_repos = self.fetch_github_trending()
                for g in gh_repos:
                    if g.get("source_title", "").lower() not in seen_titles:
                        all_sources.append(g)
                        seen_titles.add(g.get("source_title", "").lower())
            except Exception as e:
                logger.warning(f"GitHub trending search warning: {e}")

            # 3. Ingest live RSS feeds
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

