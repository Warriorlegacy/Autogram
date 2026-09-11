# Autogram — Autonomous HTTP Webhook Trigger Guide

This guide explains how to bypass GitHub's internal schedule queue delays and trigger the **Autogram Autonomous Publishing Engine** with second-level precision using external HTTP POST requests.

---

## 1. Quick Reference: The HTTP Requests

You have **two distinct endpoints** to trigger the publishing pipeline on demand or on schedule:

### Option A: Trigger GitHub Actions (`repository_dispatch`) — Recommended

This spins up an Ubuntu cloud runner on GitHub Actions, runs Playwright Chromium, renders 10 slides, uploads them to the CDN, publishes to Instagram, and commits memory to git.

* **URL:** `https://api.github.com/repos/Warriorlegacy/Autogram/dispatches`
* **Method:** `POST`
* **Headers:**
  ```http
  Authorization: Bearer <YOUR_GITHUB_PAT>
  Accept: application/vnd.github+json
  User-Agent: Autogram-Scheduler
  Content-Type: application/json
  ```
* **Body (JSON):**
  ```json
  {
    "event_type": "publish-slot"
  }
  ```
* **Expected Response:** `204 No Content` (Workflow starts instantly in GitHub Actions)

---

### Option B: Trigger Live Render Backend Directly (`/api/webhook/autopilot`)

This triggers the pipeline directly on your hosted Render web service without needing GitHub Actions runner minutes.

* **URL:** `https://autogram-dashboard.onrender.com/api/webhook/autopilot?mode=live`
* **Method:** `POST`
* **Headers:**
  ```http
  Authorization: Bearer autogram_owner_vip_2026
  User-Agent: Autogram-Scheduler
  ```
* **Expected Response:**
  ```json
  {
    "ok": true,
    "message": "Autonomous pipeline triggered successfully in LIVE mode.",
    "status": "started",
    "brand": "@signhify.studio"
  }
  ```

---

## 2. Generating a GitHub Personal Access Token (PAT)

To use **Option A** (`api.github.com`), you need a GitHub token with repository permissions:

1. Go to **GitHub Settings** → **Developer Settings** → **Personal Access Tokens** → **Tokens (classic)**
   * Direct Link: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**.
3. Name it: `Autogram-Scheduler`.
4. Expiration: **No expiration** (or 1 year).
5. Select Scopes:
   * [x] **`repo`** (Full control of private repositories)
   * [x] **`workflow`** (Update and trigger GitHub Action workflows)
6. Click **Generate token** and copy the token (`ghp_...`).

---

## 3. Step-by-Step: Setting Up 100% Free Autonomous Cron (cron-job.org)

