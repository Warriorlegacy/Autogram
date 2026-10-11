# Video Studio — Instagram Reels Publishing

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/08_INSTAGRAM_PUBLISHING.md` |
| **Date** | 2026-10-11 |
| **Status** | **SPECIFICATION ONLY — NOT IMPLEMENTED, NOT AUTHORIZED** |
| **API** | Meta Graph API **v26.0** |
| **Companions** | `07_VIDEO_QUALITY_CHECKLIST.md`, `04_COSTS_AND_LICENSING.md` |

---

## 0. Status, Plainly

> ### Publishing does not exist in `video_studio`, and nothing is authorized to send anything to Instagram.
>
> - `video_studio/publish.py` **produces a package. It never publishes.** The module docstring says so: *"Publishing is NEVER done here."*
> - There is **no `--publish` flag**. `cli.py` defines four subcommands — `build`, `render`, `qa`, `package` — and none of them contacts a network.
> - Every artifact carries `"publishing": {"enabled": false, "reason": "opt-in via --publish; never default"}`. That value is **hardcoded** at `publish.py:67`.
> - No `video_studio` module imports `requests`, reads a token, or opens a socket.
>
> **This document is the specification for that future step.** Read it before writing a line of it.

| Capability | State | Where |
|---|---|---|
| Produce `reel.mp4`, `cover.jpg`, `captions.srt`, `caption.txt`, `asset_manifest.json` | **[I]** | `video_studio/publish.py` |
| Obtain a public HTTPS URL for the video | **[N]** | The real blocker — §6 |
| `POST /{ig-user-id}/media` with `media_type=REELS` | **[I]** for the legacy carousel pipeline only | `src/instagram/publisher.py:275` |
| Poll `GET /{ig-container-id}?fields=status_code` | **[I]** legacy only | `publisher.py:93` |
| `POST /{ig-user-id}/media_publish` | **[I]** legacy only | `publisher.py:141` |
| Wire the Reel flow into `video_studio` | **[N]** | Not written |
| Cover image upload / `cover_url` | **[N]** | Not implemented anywhere for Reels |
| Scheduled publishing of Reels | **[N]** | The legacy scheduler handles carousels only |

The legacy `src/instagram/publisher.py` already implements the full Reel container flow with a dry-run mode. It is **not wired into `video_studio`** and has never published a Reel. Reusing it is the obvious first move; §6 lists what it still lacks.

---

## 1. Prerequisites

### 1.1 Account type — non-negotiable

| Requirement | Detail |
|---|---|
| **Instagram Professional account** | Business **or** Creator. A **personal account cannot publish** through the API |
| **Facebook Page linked** | The professional account must be connected to a Page |
| **Page Publishing Authorization** | Must be complete where Meta requires it |

An account that is not Professional fails at step 1 with an opaque permission error. Verify before writing any code.

### 1.2 Permissions

| Auth path | Scopes |
|---|---|
| **Facebook Login** | `instagram_basic` · `instagram_content_publish` · `pages_read_engagement` |
| **Instagram Login with Facebook** | `instagram_business_basic` · `instagram_business_content_publish`, on `graph.instagram.com` |

### 1.3 Technical preconditions

| # | Requirement | Verified state |
|---|---|---|
| 1 | **Public HTTPS URL** for `video_url` — Meta's servers must fetch the file themselves | **[N]** not solved. The real blocker |
| 2 | Video conforms to Reels specs | **[I]** 1080×1920, 30 fps, H.264, 40.5 s |
| 3 | Non-zero file size | **[I]** 2,213,568 bytes |
| 4 | Token with the right scopes | **[N]** not configured for Reels |
| 5 | Professional account | **UNVERIFIED** — no data obtainable |

### 1.4 Reels format constraints

| Constraint | Value | Reference artifact |
|---|---|---|
| Aspect | 9:16 vertical | 9:16 ✔ |
| Resolution | **1080 × 1920 recommended**, min 540 × 960 | 1080 × 1920 ✔ |
| Frame rate | 24–60 fps | 30 ✔ |
| Duration | **3–90 s** | 40.5 ✔ |
| Video codec | H.264 | h264 ✔ |
| Pixel format | `yuv420p` | yuv420p ✔ |
| Audio codec | AAC (when present) | no audio track — permitted |
| Carousels | **Reels cannot appear in carousels** | n/a |
| Alt text | **Not supported** on Reels or Stories | do not rely on it for accessibility |
| Stickers | Not supported | n/a |

The reference artifact satisfies every hard constraint. **No format work is required before publishing is attempted.**

---

## 2. The Publish Flow

Three calls. Container → poll → publish. The container step is asynchronous: `POST /media` returns immediately with an id that is **not** yet a post.

### 2.1 Step 1 — Create the container

```
POST https://graph.facebook.com/v26.0/{ig-user-id}/media
```

| Parameter | Value | Required |
|---|---|---|
| `media_type` | `REELS` | **yes** |
| `video_url` | **public HTTPS URL** | **yes** |
| `caption` | up to 2,200 characters | no |
| `cover_url` | public HTTPS URL of a cover image | no |
| `share_to_feed` | `true` | no |
| `thumb_offset` | ms into the video for the thumbnail frame | no |
| `access_token` | user or system user token | **yes** |

Response:

```json
{ "id": "<container-id>", "uri": "https://graph.facebook.com/v26.0/<container-id>" }
```

`id` is a **container id**, not a media id. Nothing is published yet.

### 2.2 Step 2 — Poll until the container is ready

```
GET https://graph.facebook.com/v26.0/{container-id}?fields=status_code,status
```

| `status_code` | Meaning | Action |
|---|---|---|
| `IN_PROGRESS` | Meta is fetching and processing the video | keep polling |
| `FINISHED` | Ready to publish | proceed to step 3 |
| `ERROR` | Processing failed | inspect `status`; do not retry blindly |
| `EXPIRED` | Container aged out | create a new one; do not publish |

**Containers expire 24 h after creation.** A container that is not published in time is dead and must be recreated.

Polling parameters used by the legacy client (`publisher.py:93`): **5-second interval, 600-second ceiling for Reels** (`wait_until_ready(container_id, timeout_s=600)`), raising `RuntimeError` on `ERROR`/`EXPIRED` and `TimeoutError` on overrun.

For a 40.5 s, 2.2 MB MP4, processing should complete in well under 600 s. The ceiling exists for large files, not this one.

### 2.3 Step 3 — Publish

```
POST https://graph.facebook.com/v26.0/{ig-user-id}/media_publish
```

| Parameter | Value |
|---|---|
| `creation_id` | the container id from step 1 |
| `access_token` | the same token |

Response:

```json
{ "id": "<media-id>" }
```

That `id` is the **published media id**. Log it.

### 2.4 Sequence, complete

```
   video_studio/output/<slug>/reel.mp4
              │
              ▼
   [ UNAUTHORIZED — human decision ]  publishing.enabled is false
              │
              ▼
   upload to a public HTTPS host  ── NOT IMPLEMENTED
              │  video_url
              ▼
   POST   /v26.0/{ig-user-id}/media          → container_id
              │
              ▼
   GET    /v26.0/{container-id}?fields=status_code
              │  poll every 5 s, ceiling 600 s
              ▼  status_code == FINISHED
   POST   /v26.0/{ig-user-id}/media_publish  → media_id
              │
              ▼
   log media_id · record result · never retry the publish on ambiguity
