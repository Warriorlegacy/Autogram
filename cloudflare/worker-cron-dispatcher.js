/**
 * Cloudflare Worker: Autogram Zero-Jitter Cron Dispatcher
 * Dispatches GitHub Actions repository_dispatch events at the exact second
 * for 100% zero-touch 24/7 cloud publishing.
 * 
 * Free tier allowance: 100,000 requests/day (10ms CPU per request).
 */

export default {
  async scheduled(event, env, ctx) {
    const GITHUB_REPO = env.GITHUB_REPO || "Warriorlegacy/Autogram";
    const GITHUB_TOKEN = env.GH_PAT_TOKEN; // Personal Access Token with 'repo' scope

    if (!GITHUB_TOKEN) {
      console.error("Missing GH_PAT_TOKEN secret in Cloudflare Worker environment.");
      return;
    }

    // Map cron triggers to publishing slot formats
    // Crons in UTC:
    // '0 4 * * *'  -> 09:30 AM IST (story)
    // '0 5 * * *'  -> 10:30 AM IST (reel)
    // '0 6 * * *'  -> 11:30 AM IST (carousel)
    // '0 9 * * *'  -> 02:30 PM IST (reel)
    // '0 12 * * *' -> 05:30 PM IST (story)
    // '0 14 * * *' -> 07:30 PM IST (carousel)
    // '0 15 * * *' -> 08:30 PM IST (reel)
    let slotFormat = "auto";
    const cron = event.cron || "";
    if (cron.includes(" 4 ") || cron.includes(" 12 ")) {
      slotFormat = "story";
    } else if (cron.includes(" 6 ") || cron.includes(" 14 ")) {
      slotFormat = "carousel";
    } else if (cron.includes(" 5 ") || cron.includes(" 9 ") || cron.includes(" 15 ")) {
      slotFormat = "reel";
    }

    const payload = {
      event_type: "publish-slot",
      client_payload: {
        timestamp: new Date().toISOString(),
        cron: cron,
        slot: slotFormat,
        source: "cloudflare-worker-cron"
      }
    };

    const url = `https://api.github.com/repos/${GITHUB_REPO}/dispatches`;
    console.log(`Dispatching GitHub Actions: ${url} (Slot: ${slotFormat}, Cron: ${cron})`);

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Accept": "application/vnd.github.v3+json",
          "Authorization": `Bearer ${GITHUB_TOKEN}`,
          "User-Agent": "Autogram-Cloudflare-Cron-Dispatcher"
        },
        body: JSON.stringify(payload)
      });

      console.log(`GitHub API Response: HTTP ${response.status} ${response.statusText}`);
    } catch (err) {
      console.error(`Failed to dispatch GitHub Actions: ${err.message}`);
    }
  },

  async fetch(request, env, ctx) {
    // Health check endpoint or manual test trigger
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({ status: "healthy", service: "autogram-cron-dispatcher", time: new Date().toISOString() }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    if (url.pathname === "/trigger" && request.method === "POST") {
      const auth = request.headers.get("Authorization");
      if (auth !== `Bearer ${env.TRIGGER_SECRET || "autogram_owner_vip_2026"}`) {
        return new Response("Unauthorized", { status: 401 });
      }

      await this.scheduled({ cron: "manual-http-trigger" }, env, ctx);
      return new Response(JSON.stringify({ status: "dispatched", time: new Date().toISOString() }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response("Autogram Cloudflare Cron Dispatcher is Active. Endpoints: /health, /trigger", { status: 200 });
  }
};

