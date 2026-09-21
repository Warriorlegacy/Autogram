"""CLI for the authoritative 60s Reel slot. Used by daily-video.yml and locally."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> None:
    p = argparse.ArgumentParser(description="Signhify 60s autonomous Reel slot")
    p.add_argument("--topic", default="")
    p.add_argument("--pillar", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force-template", default="", help="A|B|C|D|E")
    p.add_argument("--publish-reel", action="store_true", default=True)
    p.add_argument("--no-publish-reel", dest="publish_reel", action="store_false")
    p.add_argument("--publish-story", action="store_true", default=True)
    p.add_argument("--no-publish-story", dest="publish_story", action="store_false")
    p.add_argument("--slot", default="", help="morning|afternoon|night")
    a = p.parse_args()

    from src.content.video60_pipeline import run_60s_slot
    rep = run_60s_slot(topic_override=a.topic, pillar=a.pillar or None,
                       dry_run=a.dry_run, force_template=a.force_template,
                       publish_reel=a.publish_reel, publish_story=a.publish_story,
                       slot_hint=a.slot)
    print(f"SLOT={rep['slot_key']} STATUS={rep.get('status')} "
          f"DUR={rep.get('final_duration')} THEME={rep.get('theme')} "
          f"REMOTION={rep.get('remotion_status')} REEL={rep.get('reel_media_id')} "
          f"STORY={rep.get('story_status')}")
    if rep.get("status") == "QA_FAILED":
        sys.exit(2)


if __name__ == "__main__":
    main()
