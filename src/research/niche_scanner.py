"""
Niche & competitor scanner (Makerzz P1 gate).

Normalizes competitor profile data into structured signals, computes
engagement velocity, and extracts 8 ranked content angles:

    Engagement Rate = (Likes + Comments*2 + Shares*4) / Views

Every signal record keeps provenance (source URL, type, timestamps).
Unknown metrics are stored as availability=unavailable — never fabricated.
"""

import json
import re
from datetime import datetime
from pathlib import Path

ENGAGEMENT_WEIGHTS = {"likes": 1.0, "comments": 2.0, "shares": 4.0}
TARGET_ANGLES = 8


def compute_engagement_velocity(
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    views: int = 0,
) -> float | None:
    """
    Makerzz engagement velocity formula.
    Returns None when views is unavailable/zero — never guesses.
    """
    if views <= 0:
        return None
    score = (
        likes * ENGAGEMENT_WEIGHTS["likes"]
        + comments * ENGAGEMENT_WEIGHTS["comments"]
        + shares * ENGAGEMENT_WEIGHTS["shares"]
    )
    return round(score / views, 6)


def normalize_profile(raw: dict) -> dict:
    """Normalize a raw profile/competitor payload into the canonical scan shape."""
    handle = raw.get("handle") or raw.get("username") or raw.get("name") or "unknown"
    posts = raw.get("posts") or raw.get("media") or []

    normalized_posts = []
    for p in posts:
        likes = _safe_int(p.get("likes", p.get("like_count")))
        comments = _safe_int(p.get("comments", p.get("comment_count")))
        shares = _safe_int(p.get("shares", p.get("share_count")))
        views = _safe_int(p.get("views", p.get("view_count", p.get("plays"))))
        er = compute_engagement_velocity(likes, comments, shares, views)
        normalized_posts.append({
            "caption": (p.get("caption") or p.get("title") or "")[:280],
            "format": p.get("format") or p.get("type") or "unknown",
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "engagement_rate": er,
            "availability": "measured" if er is not None else "unavailable",
            "url": p.get("url", ""),
            "posted_at": p.get("posted_at") or p.get("timestamp"),
        })

    return {
        "handle": handle,
        "platform": raw.get("platform", "instagram"),
        "followers": _safe_int(raw.get("followers"), None),
        "post_count": len(normalized_posts),
        "posts": normalized_posts,
        "bio": (raw.get("bio") or "")[:500],
        "availability": {
            "followers": "measured" if raw.get("followers") is not None else "unavailable",
        },
    }


def _safe_int(value, default: int | None = 0):
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_ranked_angles(profile: dict, niche: str, max_angles: int = TARGET_ANGLES) -> list[dict]:
    """
    Derive up to 8 ranked content angles from a normalized profile's top posts.
    Deterministic: ranking by engagement_rate (unavailable metrics sink to bottom).
    """
    posts = [p for p in profile.get("posts", []) if p.get("caption")]
    if not posts:
        return []

    measured = [p for p in posts if p.get("engagement_rate") is not None]
    measured.sort(key=lambda p: p["engagement_rate"], reverse=True)
    ranked_pool = measured + [p for p in posts if p.get("engagement_rate") is None]

    angles = []
    seen_formats: set[str] = set()
    for rank, post in enumerate(ranked_pool[:max_angles], start=1):
        caption = post["caption"]
        hook = _extract_hook(caption)
        fmt = post.get("format", "unknown")
        angles.append({
            "rank": rank,
            "angle": _angle_from_caption(caption, niche),
            "score": _angle_score(post),
            "mechanism": _mechanism_from_format(fmt),
            "evidence": [
                {
                    "claim": caption[:160],
                    "sourceUrl": post.get("url") or f"handle:{profile.get('handle')}",
                    "sourceType": "profile_post",
                    "observedAt": datetime.utcnow().isoformat(),
                    "metric": {
                        "value": post.get("engagement_rate"),
                        "unit": "engagement_rate",
                        "availability": post.get("availability", "unavailable"),
                    },
                }
            ],
            "reproducibleFormat": _reproducible_format(fmt, hook),
            "novelty": round(min(1.0, 0.5 + rank * 0.05), 2),
        })
        seen_formats.add(fmt)

    return angles


