# ⚡ Autogram Cloudflare Cron Dispatcher

A lightweight, 100% free Cloudflare Worker that fires exact-second cron triggers to dispatch GitHub Actions workflows without queue jitter.

---

## 1. Quick Deploy (30 Seconds via CLI)

From `d:\Autogram\cloudflare-cron-dispatcher`:

```bash
# 1. Install wrangler if not present
npx wrangler login

# 2. Add your GitHub Personal Access Token (repo scope)
npx wrangler secret put GH_PAT_TOKEN

# 3. (Optional) Set your custom webhook secret for manual calls
npx wrangler secret put DISPATCH_SECRET

# 4. Deploy worker to your Cloudflare account
npx wrangler deploy
```

---

## 2. Web Dashboard Deploy (Alternative 1-Click Method)

If you prefer not using the CLI:
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create Application**.
2. Name it `autogram-cron-dispatcher` and click **Deploy**.
3. Click **Quick Edit** and paste the code from [`src/index.js`](file:///d:/Autogram/cloudflare-cron-dispatcher/src/index.js).
4. Go to **Settings** → **Variables and Secrets**:
   - Add Secret `GH_PAT_TOKEN`: Your GitHub Token (with `repo` permissions).
   - Add Variable `GITHUB_REPO`: `Warriorlegacy/Autogram`
5. Go to **Triggers** → **Cron Triggers** → Add Cron Triggers:
   - `0 4 * * *` (09:30 AM IST)
   - `0 6 * * *` (11:30 AM IST)
   - `0 12 * * *` (05:30 PM IST)
   - `0 14 * * *` (07:30 PM IST)

---

## 3. Manual On-Demand Trigger URL

Once deployed, you can trigger a run at any time via HTTP:
```bash
curl -X POST "https://autogram-cron-dispatcher.<your-subdomain>.workers.dev/trigger?slot=carousel&secret=autogram_owner_vip_2026"
```
