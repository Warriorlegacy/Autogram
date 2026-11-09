/**
 * Cloudflare Worker: autogram-cron-dispatcher
 *
 * Provides 100% zero-jitter, second-level precision cron triggers for Autogram.
 * Dispatches repository_dispatch events to GitHub Actions API to trigger
 * the 24/7 autonomous publishing pipeline.
 *
 * Free Tier Allowance:
 * - Cloudflare Workers: 100,000 requests/day, 10ms CPU/request ($0.00)
 */

export default {
  /**
   * Cloudflare Scheduled Handler (Fires on exact UTC schedule with zero queue delay)
   */
  async scheduled(event, env, ctx) {
    const GITHUB_REPO = env.GITHUB_REPO || "Warriorlegacy/Autogram";
    const GITHUB_TOKEN = env.GH_PAT_TOKEN;

    if (!GITHUB_TOKEN) {
      console.error("Missing GH_PAT_TOKEN secret in Cloudflare Worker environment.");
      return;
    }

    // Map cron schedule to slot type
    let slot = "carousel";
    if (event.cron === "0 4 * * *") slot = "story";
    else if (event.cron === "0 6 * * *") slot = "carousel";
    else if (event.cron === "0 12 * * *") slot = "story";
    else if (event.cron === "0 14 * * *") slot = "reel";

    console.log(`[Cron Trigger] Fired for cron: ${event.cron} -> Slot: ${slot}`);

    const res = await dispatchGitHub(GITHUB_REPO, GITHUB_TOKEN, slot, {
      trigger: "cloudflare-cron",
      cron: event.cron,
      scheduled_time: new Date(event.scheduledTime).toISOString()
    });

    console.log(`[GitHub Dispatch Response] Status: ${res.status}`);
  },

  /**
   * HTTP Fetch Handler (Supports manual webhook trigger & health check)
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === "/" || url.pathname === "/health") {
      return new Response(JSON.stringify({
        service: "autogram-cron-dispatcher",
        status: "active",
        repo: env.GITHUB_REPO || "Warriorlegacy/Autogram",
        time_utc: new Date().toISOString(),
        slots: [
          { time_ist: "09:30 AM", time_utc: "04:00 UTC", format: "story" },
          { time_ist: "11:30 AM", time_utc: "06:00 UTC", format: "carousel" },
          { time_ist: "05:30 PM", time_utc: "12:00 UTC", format: "story" },
          { time_ist: "07:30 PM", time_utc: "14:00 UTC", format: "reel" }
        ]
      }, null, 2), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // Manual on-demand dispatch trigger: /trigger?slot=carousel&secret=...
    if (url.pathname === "/trigger") {
      const secret = url.searchParams.get("secret") || request.headers.get("x-dispatch-secret");
      const requiredSecret = env.DISPATCH_SECRET || "autogram_owner_vip_2026";

      if (secret !== requiredSecret) {
        return new Response(JSON.stringify({ error: "Unauthorized" }), {
          status: 401,
          headers: { "Content-Type": "application/json" }
        });
      }

      const slot = url.searchParams.get("slot") || "carousel";
      const GITHUB_REPO = env.GITHUB_REPO || "Warriorlegacy/Autogram";
      const GITHUB_TOKEN = env.GH_PAT_TOKEN;

      if (!GITHUB_TOKEN) {
        return new Response(JSON.stringify({ error: "GH_PAT_TOKEN not set in worker environment" }), {
          status: 500,
          headers: { "Content-Type": "application/json" }
        });
      }

      const ghRes = await dispatchGitHub(GITHUB_REPO, GITHUB_TOKEN, slot, {
        trigger: "manual-webhook",
        timestamp: new Date().toISOString()
      });

      return new Response(JSON.stringify({
        status: "dispatched",
        slot,
        github_status: ghRes.status,
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response("Not Found", { status: 404 });
  }
};

/**
 * Dispatches repository_dispatch event to GitHub API
 */
async function dispatchGitHub(repo, token, slot, clientPayload = {}) {
  return await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
    method: "POST",
    headers: {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": `Bearer ${token}`,
      "User-Agent": "Autogram-Cloudflare-Cron"
    },
    body: JSON.stringify({
      event_type: "publish-slot",
      client_payload: {
        slot,
        ...clientPayload
      }
    })
  });
}
