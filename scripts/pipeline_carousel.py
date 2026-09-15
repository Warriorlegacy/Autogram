"""
Autonomous Signhify Promo Carousel Pipeline.
Generates, renders, hosts, and publishes 1080x1350 viral promo carousels for @signhify.studio.
"""

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.auth.licensing import verify_license_gate
from src.config import settings
from src.content.hyperframes_carousel import SignhifyCarouselEngine
from src.storage.uploader import AssetUploader
from src.instagram.publisher import InstagramPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pipeline_carousel")


def run_carousel_pipeline(
    topic: str | None = None,
    dry_run: bool | None = None,
    output_base_dir: str | Path | None = None
) -> dict:
    """
    Executes the autonomous promo carousel pipeline:
    1. Enforces license gate.
    2. Renders 7 high-impact slides to 1080x1350 JPEGs.
    3. Uploads assets to free CDN cascade.
    4. Publishes carousel post to Instagram Graph API (or logs dry run).
    5. Updates content memory ledger.
    """
    # 1. License gate verification
    verify_license_gate()

    if dry_run is None:
        dry_run = settings.dry_run or os.environ.get("DRY_RUN", "true").lower() == "true"

    today_str = datetime.date.today().isoformat()
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_base_dir:
        carousel_dir = Path(output_base_dir)
    else:
        carousel_dir = REPO_ROOT / "workspace" / "promo_carousel" / f"{today_str}_{timestamp_str}"
    carousel_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting Signhify Promo Carousel Pipeline (dry_run={dry_run})...")
    logger.info(f"Output directory: {carousel_dir}")

    # 2. Render carousel slides
    engine = SignhifyCarouselEngine()
    result = engine.generate_and_render_promo_carousel(output_dir=carousel_dir, topic=topic)
    image_paths = result["image_paths"]
    caption = result["caption"]

    logger.info(f"Successfully rendered {len(image_paths)} slides.")

    # 3. Upload images via AssetUploader
    uploader = AssetUploader()
    public_urls = uploader.upload_carousel(
        image_paths=image_paths,
        publication_date=today_str,
        dry_run=dry_run,
        prefer_crawler_cdn=True
    )
    logger.info(f"Obtained {len(public_urls)} public CDN image URLs for Meta ingestion.")

    # 4. Publish to Instagram
    media_id = None
    publisher = InstagramPublisher()
    publisher.dry_run = dry_run

    try:
        alt_texts = [f"Signhify Studio 3D Web Engine Slide {i+1}" for i in range(len(public_urls))]
        media_id = publisher.publish_carousel(
            image_urls=public_urls,
            alt_texts=alt_texts,
            caption=caption
        )
        logger.info(f"Instagram carousel publication succeeded! Media ID: {media_id}")
    except Exception as e:
        logger.error(f"Failed to publish carousel to Instagram: {e}", exc_info=True)
        if not dry_run:
            raise

    # 5. Persist manifest and update content memory
    manifest = {
        "timestamp": datetime.datetime.now().isoformat(),
        "topic": result["topic"],
        "dry_run": dry_run,
        "media_id": media_id,
        "slides_count": len(image_paths),
        "local_images": image_paths,
        "public_urls": public_urls,
        "caption": caption
    }

    manifest_path = carousel_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info(f"Saved carousel manifest to {manifest_path}")

    # Update content memory ledger
    mem_file = REPO_ROOT / "data" / "content-memory.json"
    if mem_file.exists():
        try:
            mem = json.loads(mem_file.read_text(encoding="utf-8"))
            recent = mem.get("recent_posts", [])
            recent.append({
                "date": today_str,
                "topic": f"[Promo Carousel] {result['topic']}",
                "pillar": "Autonomous 3D Web Engine",
                "media_id": media_id,
                "type": "carousel"
            })
            mem["recent_posts"] = recent[-50:]  # Keep last 50
            mem_file.write_text(json.dumps(mem, indent=2), encoding="utf-8")
            logger.info("Updated content-memory.json with new promo carousel record.")
        except Exception as e_mem:
            logger.warning(f"Could not update content memory: {e_mem}")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Signhify Studio Promo Carousel Generator & Publisher")
    parser.add_argument("--topic", type=str, default=None, help="Custom carousel topic override")
    parser.add_argument("--dry-run", action="store_true", default=None, help="Run without posting to live Meta API")
    parser.add_argument("--live", action="store_true", help="Force live publishing to Instagram feed")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to store rendered images")

    args = parser.parse_args()

    dry_run = None
    if args.live:
        dry_run = False
    elif args.dry_run:
        dry_run = True

    try:
        run_carousel_pipeline(
            topic=args.topic,
            dry_run=dry_run,
            output_base_dir=args.output_dir
        )
    except Exception as e:
        logger.error(f"Carousel pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
