"""
Autogram — Automated cron-job.org Setup Script
Creates all 7 daily Instagram publishing slot webhooks on cron-job.org via REST API.
"""

import sys
import json
import requests

GITHUB_TOKEN = "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"
REPO = "Warriorlegacy/Autogram"
DISPATCH_URL = f"https://api.github.com/repos/{REPO}/dispatches"

SLOTS = [
    {"title": "Autogram Slot 1 (08:00 AM IST) — Mindset & Commute", "hour": 8, "minute": 0},
    {"title": "Autogram Slot 2 (10:30 AM IST) — Deep Work Tools", "hour": 10, "minute": 30},
    {"title": "Autogram Slot 3 (01:00 PM IST) — Tech Deep Dive", "hour": 13, "minute": 0},
    {"title": "Autogram Slot 4 (03:30 PM IST) — Mid-Day Growth Hacks", "hour": 15, "minute": 30},
    {"title": "Autogram Slot 5 (06:00 PM IST) — Client Acquisition", "hour": 18, "minute": 0},
    {"title": "Autogram Slot 6 (08:30 PM IST) — Prime Evening Deep-Dive", "hour": 20, "minute": 30},
    {"title": "Autogram Slot 7 (10:30 PM IST) — Late Night Blueprint", "hour": 22, "minute": 30},
]

def create_slot_job(api_key: str, title: str, hour: int, minute: int) -> dict:
    url = "https://api.cron-job.org/jobs"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "job": {
            "title": title,
            "url": DISPATCH_URL,
            "enabled": True,
            "saveResponses": True,
            "requestMethod": 1,  # POST
            "extendedData": {
                "headers": {
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "Autogram-Scheduler",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"event_type": "publish-slot"})
            },
            "schedule": {
                "timezone": "Asia/Kolkata",
                "hours": [hour],
                "minutes": [minute],
                "mdays": [-1],
                "months": [-1],
                "wdays": [-1]
            }
        }
    }
    resp = requests.put(url, headers=headers, json=payload, timeout=20)
    return {"status_code": resp.status_code, "response": resp.json() if resp.status_code in [200, 201] else resp.text}

def create_render_keepalive(api_key: str) -> dict:
    url = "https://api.cron-job.org/jobs"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "job": {
            "title": "Autogram Render Dashboard Keep-Alive",
            "url": "https://autogram-dashboard.onrender.com/health",
            "enabled": True,
            "saveResponses": False,
            "requestMethod": 0,  # GET
            "schedule": {
                "timezone": "UTC",
                "hours": [-1],
                "minutes": [-1],  # Every minute or interval handled by cron-job.org
                "mdays": [-1],
                "months": [-1],
                "wdays": [-1]
            }
        }
    }
    resp = requests.put(url, headers=headers, json=payload, timeout=20)
    return {"status_code": resp.status_code, "response": resp.json() if resp.status_code in [200, 201] else resp.text}

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/setup_cronjob_org.py <CRON_JOB_ORG_API_KEY>")
        print("\nGet your API key in 5 seconds from: https://console.cron-job.org/settings (API Keys tab)")
        sys.exit(1)

    api_key = sys.argv[1].strip()
    print(f"Connecting to cron-job.org API with provided key...")
    print(f"Target repository: {REPO}")
    print("=" * 60)

    success_count = 0
    for slot in SLOTS:
        print(f"Creating job: {slot['title']}...")
        res = create_slot_job(api_key, slot["title"], slot["hour"], slot["minute"])
        if res["status_code"] in [200, 201]:
            job_id = res["response"].get("jobId", "OK")
            print(f"  ✓ SUCCESS -> Job ID: {job_id}")
            success_count += 1
        else:
            print(f"  ✗ FAILED ({res['status_code']}): {res['response']}")

    print("=" * 60)
    print(f"Finished! {success_count}/{len(SLOTS)} publishing slots configured successfully.")

if __name__ == "__main__":
    main()
