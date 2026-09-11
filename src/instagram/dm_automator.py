"""
In-House Instagram Auto-DM & Comment-Reply Automation Engine (src/instagram/dm_automator.py).
Replaces third-party SaaS (ManyChat) with an autonomous, zero-cost, self-hosted system.
Monitors posts for "FOSS" or "PROMPT" comments, posts randomized public replies to boost reach,
and sends automated Private Reply DMs with GitHub/Notion blueprints directly via Meta Graph API.
"""

import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from src.config import settings
from src.db.database import db

logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent.parent.parent / "data" / "dm_automation_state.json"

# Trigger keywords and matching rules
TRIGGERS = {
    "FOSS": {
        "patterns": [r"\bfoss\b", r"\bself-host(ed|ing)?\b", r"\bdocker\b", r"\bblueprint\b", r"\bsetup\b"],
        "public_replies": [
            "Just sent the full Docker setup & GitHub link to your DMs! 🚀",
            "Check your DMs! The 1-click self-host blueprint is on the way ⚡",
            "Sent! Enjoy the free alternative. Let me know if you hit any setup snags 🛠️",
            "DM sent! Stop paying SaaS bills and start shipping 📦"
        ],
        "dm_text": (
            "Hey builder! 👋\n\n"
            "Here is the complete self-hosting blueprint and 1-line Docker setup from our recent breakdown:\n\n"
            "📦 GitHub Master Vault: https://github.com/signhify/open-source-vault\n"
            "⚡ 1-Line Commands & Configs: https://github.com/signhify/open-source-vault/blob/main/quickstart.md\n\n"
            "Stop paying $100s/mo in SaaS bills. Follow @signhify.studio for daily battle-tested open source tools! 🚀"
        )
    },
    "PROMPT": {
        "patterns": [r"\bprompt\b", r"\bcode\b", r"\bmegaprompt\b", r"\bchatgpt\b", r"\bsecret\b"],
        "public_replies": [
            "Just sent the complete prompt code & variables to your DMs! 🔥",
            "Check your inbox! The copy-paste prompt architecture is in your DMs ⚡",
            "Sent! Copy and paste it straight into ChatGPT or Claude 📋",
            "DM sent! Replace [INPUT_DATA] before running 🧠"
        ],
        "dm_text": (
            "Here is the full copy-paste prompt code + variables from our breakdown! 🚀\n\n"
            "🧠 Master Prompt Vault: https://github.com/signhify/prompt-vault\n"
            "🎯 Tested On: GPT-4o, Claude 3.5 Sonnet, DeepSeek-R1, o3-mini\n"
            "📋 Copy-paste template: https://github.com/signhify/prompt-vault/blob/main/viral_prompts.md\n\n"
            "Make sure to replace [INPUT_DATA] before running.\n"
            "Follow @signhify.studio for daily tested AI prompt architectures! ⚡"
        )
    }
}


