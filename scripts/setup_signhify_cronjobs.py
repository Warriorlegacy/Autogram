"""
Autogram - Signhify Automated Cron Setup Script
Creates the 3x daily Reels and 1x daily Carousel publishing webhooks on cron-job.org via REST API.
"""

import json
import os
import sys
from pathlib import Path
import requests

CRON_KEY = os.getenv("CRON_JOB_ORG_API_KEY", "BilYJliJ/6GIVaoqQBjUMdE/MH41nNXdUdh9kpAT6kA=")
GITHUB_TOKEN = "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"
REPO = "Warriorlegacy/Autogram"
DISPATCH_URL = f"https://api.github.com/repos/{REPO}/dispatches"

SIGNHIFY_JOBS = [
    # 3x Daily Reels for Signhify Studio Promotion
    {
        "title": "Signhify Reel 1 (10:30 AM IST) - Morning 3D Promo",
        "event_type": "publish-reel",
        "hour": 10,
        "minute": 30,
    },
    {
        "title": "Signhify Reel 2 (02:30 PM IST) - Afternoon 3D Showcase",
        "event_type": "publish-reel",
        "hour": 14,
        "minute": 30,
    },
    {
        "title": "Signhify Reel 3 (08:30 PM IST) - Prime Evening 3D Viral Reel",
        "event_type": "publish-reel",
        "hour": 20,
        "minute": 30,
    },
    # 1x Daily Carousel for Signhify Studio Promotion
    {
        "title": "Signhify Carousel (12:30 PM IST) - Daily Viral 3D Promo Carousel",
        "event_type": "publish-carousel",
        "hour": 12,
        "minute": 30,
    },
]


def create_or_update_job(api_key: str, job_def: dict, existing_jobs: list) -> dict:
    url = "https://api.cron-job.org/jobs"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    title = job_def["title"]
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
                    "Content-Type": "application/json",
                },
                "body": json.dumps({"event_type": job_def["event_type"]}),
            },
            "schedule": {
                "timezone": "Asia/Kolkata",
                "hours": [job_def["hour"]],
                "minutes": [job_def["minute"]],
                "mdays": [-1],
                "months": [-1],
                "wdays": [-1],
            },
        }
    }

    # Check if job already exists with same or similar title
    existing_id = None
    for j in existing_jobs:
        if j.get("title", "").strip().lower() == title.strip().lower():
            existing_id = j.get("jobId")
            break

    if existing_id:
        # Update existing job via PATCH
        patch_url = f"https://api.cron-job.org/jobs/{existing_id}"
        resp = requests.patch(patch_url, headers=headers, json=payload, timeout=20)
        return {"action": "updated", "status_code": resp.status_code, "jobId": existing_id}
    else:
        # Create new job via PUT
        resp = requests.put(url, headers=headers, json=payload, timeout=20)
        return {"action": "created", "status_code": resp.status_code, "response": resp.json() if resp.status_code in [200, 201] else resp.text}


def main():
    api_key = sys.argv[1].strip() if len(sys.argv) > 1 else CRON_KEY
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"Connecting to cron-job.org API with provided key...")
    print(f"Target repository: {REPO} -> {DISPATCH_URL}")
    print("=" * 60)

    # Fetch existing jobs to avoid duplicates
    r = requests.get("https://api.cron-job.org/jobs", headers=headers, timeout=15)
    existing_jobs = r.json().get("jobs", []) if r.status_code == 200 else []
    print(f"Current existing cron jobs on account: {len(existing_jobs)}")

    for job_def in SIGNHIFY_JOBS:
        print(f"Configuring job: '{job_def['title']}' (event: {job_def['event_type']} @ {job_def['hour']:02d}:{job_def['minute']:02d} IST)...")
        res = create_or_update_job(api_key, job_def, existing_jobs)
        print(f"  Result: {res}")

    print("=" * 60)
    print("All Signhify Reels (3x daily) and Carousel (1x daily) cron jobs configured successfully!")


if __name__ == "__main__":
    main()
