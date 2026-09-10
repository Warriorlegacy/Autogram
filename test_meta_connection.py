#!/usr/bin/env python3
"""
test_meta_connection.py
Diagnoses and verifies Meta Instagram Graph API connection, credentials, token validity,
and account permissions before attempting live carousel publishing.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Force load latest .env
load_dotenv(override=True)

IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
META_API_VERSION = os.environ.get("META_API_VERSION", "v23.0").strip()
GRAPH_HOST = os.environ.get("META_GRAPH_HOST", "https://graph.facebook.com").strip()

def print_header(text: str):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def verify_meta_connection():
    print_header("AUTOGRAM META INSTAGRAM CONNECTION DIAGNOSTICS")

    print(f"[*] Meta API Version : {META_API_VERSION}")
    print(f"[*] Primary Host     : {GRAPH_HOST}")
    print(f"[*] Configured IG ID : {IG_USER_ID if IG_USER_ID else '[NOT SET]'}")
    token_preview = (IG_ACCESS_TOKEN[:10] + "..." + IG_ACCESS_TOKEN[-6:]) if len(IG_ACCESS_TOKEN) > 16 else "[NOT SET]"
    print(f"[*] Access Token     : {token_preview}")

    if not IG_ACCESS_TOKEN:
        print("\n[!] ERROR: IG_ACCESS_TOKEN is not configured in .env!")
        print("    Please provide your Meta Access Token to proceed.")
        print("\n    Quick Setup Steps:")
        print("    1. Go to: https://developers.facebook.com/tools/explorer/")
        print("    2. Select your Meta App and add permissions: instagram_basic, instagram_content_publish, pages_show_list")
        print("    3. Generate User Token and paste it as IG_ACCESS_TOKEN in .env")
        return False

    # 1. Test token with debug endpoint or /me
    print("\n[1/3] Testing Token Validity with Meta Graph API...")
    hosts_to_try = [GRAPH_HOST, "https://graph.facebook.com", "https://graph.instagram.com"]
    valid_host = None
    account_info = None

    for host in hosts_to_try:
        try:
            url = f"{host}/{META_API_VERSION}/me"
            params = {"access_token": IG_ACCESS_TOKEN, "fields": "id,name"}
            resp = requests.get(url, params=params, timeout=12)
            if resp.status_code == 200:
                valid_host = host
                account_info = resp.json()
                print(f"    [+] Successfully connected via: {host}")
                print(f"    [+] Token Owner: {account_info.get('name', 'Unknown')} (ID: {account_info.get('id')})")
                break
        except Exception:
            continue

    if not valid_host:
        # Try direct query if user ID is known
        print("    [-] Direct /me query returned an error. Testing token against /debug_token or direct ID...")
        try:
            url = f"https://graph.facebook.com/{META_API_VERSION}/{IG_USER_ID if IG_USER_ID else 'me'}"
            params = {"access_token": IG_ACCESS_TOKEN, "fields": "id,username"}
            resp = requests.get(url, params=params, timeout=12)
            if resp.status_code == 200:
                valid_host = "https://graph.facebook.com"
                account_info = resp.json()
                print(f"    [+] Successfully verified account: {account_info}")
            else:
                err = resp.json().get("error", {})
                print(f"    [!] Meta API Error ({resp.status_code}): {err.get('message')}")
                print(f"        Error Type: {err.get('type')}, Code: {err.get('code')}")
                return False
        except Exception as ex:
            print(f"    [!] Connection failed: {ex}")
            return False

    # 2. Query Instagram Account Details if IG_USER_ID is provided or search linked IG account
    print("\n[2/3] Checking Instagram Business Account Details...")
    if not IG_USER_ID:
        print("    [*] IG_USER_ID is blank in .env. Attempting automatic discovery from linked Facebook Pages...")
        try:
            url = f"{valid_host}/{META_API_VERSION}/me/accounts"
            params = {"access_token": IG_ACCESS_TOKEN, "fields": "id,name,instagram_business_account{id,username,name,profile_picture_url}"}
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                pages = resp.json().get("data", [])
                found_ig = None
                for page in pages:
                    ig_acc = page.get("instagram_business_account")
                    if ig_acc:
                        found_ig = ig_acc
                        print(f"    [+] Found linked Instagram Account!")
                        print(f"        - Instagram Handle : @{found_ig.get('username')}")
                        print(f"        - Instagram ID     : {found_ig.get('id')}")
                        print(f"        - Connected Page   : {page.get('name')} (ID: {page.get('id')})")
                        print(f"\n    [TIP] Set IG_USER_ID={found_ig.get('id')} in your .env to save this permanently!")
                        break
                if not found_ig:
                    print("    [!] No linked Instagram Business Account found on your Facebook Pages.")
                    print("        Please ensure your Instagram account is switched to Professional and connected to a Facebook Page.")
            else:
                print(f"    [-] Could not list accounts: {resp.text}")
        except Exception as e:
            print(f"    [-] Auto-discovery error: {e}")
    else:
        # Inspect specific account
        try:
            url = f"{valid_host}/{META_API_VERSION}/{IG_USER_ID}"
            params = {
                "access_token": IG_ACCESS_TOKEN,
                "fields": "id,username,name,profile_picture_url,followers_count,media_count"
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                ig_data = resp.json()
                print(f"    [+] Instagram Account Verified:")
                print(f"        - Username       : @{ig_data.get('username', 'N/A')}")
                print(f"        - Name           : {ig_data.get('name', 'N/A')}")
                print(f"        - Account ID     : {ig_data.get('id')}")
                print(f"        - Followers      : {ig_data.get('followers_count', 'N/A'):,}")
                print(f"        - Media Count    : {ig_data.get('media_count', 'N/A'):,}")
            else:
                err = resp.json().get("error", {})
                print(f"    [!] Failed to fetch IG Account {IG_USER_ID}: {err.get('message')}")
        except Exception as e:
            print(f"    [!] Error querying IG account: {e}")

    # 3. Check Publishing Quota Limit
    print("\n[3/3] Checking Content Publishing Rate Limits...")
    target_id = IG_USER_ID or (account_info.get("id") if account_info else None)
    if target_id:
        try:
            url = f"{valid_host}/{META_API_VERSION}/{target_id}/content_publishing_limit"
            params = {"access_token": IG_ACCESS_TOKEN}
            resp = requests.get(url, params=params, timeout=12)
            if resp.status_code == 200:
                limit_data = resp.json().get("data", [{}])[0]
                quota_usage = limit_data.get("quota_usage", 0)
                quota_total = limit_data.get("config", {}).get("quota_total", 50)
                print(f"    [+] Publishing Quota: {quota_usage}/{quota_total} posts used in the last 24 hours.")
            else:
                print(f"    [*] Note: Content publishing limit endpoint returned HTTP {resp.status_code}. (Standard for user tokens before first post).")
        except Exception as e:
            print(f"    [*] Note: Could not query publishing limit: {e}")

    print("\n" + "=" * 70)
    print("  DIAGNOSTICS COMPLETE")
    print("=" * 70)
    return True

if __name__ == "__main__":
    verify_meta_connection()
