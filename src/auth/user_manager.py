"""
User Authentication and Access Management for Autogram SaaS.
Provides secure password hashing (PBKDF2-HMAC-SHA256), session management,
role-based access control (admin vs user), and tier entitlements.
"""

import os
import time
import hmac
import hashlib
import sqlite3
import secrets
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "autopilot.db"
SESSION_SECRET = os.getenv("AUTOGRAM_SESSION_SECRET", "autogram_secure_session_secret_token_2026_signhify")

# Password hashing configuration (PBKDF2-HMAC-SHA256, 100,000 rounds)
HASH_ITERATIONS = 100000

TIERS = {
    "starter": {
        "name": "Starter",
        "price_monthly": 29,
        "price_annual": 290,
        "badge": "Entry",
        "features": [
            "30 Carousels / month",
            "Auto-Detect AI Models",
            "Standard Prompt Library (15+ prompts)",
            "3 Design Templates",
            "Manual Publishing Export",
            "Email Support"
        ],
        "limits": {
            "carousels_per_month": 30,
            "reels_per_month": 10,
            "connected_accounts": 1
        }
    },
    "growth": {
        "name": "Growth Pro",
        "price_monthly": 79,
        "price_annual": 790,
        "badge": "Most Popular",
        "features": [
            "120 Carousels / month",
            "40 AI Video Reels / month",
            "All AI Providers (OpenAI, Claude, Groq, Ollama, Custom)",
            "Full Prompt Library (30+ prompts)",
            "All 5 Carousel Design Templates",
            "7x Daily Automated Scheduler",
            "Direct Meta Graph API Publishing",
            "Priority Support"
        ],
        "limits": {
            "carousels_per_month": 120,
            "reels_per_month": 40,
            "connected_accounts": 3
        }
    },
    "agency_pro": {
        "name": "Agency Pro",
        "price_monthly": 199,
        "price_annual": 1990,
        "badge": "Uncapped",
        "features": [
            "Unlimited Carousels & Reels",
            "Custom Endpoints & Private LLM Proxies",
            "Full White-Label Watermark Removal",
            "Unlimited Client Workspaces",
            "Auto-DM Engine & Comment Funnels",
            "Dedicated Account Manager & SLA",
            "Custom CSS Design System Overrides"
        ],
        "limits": {
            "carousels_per_month": 99999,
            "reels_per_month": 99999,
            "connected_accounts": 10
        }
    },
    "owner": {
        "name": "Master Owner VIP",
        "price_monthly": 0,
        "price_annual": 0,
        "badge": "Admin Master",
        "features": [
            "100% Unrestricted Root Master Access",
            "Zero System Rate Limits",
            "Direct Subprocess & Cloud Daemon Control",
            "License Key Minting & User Tier Management"
        ],
        "limits": {
            "carousels_per_month": 999999,
            "reels_per_month": 999999,
            "connected_accounts": 999
        }
    }
}


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 100k rounds and a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS
    )
    return f"pbkdf2:sha256:{HASH_ITERATIONS}${salt}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        parts = password_hash.split("$")
        if len(parts) != 3:
            return False
        meta, salt, stored_key = parts
        _, _, iterations_str = meta.split(":")
        iterations = int(iterations_str)

        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False


def generate_session_token(user_id: int, username: str, role: str) -> str:
    """Generate an HMAC-signed session token with expiration timestamp."""
    expire = int(time.time()) + (86400 * 14)  # 14 days
    payload = f"{user_id}:{username}:{role}:{expire}"
    sig = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
    return f"{payload}:{sig}"