class InstagramDMAutomator:
    """
    Autonomous Instagram Comment-Reply and Private Reply (Auto-DM) engine.
    Uses Meta's official Instagram Graph API:
    - POST /{comment-id}/replies  (Public reply)
    - POST /{ig-user-id}/messages  (Private Reply DM to commenter)
    """

    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.meta_api_version}"
        self.user_id = settings.ig_user_id
        self.token = settings.ig_access_token
        self.dry_run = settings.dry_run
        self.state_file = STATE_FILE
        self._init_state()

    def _init_state(self):
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps({"processed_comments": {}}, indent=2), encoding="utf-8")

    def load_processed_comments(self) -> set[str]:
        """Loads set of previously handled comment IDs to prevent duplicate DMs."""
        processed = set()
        # 1. Check database if available
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT comment_id FROM auto_dm_log")
                for row in cursor.fetchall():
                    processed.add(row[0])
        except Exception:
            pass

        # 2. Check JSON state file fallback
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                processed.update(data.get("processed_comments", {}).keys())
            except Exception:
                pass

        return processed

    def record_processed_comment(
        self,
        comment_id: str,
        media_id: str,
        username: str,
        comment_text: str,
        keyword: str,
        public_reply_id: str,
        dm_status: str
    ):
        """Persists processed comment to DB and state file."""
        # 1. DB persistence
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO auto_dm_log 
                (comment_id, media_id, username, comment_text, keyword, public_reply_id, dm_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (comment_id, media_id, username, comment_text, keyword, public_reply_id, dm_status))
                conn.commit()
        except Exception as e:
            logger.debug(f"DB auto_dm_log persistence skipped: {e}")

        # 2. JSON state file persistence
        try:
            data = {"processed_comments": {}}
            if self.state_file.exists():
                try:
                    data = json.loads(self.state_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            data["processed_comments"][comment_id] = {
                "media_id": media_id,
                "username": username,
                "keyword": keyword,
                "public_reply_id": public_reply_id,
                "dm_status": dm_status,
                "timestamp": time.time()
            }
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to update auto_dm_state.json: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on processed comments and DMs from DB or state file."""
        stats = {
            "total_dms_sent": 0,
            "total_comments_handled": 0,
            "by_keyword": {"FOSS": 0, "PROMPT": 0},
            "recent_actions": []
        }
        # Try DB first
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM auto_dm_log WHERE dm_status = 'DM_SENT'")
                stats["total_dms_sent"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM auto_dm_log")
                stats["total_comments_handled"] = cursor.fetchone()[0]

                cursor.execute("SELECT keyword, COUNT(*) FROM auto_dm_log GROUP BY keyword")
                for kw, cnt in cursor.fetchall():
                    if kw:
                        stats["by_keyword"][kw] = cnt

                cursor.execute("""
                SELECT comment_id, media_id, username, comment_text, keyword, dm_status, created_at 
                FROM auto_dm_log ORDER BY created_at DESC LIMIT 15
                """)
                for row in cursor.fetchall():
                    stats["recent_actions"].append({
                        "comment_id": row[0],
                        "media_id": row[1],
                        "username": row[2],
                        "comment_text": row[3],
                        "keyword": row[4],
                        "dm_status": row[5],
                        "timestamp": str(row[6])
                    })
                return stats
        except Exception as e:
            logger.debug(f"DB read for DM stats failed, falling back to JSON: {e}")

        # JSON fallback
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                processed = data.get("processed_comments", {})
                stats["total_comments_handled"] = len(processed)
                for cid, item in processed.items():
                    if item.get("dm_status") == "DM_SENT":
                        stats["total_dms_sent"] += 1
                    kw = item.get("keyword")
                    if kw in stats["by_keyword"]:
                        stats["by_keyword"][kw] += 1
                    stats["recent_actions"].append({
                        "comment_id": cid,
                        "media_id": item.get("media_id"),
                        "username": item.get("username"),
                        "comment_text": "",
                        "keyword": kw,
                        "dm_status": item.get("dm_status"),
                        "timestamp": item.get("timestamp")
                    })
                stats["recent_actions"] = stats["recent_actions"][-15:]
            except Exception:
                pass

        return stats

    def fetch_recent_media_ids(self, limit: int = 5) -> List[str]:
        """Fetches recent published media IDs for @signhify.studio."""
        if self.dry_run or not self.token or not self.user_id:
            logger.info("[DRY-RUN] Simulating media fetch for recent posts.")
            return ["mock_media_12345"]

        url = f"{self.base_url}/{self.user_id}/media"
        params = {
            "fields": "id,caption,timestamp",
            "limit": limit,
            "access_token": self.token
        }
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            items = resp.json().get("data", [])
            return [item["id"] for item in items if "id" in item]
        except Exception as e:
            logger.error(f"Failed to fetch recent Instagram media: {e}")
            return []

    def fetch_comments_for_media(self, media_id: str) -> List[Dict[str, Any]]:
        """Fetches top-level comments on a given Instagram media post."""
        if self.dry_run or str(media_id).startswith("mock"):
            logger.info(f"[DRY-RUN] Simulating comments fetch for media {media_id}")
            return [
                {"id": f"sim_c_{int(time.time()*1000)%10000}_foss", "text": "FOSS please!", "username": "builder_alex"},
                {"id": f"sim_c_{int(time.time()*1000)%10000}_prompt", "text": "Can you send the PROMPT code?", "username": "prompt_engineer_99"}
            ]

        url = f"{self.base_url}/{media_id}/comments"
        params = {
            "fields": "id,text,username,timestamp",
            "access_token": self.token
        }
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch comments for media {media_id}: {e}")
            return []

    def send_public_reply(self, comment_id: str, message: str) -> str:
        """Publishes a randomized public comment reply to boost algorithmic reach."""
        if self.dry_run or str(comment_id).startswith("sim_"):
            sim_reply_id = f"mock_reply_{int(time.time()*1000)%100000}"
            logger.info(f"[DRY-RUN] Simulated public comment reply to {comment_id}: '{message}' (ID: {sim_reply_id})")
            return sim_reply_id

        url = f"{self.base_url}/{comment_id}/replies"
        data = {
            "message": message,
            "access_token": self.token
        }
        resp = requests.post(url, data=data, timeout=20)
        resp.raise_for_status()
        reply_id = resp.json().get("id", "")
        logger.info(f"Published public reply to comment {comment_id}: Reply ID = {reply_id}")
        return reply_id

    def send_private_dm(self, comment_id: str, message_text: str) -> bool:
        """
        Sends a private DM to the commenter using Meta's Private Replies API:
        POST /{ig-user-id}/messages with recipient: {"comment_id": comment_id}
        """
        if self.dry_run or str(comment_id).startswith("sim_"):
            logger.info(f"[DRY-RUN] Simulated sending private DM for comment {comment_id}")
            return True

        url = f"{self.base_url}/{self.user_id}/messages"
        payload = {
            "recipient": {
                "comment_id": comment_id
            },
            "message": {
                "text": message_text
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": self.token
        }
        try:
            resp = requests.post(url, params=params, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                logger.info(f"Successfully sent automated private DM for comment {comment_id}!")
                return True
            else:
                logger.warning(f"Private DM returned status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending private DM for comment {comment_id}: {e}")
            return False

    def match_keyword(self, comment_text: str) -> Optional[str]:
        """Matches comment text against FOSS or PROMPT trigger patterns."""
        text_lower = comment_text.lower().strip()
        for trigger_key, cfg in TRIGGERS.items():
            for pattern in cfg["patterns"]:
                if re.search(pattern, text_lower):
                    return trigger_key
        return None

    def process_comment(self, comment: Dict[str, Any], media_id: str) -> Optional[Dict[str, Any]]:
        """Evaluates a single comment and executes auto-reply + DM if matched."""
        comment_id = comment.get("id")
        text = comment.get("text", "")
        username = comment.get("username", "user")

        if not comment_id:
            return None

        matched_key = self.match_keyword(text)
        if not matched_key:
            return None  # No action needed for generic comments

        cfg = TRIGGERS[matched_key]
        public_reply_text = random.choice(cfg["public_replies"])
        dm_text = cfg["dm_text"]

        logger.info(f"Trigger matched! Comment '{text}' by @{username} matched keyword [{matched_key}].")

        # 1. Post randomized public reply
        public_reply_id = "sim_reply"
        try:
            public_reply_id = self.send_public_reply(comment_id, public_reply_text)
        except Exception as e:
            logger.warning(f"Could not send public reply to comment {comment_id}: {e}")

        # 2. Brief typing pause to respect Meta humanization rules
        time.sleep(random.uniform(1.0, 2.5))

        # 3. Send private DM
        dm_sent = False
        try:
            dm_sent = self.send_private_dm(comment_id, dm_text)
        except Exception as e:
            logger.warning(f"Could not send private DM for comment {comment_id}: {e}")

        status_str = "DM_SENT" if dm_sent else "PUBLIC_ONLY"
        self.record_processed_comment(
            comment_id=comment_id,
            media_id=media_id,
            username=username,
            comment_text=text,
            keyword=matched_key,
            public_reply_id=public_reply_id,
            dm_status=status_str
        )

        return {
            "comment_id": comment_id,
            "username": username,
            "keyword": matched_key,
            "public_reply_id": public_reply_id,
            "dm_status": status_str
        }

    def scan_and_automate(self, limit_posts: int = 5) -> Dict[str, Any]:
        """
        Scans recent Instagram posts, discovers new comments, and executes auto-DMs.
        Returns detailed summary of actions taken.
        """
        logger.info("==================================================")
        logger.info(" Starting Instagram Auto-DM & Comment-Reply Scan")
        logger.info("==================================================")

        processed_ids = self.load_processed_comments()
        media_ids = self.fetch_recent_media_ids(limit=limit_posts)
        
        actions_taken = []
        total_comments_checked = 0

        for mid in media_ids:
            comments = self.fetch_comments_for_media(mid)
            for c in comments:
                cid = c.get("id")
                if not cid or cid in processed_ids:
                    continue  # Already processed

                total_comments_checked += 1
                result = self.process_comment(c, media_id=mid)
                if result:
                    actions_taken.append(result)
                    processed_ids.add(cid)

        summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "media_scanned": len(media_ids),
            "comments_checked": total_comments_checked,
            "actions_executed": len(actions_taken),
            "details": actions_taken
        }

        logger.info(
            f"Auto-DM Scan Finished: {len(actions_taken)} automated responses dispatched "
            f"across {total_comments_checked} new comments."
        )
        return summary


dm_automator = InstagramDMAutomator()
