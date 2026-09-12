import os
import requests
import json

CRON_KEY = os.getenv("CRON_JOB_ORG_API_KEY", "BilYJliJ/6GIVaoqQBjUMdE/MH41nNXdUdh9kpAT6kA=")
HEADERS = {"Authorization": f"Bearer {CRON_KEY}"}

r = requests.get("https://api.cron-job.org/jobs", headers=HEADERS, timeout=15)
jobs = r.json().get("jobs", [])
print(f"Total jobs: {len(jobs)}")
for j in jobs:
    if "Autogram" in j.get("title", ""):
        job_id = j["jobId"]
        detail = requests.get(f"https://api.cron-job.org/jobs/{job_id}", headers=HEADERS, timeout=10).json()
        job_data = detail.get("jobDetails", {})
        title = j.get("title")
        enabled = job_data.get("enabled")
        last_status = job_data.get("lastStatus")
        url = job_data.get("url")
        print(f"Job {job_id}: {title}")
        print(f"  Enabled: {enabled} | Last Status: {last_status} | URL: {url}")
        ext = job_data.get("extendedData", {})
        if ext:
            headers = ext.get("headers", {})
            if isinstance(headers, dict):
                auth = headers.get("Authorization", "")
            elif isinstance(headers, list):
                auth = "".join(str(h) for h in headers if "Authorization" in str(h))
            else:
                auth = ""
            masked_auth = (auth[:15] + "...") if auth else "None"
            print(f"  Method: {job_data.get('requestMethod')} | Auth: {masked_auth} | Body: {ext.get('body')}")
