# Daily AI Reel — Setup

The workflow will not do anything until you add the secrets below. This is the
complete list. Nothing here is committed; `.env` is written at run time and
deleted in the same job.

## 1. Repository secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Required | Notes |
|---|---|---|
| `GROQ_API_KEY` | **yes** | Primary LLM. Free tier. Benchmarked fastest at ~3s/brief. |
| `GEMINI_API_KEY` | recommended | Second LLM. Free tier. The failover if Groq rate-limits. |
| `IG_USER_ID` | **yes** | Your numeric IG user id. `17841478609535151` for @signhify.studio. |
| `META_GRAPH_ACCESS_TOKEN` | **yes** | **The Page token.** No expiry; survives a password change. This is the whole reason your old setup died. |
| `IG_ACCESS_TOKEN` | optional | 60-day User token. Only a fallback. |
| `META_APP_ID` | recommended | Enables the 60-day exchange in `setup_meta_token.py`. |
| `META_APP_SECRET` | recommended | Same. |
| `AUTOGRAM_OWNER_KEY` | recommended | Licence gate. |

**Variables** (not secrets) — **Settings → Variables → New repository variable**

| Variable | Value | Why |
|---|---|---|
| `PUBLIC_CDN_BASE` | *(leave blank)* | The workflow uploads per-run and passes the real URL, so a fixed CDN base is not required. |

## 2. Test it before letting it publish

The workflow defaults to `dry_run: true` on manual dispatch, which generates,
renders and QAs but never publishes.

Go to **Actions → daily-ai-reel → Run workflow**:

1. Leave `topic` blank, `dry_run` = `true` → confirm it produces a Reel and passes QA.
2. Run with a topic you like and `dry_run` = `false` to publish exactly one.
3. Only after that, let the schedule run.

If you want the schedule to publish immediately, set `dry_run: false` as the
default in the `workflow_dispatch` input. It is `true` today on purpose.

## 3. Runtime cost

Each run does a full 30–55s Reel: AI brief (~4s), Kokoro narration (~30s of
synthesis), headless Chrome render, FFmpeg loudnorm, QA, upload, publish.

GitHub-hosted runners are 2-core. Budget roughly **8–15 minutes per Reel** in CI
versus ~4 on your local 8-core machine.

- **Public repo:** Actions minutes are free and unlimited.
- **Private repo:** the free tier is 2,000 minutes/month. At ~12 min × 7 Reels
  × 30 days that is **~2,520 minutes — over the free tier.** You would either
  pay, or drop to fewer slots, or make the repo public.

That arithmetic is the main thing to decide before enabling the schedule.

## 4. Known constraints

- **Public repos auto-disable scheduled workflows after 60 days without repo
  activity.** A public repo going quiet stops publishing silently.
- **GitHub cron is UTC** and can be delayed under load. The slots use `:30`
  rather than `:00` to dodge the worst of it.
- **Free file hosts expire.** The uploader tries catbox then uguu; uguu keeps
  files ~48h. Meta fetches the video within seconds, so this is fine in
  practice, but do not treat the URL as permanent.
- **`hyperframes check` runs before render.** A brief that fails brand,
  narration-fit or layout gates stops the job rather than shipping a bad Reel.

## 5. Rolling back

Turn the schedule off by disabling the workflow in the Actions tab. Nothing
else is required — there is no self-hosted runner and no always-on machine
depending on it. To test again later, re-enable and use **Run workflow**.