```

### 2.5 Readback trap

**`media_type` reads back as `VIDEO` after publish, not `REELS`.**

Any verification code that asserts `media_type == "REELS"` on a published Reel will fail on a publish that actually succeeded. Assert on `VIDEO`.

---

## 3. Rate Limits

| Limit | Value | Source |
|---|---|---|
| Published posts | **50 / rolling 24 h** | Endpoint reference + quota field doc |
| Published posts | 100 / rolling 24 h | Content publishing guide |
| Container creation | **400 / rolling 24 h** | Official |
| Container expiry | **24 h** after creation | Official |
| Live query | `GET /{ig-id}/content_publishing_limit?fields=quota_usage` | Official |

> **Meta's own documentation contradicts itself on the post limit** — the content publishing guide says 100, the endpoint reference and quota field doc say 50.
>
> **Design against 50. Treat 100 as unavailable.** The legacy publisher already takes the conservative reading and hard-caps at 24 (`publisher.py:148-157`) with the comment *"Meta allows ~25 publishes/24h; 24 armed drops/day."*

| Scenario | Against a 50/24 h design limit |
|---|---|
| 7 Reels/day | ~7 headroom per day. Adequate |
| One burst of retries | A single retried publish loop can burn the **400/day container budget** for a whole day |
| Query before publishing | `check_publishing_limit()` — the legacy client does this and **raises rather than publishing** when usage ≥ 24 |

**Operational rule:** create a container once. If the poll times out, query the container status before creating another. A retry loop that recreates containers is how a day's budget disappears.

---

## 4. Cover Image Handling

The reference Reel already produces a dedicated cover:

| Property | Value |
|---|---|
| File | `video_studio/output/<slug>/cover.jpg` |
| Extracted at | **t = 0.9 s** (`publish.py:35`, `extract_cover(video, cover, at=0.9)`) |
| Size | 97,357 bytes |
| Quality | `-q:v 2` (high JPEG quality) |
| Rationale | *"A clean thumbnail: a clean hero frame, not a mid-transition mush."* |

t = 0.9 s is inside scene 1 (`hook`, 0–4.0 s) and past the 0.42 s fade-in — so it lands on a settled hero frame, not a transition.

**Two paths to attach it:**

| Path | Mechanism | State |
|---|---|---|
| `cover_url` on `POST /media` | Meta fetches an image from a public URL | **[N]** — needs the same public-hosting answer as `video_url` |
| `thumb_offset` on `POST /media` | Milliseconds into the already-hosted video | **[N]** — requires only `video_url`, no second upload. **The cheaper option** |

If `cover_url` is used, it must be a **public HTTPS URL**. A `file://` path or a local path fails silently at best.