[cron-job.org](https://cron-job.org) is the best free external scheduler. It has **zero delay**, supports timezone selection (`Asia/Kolkata`), allows unlimited jobs, and runs 24/7 without requiring your computer to be open.

### Step 1: Create a Free Account
1. Open [https://cron-job.org](https://cron-job.org) and register for a free account.
2. Verify your email address.

### Step 2: Create the 7 Daily Slot Jobs
In the dashboard, click **Create Cronjob** and configure the fields:

#### Job Settings:
* **Title:** `Autogram Slot 1 - 08:00 AM IST`
* **URL:** `https://api.github.com/repos/Warriorlegacy/Autogram/dispatches`
* **Request Method:** `POST`

#### Schedule:
* **Execution Schedule:** User-defined (Cron)
* **Timezone:** Select `Asia/Kolkata (IST)`
* **Time:** Set according to the slot schedule below.

#### Request Headers:
Click **Advanced** → **Request Headers** → **Add Header**:
1. `Authorization` → `Bearer ghp_YOUR_GITHUB_TOKEN`
2. `Accept` → `application/vnd.github+json`
3. `User-Agent` → `Autogram-Scheduler`
4. `Content-Type` → `application/json`

#### Request Body:
Under **Request Body**, enter:
```json
{"event_type": "publish-slot"}
```

#### Failure / Notification Settings:
* **Send notification on failure:** Enabled
* Click **Create**.

---

## 4. The 7 Strategic Daily Posting Slots (Asia/Kolkata)

Repeat the job creation for the 7 daily engagement windows:

| Slot # | Time (IST) | Time (UTC) | Content Pillar Focus | cron-job.org Schedule |
|---|---|---|---|---|
| **Slot 1** | **08:00 AM** | 02:30 UTC | Morning Commute & Mindset | Minute `00`, Hour `08` |
| **Slot 2** | **10:30 AM** | 05:00 UTC | Deep Work Tools & Architecture | Minute `30`, Hour `10` |
| **Slot 3** | **01:00 PM** | 07:30 UTC | Lunch Break Frameworks | Minute `00`, Hour `13` |
| **Slot 4** | **03:30 PM** | 10:00 UTC | Mid-Day Growth Hacks & Prompts | Minute `30`, Hour `15` |
| **Slot 5** | **06:00 PM** | 12:30 UTC | Outbound & Client Acquisition | Minute `00`, Hour `18` |
| **Slot 6** | **08:30 PM** | 15:00 UTC | Prime Evening Deep-Dive | Minute `30`, Hour `20` |
| **Slot 7** | **10:30 PM** | 17:00 UTC | Late-Night Founder Operating Systems | Minute `30`, Hour `22` |

> [!TIP]
> You can also set a single job that runs at minutes `00, 30` during those hours, or 7 separate named jobs for clear individual monitoring.

---

## 5. Keep Render Dashboard Awake (Zero Quota Usage)

If you use Render, keep the free service from spinning down by creating an 8th cron job on **cron-job.org**:

* **Title:** `Render Keep-Alive Ping`
* **URL:** `https://autogram-dashboard.onrender.com/health`
* **Method:** `GET`
* **Schedule:** `Every 10 minutes` (all hours, all days)

This ensures Render is always warm and ready with **zero impact on your GitHub Actions quota**.

---

## 6. Testing the Trigger from Terminal / PowerShell

You can verify the trigger immediately from your computer with either of these commands:

### Using cURL (Command Prompt / Bash):
```bash
curl -i -X POST "https://api.github.com/repos/Warriorlegacy/Autogram/dispatches" \
  -H "Authorization: Bearer <YOUR_GITHUB_TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  -H "User-Agent: Autogram-Scheduler" \
  -H "Content-Type: application/json" \
  -d "{\"event_type\": \"publish-slot\"}"
```
*Expected output: `HTTP/2 204`*

### Using PowerShell:
```powershell
$headers = @{
    "Authorization" = "Bearer <YOUR_GITHUB_TOKEN>"
    "Accept"        = "application/vnd.github+json"
    "User-Agent"    = "Autogram-Scheduler"
}
$body = '{"event_type": "publish-slot"}'
Invoke-RestMethod -Uri "https://api.github.com/repos/Warriorlegacy/Autogram/dispatches" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

### Using GitHub CLI (`gh`):
```bash
gh workflow run daily-post.yml --repo Warriorlegacy/Autogram
```

---

## 7. How It Works Behind the Scenes

```
[cron-job.org / External Scheduler]
         │ (Exact-second scheduled HTTP POST)
         ▼
[GitHub API: /repos/Warriorlegacy/Autogram/dispatches]
         │
         ▼
[.github/workflows/daily-post.yml triggers on `repository_dispatch`]
         │
         ├── 1. Spins up clean Ubuntu runner
         ├── 2. Acquires live sources (RSS / Hacker News)
         ├── 3. Scores topic via 6-Pillar engine
         ├── 4. Generates copy with multi-LLM chain (Gemini / Groq / CF / OpenRouter)
         ├── 5. Renders 10 JPEG slides with Chromium Playwright
         ├── 6. Uploads to high-speed CDN
         ├── 7. Publishes carousel + first-comment to Instagram live feed
         └── 8. Commits content memory to prevent topic repetition
```
