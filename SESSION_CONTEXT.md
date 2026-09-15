# Session Context — Multi-Platform Publishing

## Date: 2026-09-15
## Status: Active

---

## What Exists Already

The codebase has a **complete multi-platform distribution adapter system** at `src/distribution/`:

### Architecture
- **`src/distribution/base_adapter.py`** — Abstract `PublishAdapter` base class with `CanonicalPost` format
- **`src/distribution/adapters/instagram_adapter.py`** — Instagram adapter (wraps existing `src/instagram/publisher.py`)
- **`src/distribution/adapters/ayrshare_adapter.py`** — Ayrshare adapter supporting **13 platforms**

### Ayrshare Adapter Supported Platforms
| Platform | Status |
|----------|--------|
| Instagram | ✅ Already works via direct adapter |
| LinkedIn | ✅ Via Ayrshare |
| X (Twitter) | ✅ Via Ayrshare |
| Reddit | ✅ Via Ayrshare |
| YouTube | ✅ Via Ayrshare |
| TikTok | ✅ Via Ayrshare |
| Facebook | ✅ Via Ayrshare |
| Threads | ✅ Via Ayrshare |
| Pinterest | ✅ Via Ayrshare |
| Bluesky | ✅ Via Ayrshare |
| Telegram | ✅ Via Ayrshare |
| Discord | ✅ Via Ayrshare |
| Google Business | ✅ Via Ayrshare |

### How to Enable Multi-Platform Publishing

1. **Get Ayrshare API key** from https://ayrshare.com (free tier available)
2. **Add to `.env`:**
   ```
   AYRSHARE_API_KEY=your_key_here
   ```
3. **Connect social accounts** in the Ayrshare dashboard (LinkedIn, X, Reddit, etc.)
4. **Publish via adapter:**
   ```python
   from src.distribution import get_adapters
   from src.distribution.base_adapter import CanonicalPost

   adapters = get_adapters()
   ayrshare = adapters["ayrshare"]

   post = CanonicalPost(
       format="reel",
       caption="Check out our latest 3D website build!",
       media_urls=["https://cdn.example.com/reel.mp4"],
       metadata={"platforms": ["linkedin", "x", "reddit", "instagram"]}
   )

   result = ayrshare.publish(post)
   ```

### Current Pipeline Publishing Flow
- `scripts/pipeline_hindi_promo.py` → publishes to Instagram only via `src.instagram.publisher`
- `scripts/pipeline_reels.py` → publishes to Instagram only
- `scripts/pipeline_carousel.py` → publishes to Instagram only
- `orchestrator.py` → publishes to Instagram only

### To Add Multi-Platform to Any Pipeline
After the existing Instagram publish call, add:
```python
from src.distribution import get_adapters
from src.distribution.base_adapter import CanonicalPost

adapters = get_adapters()
post = CanonicalPost(
    format="reel",  # or "carousel", "story", "short"
    caption=caption,
    media_urls=[video_url],
    metadata={"platforms": ["linkedin", "x", "reddit"]}
)
result = adapters["ayrshare"].publish(post)
```

### Key Files
- `src/distribution/__init__.py` — Adapter registry
- `src/distribution/base_adapter.py` — Abstract base + CanonicalPost
- `src/distribution/adapters/ayrshare_adapter.py` — Multi-platform dispatch
- `src/distribution/adapters/instagram_adapter.py` — Instagram-specific

### Cron Jobs (cron-job.org → GitHub Actions)
| Job | Time (IST) | Event | Handler |
|-----|-----------|-------|---------|
| Signhify Reel 1 | 10:30 AM | publish-reel | daily_reels.yml |
| Signhify Carousel | 12:30 PM | publish-carousel | daily_carousel.yml |
| Signhify Hindi 1 | 1:30 PM | publish-hindi | daily_hindi_promo.yml |
| Signhify Reel 2 | 2:30 PM | publish-reel | daily_reels.yml |
| Signhify Reel 3 | 8:30 PM | publish-reel | daily_reels.yml |
| Signhify Hindi 2 | 9:30 PM | publish-hindi | daily_hindi_promo.yml |

### Recent Changes (2026-09-15)
- Created `daily_hindi_promo.yml` GitHub Actions workflow
- Updated `setup_signhify_cronjobs.py` with Hindi promo slots
- All 6 cron jobs active on cron-job.org