---

## 5. Caption and Hashtag Packaging

`publish.py:build_caption` produces `caption.txt`:

```
I typed one sentence. A website built itself.

One Prompt. A 3D Website. — built from a single prompt.

#signhifystudio #vibecoding #ai3d #webdev #buildinpublic #startupindia

Follow @signhify.studio for more
```

| Component | Source | Editable where |
|---|---|---|
| Line 1 | `brief.hook` | the brief |
| Line 2 | `brief.title` + fixed `" — built from a single prompt."` | `publish.py:47` |
| Hashtags | `HASHTAGS` module constant | `publish.py:15` |
| Line 4 | `brief.cta` | the brief |

Caption constraints:

| Rule | Value |
|---|---|
| Max length | 2,200 characters |
| Hashtag count | Current set is 6. 3–5 typically performs better on a technical account; **no data exists to tune this** — the Instagram profile was auth-walled |
| CTA | **One action.** The default ladder rung 0 is `Comment "BLUEPRINT" or "FOSS"` |
| Banned phrases | Enforced on `title`/`hook`/`cta` at build time (exit 3). **Not** enforced on hashtags |
| Alt text | **Not supported** on Reels |

The CTA ladder — comment-first, link second, never price-hop — is in `02_BRAND_AND_CONTENT_STRATEGY.md` §10.

**Do not claim performance.** No follower count, engagement rate, or retention figure exists for this account. `instagram.com/signhify.studio` was blocked by an auth wall at research time. Any post implying otherwise is fabricated.

---

## 6. Required Safety Properties

These are **requirements on the future implementation**, not descriptions of existing code.

### 6.1 Disabled by default — non-negotiable

```python
# publish.py:67 — the flag is written, never read
"publishing": {"enabled": False, "reason": "opt-in via --publish; never default"}
```

A future publisher must:

| # | Property | Requirement |
|---|---|---|
| 1 | **Disabled by default** | No network call without an explicit opt-in flag. The package already carries `enabled: false` |
| 2 | **Explicit opt-in flag** | `--publish` on a subcommand, or a separate `publish` subcommand. Never implied by a successful render |
| 3 | **No token in source** | Read from environment only. Never a literal, never a default, never a fallback |
| 4 | **No token in logs** | Redact `access_token` from every logged URL and payload. `publisher.py` currently puts it in the query string of every request |
| 5 | **No token committed** | `.env` is gitignored. `.env.example` holds empty placeholders only |
| 6 | **Dry-run / preview mode** | Resolve credentials, validate the payload, print the plan — make zero network calls. The legacy `dry_run` property is the pattern |
| 7 | **Log the media id** | The published `id` is the only durable proof the post exists. Log it with the slug |
| 8 | **Record the result** | Append to a publish log: slug, media id, timestamp, caption hash. This is the audit trail |
| 9 | **Bounded retries** | Max 2 publish attempts. Poll retries: re-query the container, **never** create a new one blindly |
| 10 | **Fail closed** | Any ambiguity — timeout, unknown status, non-JSON response — stops the publish. A gate that can be bypassed is not a gate |
| 11 | **Quota check first** | `GET /content_publishing_limit` before creating a container. Refuse rather than be rejected |
| 12 | **Human in the loop** | Publishing is a distribution decision, not a build step. A green render must not auto-post |