def verify_session_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Verify session token signature and expiration."""
    if not token or not isinstance(token, str):
        return None
    parts = token.strip().split(":")
    if len(parts) != 5:
        return None
    user_id_str, username, role, expire_str, sig = parts
    try:
        expire = int(expire_str)
        if time.time() > expire:
            return None  # Expired
        payload = f"{user_id_str}:{username}:{role}:{expire_str}"
        expected_sig = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
        if not hmac.compare_digest(sig, expected_sig):
            return None
        return {
            "user_id": int(user_id_str),
            "username": username,
            "role": role,
            "expires_at": expire
        }
    except Exception:
        return None


class UserManager:
    def __init__(self):
        self.init_db()
        self.seed_admin_user()

    def init_db(self):
        """Create users table in autopilot.db if not exists."""
        conn = get_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    tier TEXT NOT NULL DEFAULT 'starter',
                    license_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def seed_admin_user(self):
        """Ensure the master admin user (signhify.studio) exists."""
        admin_username = "signhify.studio"
        admin_password = os.getenv("AUTOGRAM_ADMIN_PASSWORD", "Piyushrajput#1")
        
        conn = get_db()
        try:
            row = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (admin_username,)).fetchone()
            if not row:
                hashed = hash_password(admin_password)
                conn.execute(
                    "INSERT INTO users (username, email, password_hash, role, tier) VALUES (?, ?, ?, ?, ?)",
                    (admin_username, "admin@signhify.studio", hashed, "admin", "owner")
                )
                conn.commit()
            else:
                # Update password if changed
                if not verify_password(admin_password, row["password_hash"]):
                    new_hash = hash_password(admin_password)
                    conn.execute("UPDATE users SET password_hash = ?, role = 'admin', tier = 'owner' WHERE id = ?", (new_hash, row["id"]))
                    conn.commit()
        except Exception as e:
            print(f"Admin seeding notice: {e}")
        finally:
            conn.close()

    def register_user(self, username: str, password: str, email: Optional[str] = None, tier: str = "starter") -> Dict[str, Any]:
        """Register a new standard user."""
        username = username.strip().lower()
        if not username or len(username) < 3:
            return {"ok": False, "error": "Username must be at least 3 characters long."}
        if not password or len(password) < 6:
            return {"ok": False, "error": "Password must be at least 6 characters long."}

        tier = tier.lower()
        if tier not in ["starter", "growth", "agency_pro", "owner"]:
            tier = "starter"

        hashed = hash_password(password)
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role, tier) VALUES (?, ?, ?, 'user', ?)",
                (username, email.strip().lower() if email else None, hashed, tier)
            )
            conn.commit()
            user_id = cursor.lastrowid
            token = generate_session_token(user_id, username, "user")
            return {
                "ok": True,
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "role": "user",
                    "tier": tier
                },
                "token": token
            }
        except sqlite3.IntegrityError:
            return {"ok": False, "error": "Username or email is already registered."}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            conn.close()

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user by username and password, returning session token."""
        username = username.strip().lower()
        conn = get_db()
        try:
            row = conn.execute("SELECT * FROM users WHERE LOWER(username) = ?", (username,)).fetchone()
            if not row:
                return {"ok": False, "error": "Invalid username or password."}

            if not verify_password(password, row["password_hash"]):
                return {"ok": False, "error": "Invalid username or password."}

            # Update last_login
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row["id"]))
            conn.commit()

            token = generate_session_token(row["id"], row["username"], row["role"])
            return {
                "ok": True,
                "user": {
                    "id": row["id"],
                    "username": row["username"],
                    "email": row["email"],
                    "role": row["role"],
                    "tier": row["tier"]
                },
                "token": token
            }
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db()
        try:
            row = conn.execute("SELECT id, username, email, role, tier, created_at, last_login FROM users WHERE id = ?", (user_id,)).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def list_users(self) -> List[Dict[str, Any]]:
        conn = get_db()
        try:
            rows = conn.execute("SELECT id, username, email, role, tier, created_at, last_login FROM users ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_tier(self, user_id: int, new_tier: str) -> bool:
        conn = get_db()
        try:
            conn.execute("UPDATE users SET tier = ? WHERE id = ?", (new_tier.lower(), user_id))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()


user_manager = UserManager()
