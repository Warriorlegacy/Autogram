"""
Sync and configure all Autogram cron jobs on cron-job.org via REST API
"""
import requests
import json
import time

CRON_KEY = "BilYJliJ/6GIVaoqQBjUMdE/MH41nNXdUdh9kpAT6kA="
HEADERS = {
    "Authorization": f"Bearer {CRON_KEY}",
    "Content-Type": "application/json"
}

def list_jobs():
    r = requests.get("https://api.cron-job.org/jobs", headers=HEADERS, timeout=15)
    if r.status_code == 200:
        return r.json().get("jobs", [])
    print(f"Failed to list jobs: {r.status_code} {r.text}")
    return []

if __name__ == "__main__":
    print("=== FETCHING EXISTING JOBS FROM CRON-JOB.ORG ===")
    current = list_jobs()
    print(f"Found {len(current)} existing jobs:")
    for j in current:
        print(f" - [{j.get('jobId')}] {j.get('title')} -> {j.get('url')}")
