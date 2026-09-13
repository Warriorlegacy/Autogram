"""
src/leads/comment_automation.py - Automated Lead Capture & Auto-DM Trigger Engine
Processes "comment AUTO" triggers from Instagram, logs leads to SQLite, and dispatches DMs.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path("./autopilot.db")

def init_leads_table():
    """Initializes the leads table in autopilot.db if not present."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                user_handle TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                trigger_keyword TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                dm_sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

class CommentLeadAutomation:
    """Manages comment-to-DM lead generation workflows."""

    def __init__(self):
        init_leads_table()

    def process_incoming_comment(self, user_handle: str, comment_text: str, platform: str = "instagram") -> dict:
        """
        Detects if comment matches 'AUTO' trigger. If matched, logs lead and prepares DM response.
        """
        normalized = comment_text.strip().upper()
        triggers = ["AUTO", "AUTOPILOT", "SYSTEM", "BLUEPRINT"]
        matched = next((t for t in triggers if t in normalized), None)

        if not matched:
            return {"status": "ignored", "reason": "no trigger keyword"}

        dm_message = (
            f"Hey @{user_handle.lstrip('@')}! Piyush Raj Singh here from Signhify Studio.\n\n"
            "Here is your direct access to the Hormozi-Style Autonomous Posting System & Full Studio Blueprint:\n"
            "👉 https://signhify.studio\n\n"
            "Let's get your omnipresence machine running on autopilot!"
        )

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leads (platform, user_handle, comment_text, trigger_keyword, status, dm_sent_at)
                VALUES (?, ?, ?, ?, 'dispatched', ?)
            """, (platform, user_handle, comment_text, matched, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            lead_id = cursor.lastrowid
            conn.commit()

        logger.info(f"Captured lead #{lead_id} from @{user_handle} on {platform} (Keyword: {matched})")
        return {
            "status": "dispatched",
            "lead_id": lead_id,
            "user_handle": user_handle,
            "trigger": matched,
            "dm_message": dm_message
        }

    def list_recent_leads(self, limit: int = 25) -> list[dict]:
        """Returns recent captured leads from the database."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