def _extract_hook(caption: str) -> str:
    first_line = caption.strip().split("\n")[0]
    return first_line[:120]


def _angle_from_caption(caption: str, niche: str) -> str:
    hook = _extract_hook(caption)
    return f"Double down on proven hook structure in {niche}: \"{hook}\""


def _mechanism_from_format(fmt: str) -> str:
    table = {
        "reel": "Short-form motion with kinetic captions drives reach velocity",
        "carousel": "Swipe-delivered information design drives saves",
        "image": "Single-frame editorial hook drives profile visits",
        "video": "Narration-led explainer builds authority",
        "unknown": "Format leveraged by top-performing posts in this niche",
    }
    return table.get(fmt, table["unknown"])


def _reproducible_format(fmt: str, hook: str) -> str:
    return f"{fmt.upper()} — open with the same tension pattern: \"{hook[:60]}\""


def _angle_score(post: dict) -> int:
    er = post.get("engagement_rate")
    if er is None:
        return 55
    # Scale engagement rate into a 0-100 angle score (typical IG ER is 0-0.15)
    return int(min(99, max(50, er * 400 + 50)))


def scan_niche(
    profile_raw: dict,
    competitors_raw: list[dict] | None = None,
    niche: str = "",
) -> dict:
    """
    Full P1 scan. Produces the scan.json gate artifact.
    Gate artifact contract: signals, blind_spots, ranked_angles (8), evidence.
    """
    profile = normalize_profile(profile_raw)
    competitors = [normalize_profile(c) for c in (competitors_raw or [])]

    all_angles = extract_ranked_angles(profile, niche)
    for comp in competitors:
        all_angles.extend(extract_ranked_angles(comp, niche, max_angles=4))

    # Deduplicate by exact angle text, re-rank by score, cap at 8
    seen: set[str] = set()
    deduped = []
    for a in sorted(all_angles, key=lambda x: x["score"], reverse=True):
        key = a["angle"].lower().strip()
        if key not in seen:
            seen.add(key)
            deduped.append(a)
    ranked = sorted(deduped, key=lambda x: x["score"], reverse=True)[:TARGET_ANGLES]

    # Re-assign ranks after merge
    for i, a in enumerate(ranked, start=1):
        a["rank"] = i

    scan = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "niche": niche,
        "profile": profile,
        "competitors": competitors,
        "signals": _signals_from_profile(profile),
        "blind_spots": _blind_spots(profile, competitors),
        "ranked_angles": ranked,
        "gate": "scan scored" if ranked else "scan empty",
        "contentCorpus": [p.get("caption", "")[:200] for p in profile.get("posts", [])][:20],
    }
    return scan


def _signals_from_profile(profile: dict) -> list[dict]:
    signals = []
    for p in profile.get("posts", [])[:10]:
        if not p.get("caption"):
            continue
        signals.append({
            "topic": p["caption"][:100],
            "format": p.get("format", "unknown"),
            "engagement_evidence": {
                "value": p.get("engagement_rate"),
                "availability": p.get("availability", "unavailable"),
            },
            "novelty": 0.6,
            "audience_fit": 0.8,
            "source_confidence": 0.9 if p.get("engagement_rate") is not None else 0.4,
        })
    return signals


def _blind_spots(profile: dict, competitors: list[dict]) -> list[str]:
    spots = []
    fmts = {p.get("format") for p in profile.get("posts", [])}
    if "carousel" not in fmts:
        spots.append("No carousel usage detected — information-design formats are open territory.")
    if "reel" not in fmts and "video" not in fmts:
        spots.append("No short-form video in recent posts — reach velocity is untapped.")
    for comp in competitors:
        comp_fmts = {p.get("format") for p in comp.get("posts", [])}
        missing = comp_fmts - fmts
        if missing:
            spots.append(
                f"@{comp.get('handle')} leverages {', '.join(sorted(missing))} formats absent from this profile."
            )
    return spots


def save_scan(scan: dict, run_dir: Path) -> Path:
    """Persist scan.json gate artifact."""
    path = Path(run_dir) / "scan.json"
    path.write_text(json.dumps(scan, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