### 6.2 Credentials — placeholder names only

From `.env.example`. **Never place a real value in a tracked file. Never paste a token into a terminal transcript, an issue, or a commit.**

```
IG_USER_ID=
IG_ACCESS_TOKEN=
META_API_VERSION=
INSTAGRAM_BUSINESS_ACCOUNT_ID=
META_GRAPH_ACCESS_TOKEN=
```

| Name | Purpose | Consumed by |
|---|---|---|
| `IG_USER_ID` | The Instagram professional account id (`{ig-user-id}` in every call) | `src/config.py:56` → `settings.ig_user_id` |
| `IG_ACCESS_TOKEN` | Graph API access token | `src/config.py:57` → `settings.ig_access_token` |
| `META_API_VERSION` | Graph API version | `src/config.py:58` → `settings.meta_api_version` |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Spec alias for the account id | `.env.example` |
| `META_GRAPH_ACCESS_TOKEN` | Spec alias for the token | `.env.example` |

> ### Version drift — resolve before any publish
>
> `.env.example` and `src/config.py:58` both pin **`META_API_VERSION=v23.0`**. This document is written against **v26.0**. `publisher.py:23` builds `base_url` as `{graph_host}/{self.version}`, so the configured version wins at runtime.
>
> Verify v23.0 still exposes the Reels endpoints used above. If not, update the pin. **Do not change it in a commit that also publishes.**

### 6.3 Dry-run is the repo default

`src/config.py:92` — `dry_run: bool = Field(default=True, alias="DRY_RUN")`.

And `publisher.py:31`:

```python
return settings.dry_run or not (self.user_id and self.token)
```

Three independent conditions force dry-run: the flag is on, **or** the user id is missing, **or** the token is missing. Publishing cannot happen by omission. `AGENTS.md` records the corollary: **changing `.env` requires restarting the dashboard**, because `DRY_RUN` is read at launch.

---

## 7. The Real Blocker: Public HTTPS

**Everything above is implemented. This is not.**

Meta's `media` endpoint fetches the video itself from `video_url`. The file must be reachable from the public internet over HTTPS.

| State | Detail |
|---|---|
| Where the file is now | `D:\Autogram\video_studio\output\<slug>\reel.mp4` — a local path. Not reachable |
| Why it matters | This is the **hard** integration constraint, not a compute one |
| Existing candidate | `src/storage/uploader.py` — an S3/R2 → free-CDN cascade already used by the carousel pipeline. **UNVERIFIED** whether it serves a 2.2 MB MP4 over stable public HTTPS |
| Note | `freeimage.host`'s API key is hardcoded in `src/storage/uploader.py` (`6d207e02198a847aa98d0a2a901485a5`). It is a public free-tier key. Do not rely on it for anything that matters |

Resolve this **before** writing any publish code. A publisher that builds containers and cannot reach the video burns the 400/day container budget on every failed attempt.

---

## 8. Implementation Sketch

Only if §7 is solved, only with explicit opt-in, only behind dry-run.

```python
# video_studio/publish.py  —  NOT PRESENT TODAY

def publish_reel(brief, out_dir: Path, *, confirm: bool = False,
                 dry_run: bool = True) -> dict:
    """Disabled unless confirm=True AND dry_run=False AND credentials exist."""
    if not confirm:
        raise PermissionError("publishing is opt-in; pass confirm=True")
    if dry_run:
        return {"published": False, "reason": "dry-run", "slug": brief.slug}
    # ... reuse src.instagram.publisher.InstagramPublisher.create_reel_container
    #     + wait_until_ready + publish_media
    # ... fetch video_url from the uploader cascade
    # ... log the media id, append to the publish log
```

The legacy `InstagramPublisher` already has all three calls plus dry-run:

| Method | Line | Reusable as-is |
|---|---|---|
| `create_reel_container(video_url, caption)` | `publisher.py:275` | **yes** — validates the URL is absolute http(s), `media_type=REELS`, `share_to_feed=True` |
| `wait_until_ready(container_id, timeout_s)` | `publisher.py:93` | **yes** — 5 s poll, raises on `ERROR`/`EXPIRED` |
| `publish_media(creation_id)` | `publisher.py:141` | **yes** — includes the 24/24 h fail-closed quota guard |
| `publish_reel(video_url, caption)` | `publisher.py:301` | **yes** — the whole sequence end to end |
| `check_publishing_limit()` | `publisher.py:37` | **yes** |

Gaps to close before wiring:

| # | Gap |
|---|---|
| 1 | **Public URL for `reel.mp4`** — §7 |
| 2 | **`cover_url` / `thumb_offset`** — never passed for Reels |
| 3 | **Token redaction** — the token is in the query string of every request today |
| 4 | **Publish audit log** — no `slug → media_id` record exists |
| 5 | **Scheduler wiring** — `orchestrator.py --schedule` handles carousels; Reels are not in the 7 daily slots |
| 6 | **`--dry-run` propagation** — `orchestrator.py` propagates the flag at runtime; the dashboard reads `DRY_RUN` from `.env` at launch. Both paths must be checked |

---

## 9. Pre-Publish Checklist

Run **after** `07_VIDEO_QUALITY_CHECKLIST.md` is fully signed off, and **before** the first real call.

| # | Gate | Status |
|---|---|---|
| ☐ | `07_VIDEO_QUALITY_CHECKLIST.md` complete and signed | ☐ |
| ☐ | QA verdict PASS, HyperFrames gate clean | ☐ |
| ☐ | Rendered at `standard` or `high`, not `draft` | ☐ |
| ☐ | `ffprobe` confirms 1080×1920, 30/1, h264, 3–90 s | ☐ |
| ☐ | **Every frame inspected. No defect outstanding** | ☐ |
| ☐ | Professional account (Business or Creator) confirmed | ☐ |
| ☐ | Facebook Page linked, PPA complete | ☐ |
| ☐ | Token has `instagram_content_publish` (and `instagram_basic`) | ☐ |
| ☐ | **`META_API_VERSION` reconciled with this document (v26.0)** | ☐ |
| ☐ | **Public HTTPS URL for `reel.mp4` resolves from outside the machine** | ☐ |
| ☐ | `GET /content_publishing_limit` shows room | ☐ |
| ☐ | Caption ≤ 2,200 characters, zero banned phrases | ☐ |
| ☐ | `DRY_RUN=false` **and** the dashboard restarted if applicable | ☐ |
| ☐ | Dry-run executed end to end first, output reviewed | ☐ |
| ☐ | **Human explicitly authorises the publish** | ☐ |
| ☐ | Publish log destination agreed | ☐ |

---

## 10. What Is NOT True

Stated so no downstream doc mistakes a plan for a shipped feature.

| Claim | Reality |
|---|---|
| "The pipeline publishes to Instagram" | **It does not.** No `video_studio` code makes a network call |
| "`--publish` enables publishing" | **No such flag exists.** Four subcommands: `build`, `render`, `qa`, `package` |
| "The Reel flow is wired into video_studio" | **It is not.** `src/instagram/publisher.py` is legacy carousel code, not called by `video_studio` |
| "A Reel has been published" | **None has.** The reference Reel is a local artifact |
| "Cover upload works" | **No `cover_url` or `thumb_offset` is ever sent** |
| "The scheduler posts Reels" | **It does not.** 7 daily slots are carousels |
| "Post performance is known" | **No data exists.** `instagram.com/signhify.studio` was auth-walled |
| "The limit is 100/day" | **Conflicting docs.** Design against 50 |
| "Publishing is enabled" | **`publishing.enabled` is hardcoded `false`** |

---

*Compiled 2026-10-11 from `video_studio/publish.py`, `video_studio/cli.py`, `src/instagram/publisher.py`, `src/config.py`, `.env.example`, and `ffprobe` output on the reference artifact. API behaviour is documented from the Meta sources in `01_TECHNICAL_RESEARCH.md` §9. Nothing in this document describes shipped publishing code, because there is none.*