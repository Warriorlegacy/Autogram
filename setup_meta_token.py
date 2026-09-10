#!/usr/bin/env python3
"""
setup_meta_token.py
Interactive CLI helper that takes your Meta Access Token, inspects your connected
Instagram accounts, exchanges it for a 60-day long-lived token (if App ID/Secret are provided),
and saves everything directly to your .env file.
"""

import os
import sys
import re
from pathlib import Path
import requests

ENV_PATH = Path(__file__).resolve().parent / ".env"

def update_env_file(key: str, value: str):
    """Safely updates or adds a key-value pair in .env file."""
    if not ENV_PATH.exists():
        ENV_PATH.write_text(f"{key}={value}\n", encoding="utf-8")
        return

    content = ENV_PATH.read_text(encoding="utf-8")
    pattern = rf"^{re.escape(key)}=.*$"
    
    if re.search(pattern, content, flags=re.MULTILINE):
        new_content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\n{key}={value}\n"
        
    ENV_PATH.write_text(new_content, encoding="utf-8")

def main():
    print("=" * 70)
    print("  AUTOGRAM META INSTAGRAM AUTOMATED SETUP")
    print("=" * 70)
    print("\nThis wizard will link your Instagram Professional account to Autogram.\n")

    token = input("1. Paste your Meta Access Token (from Graph API Explorer): ").strip()
    if not token:
        print("[!] No token entered. Exiting.")
        sys.exit(1)

    print("\n[*] Validating token with Meta Graph API...")
    url = "https://graph.facebook.com/v23.0/me"
    params = {"access_token": token, "fields": "id,name"}
    resp = requests.get(url, params=params)
    
    if resp.status_code != 200:
        print(f"[!] Token invalid or rejected by Meta ({resp.status_code}):")
        print(resp.text)
        sys.exit(1)

    user_data = resp.json()
    print(f"[+] Connected to Facebook Profile: {user_data.get('name')} (ID: {user_data.get('id')})")

    # Discover linked Instagram accounts from Pages
    print("\n[*] Searching for linked Instagram Business/Creator accounts...")
    pages_url = "https://graph.facebook.com/v23.0/me/accounts"
    pages_params = {
        "access_token": token,
        "fields": "id,name,access_token,instagram_business_account{id,username,name,followers_count}"
    }
    pages_resp = requests.get(pages_url, params=pages_params)
    
    found_ig_accounts = []
    if pages_resp.status_code == 200:
        for page in pages_resp.json().get("data", []):
            ig = page.get("instagram_business_account")
            if ig:
                found_ig_accounts.append({
                    "ig_id": ig.get("id"),
                    "username": ig.get("username"),
                    "name": ig.get("name"),
                    "followers": ig.get("followers_count", 0),
                    "page_name": page.get("name"),
                    "page_id": page.get("id"),
                    "page_token": page.get("access_token")
                })

    selected_ig_id = None
    final_token = token

    if found_ig_accounts:
        print(f"\n[+] Found {len(found_ig_accounts)} connected Instagram account(s):")
        for idx, acc in enumerate(found_ig_accounts, start=1):
            print(f"    [{idx}] @{acc['username']} ({acc['name']})")
            print(f"        ID: {acc['ig_id']} | Followers: {acc['followers']} | Linked Page: {acc['page_name']}")
        
        if len(found_ig_accounts) == 1:
            chosen = found_ig_accounts[0]
            selected_ig_id = chosen["ig_id"]
            # Page tokens often have permanent or 60-day validity for posting
            if chosen.get("page_token"):
                use_page_tok = input(f"\nUse Page Access Token for @{chosen['username']} (recommended for publishing)? [Y/n]: ").strip().lower()
                if use_page_tok in ("", "y", "yes"):
                    final_token = chosen["page_token"]
        else:
            choice = input(f"\nSelect which account to use [1-{len(found_ig_accounts)}]: ").strip()
            idx = int(choice) - 1
            chosen = found_ig_accounts[idx]
            selected_ig_id = chosen["ig_id"]
            if chosen.get("page_token"):
                final_token = chosen["page_token"]
    else:
        print("\n[!] No Instagram Business Account was detected on your Facebook Pages.")
        manual_id = input("If you know your numeric Instagram Account ID, enter it here (or press Enter to skip): ").strip()
        if manual_id:
            selected_ig_id = manual_id

    # Optional 60-day token extension
    app_id = input("\n2. Enter Meta App ID (optional, press Enter to skip): ").strip()
    if app_id:
        app_secret = input("   Enter Meta App Secret: ").strip()
        if app_secret:
            print("\n[*] Exchanging token for 60-day long-lived access token...")
            exch_url = "https://graph.facebook.com/v23.0/oauth/access_token"
            exch_params = {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": final_token
            }
            exch_resp = requests.get(exch_url, params=exch_params)
            if exch_resp.status_code == 200:
                long_lived_token = exch_resp.json().get("access_token")
                expires_in = exch_resp.json().get("expires_in", 5184000)
                final_token = long_lived_token
                print(f"[+] 60-Day Extension Granted! (Valid for {expires_in // 86400} days)")
                update_env_file("META_APP_ID", app_id)
                update_env_file("META_APP_SECRET", app_secret)
            else:
                print(f"[-] Could not extend token: {exch_resp.text}")

    # Save to .env
    print("\n[*] Saving credentials to .env...")
    update_env_file("IG_ACCESS_TOKEN", final_token)
    if selected_ig_id:
        update_env_file("IG_USER_ID", selected_ig_id)
    update_env_file("DRY_RUN", "false")

    print("\n" + "=" * 70)
    print("  CONFIGURATION SAVED SUCCESSFULLY!")
    print("=" * 70)
    print("Your .env has been updated with:")
    print(f"  • IG_ACCESS_TOKEN = {final_token[:12]}...{final_token[-6:]}")
    if selected_ig_id:
        print(f"  • IG_USER_ID      = {selected_ig_id}")
    print("  • DRY_RUN         = false")
    print("\nYou can now run:")
    print("  python test_meta_connection.py")
    print("to verify the connection anytime!")

if __name__ == "__main__":
    main()
