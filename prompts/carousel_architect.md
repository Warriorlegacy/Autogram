# Carousel Architect Prompt

## Goal
Build an exceptionally high-density, save-worthy 7–10 slide (default: 8 slides) Instagram carousel educating builders on the winning FOSS tool, GitHub repo, or self-hosted architecture.
The reader's immediate reaction must be: "This replaces a $100/mo SaaS subscription, gives me full data privacy, and runs on my machine in 60 seconds. Saving this immediately."

## 8-Slide FOSS Carousel Blueprint
1. **Slide 1 (`hook`):** Problem / SaaS Pain / Big Promise. High contrast. Example: "Stop paying $240/year for DocuSign. Here is the open source alternative you own forever."
2. **Slide 2 (`framework` / `standard`):** The Tool Introduction. Name, GitHub repo, star count, license (AGPL/MIT/Apache), core capabilities.
3. **Slide 3 (`diagram` / `framework`):** Architecture Breakdown. How it works under the hood (Docker, PostgreSQL/SQLite, reverse proxy, zero phone-home).
4. **Slide 4 (`checklist` / `framework`):** 1-Line Deployment. Concrete command (`docker run -d ...` or `docker compose up -d`) with volume persistence.
5. **Slide 5 (`comparison`):** SaaS vs. FOSS Matrix. Direct table comparison: Cost ($0 vs $X/mo), Data privacy (Self-hosted vs Cloud), Rate limits (Infinite vs Paywalled), Vendor lock-in.
6. **Slide 6 (`checklist` / `takeaway`):** Honest Trade-offs ("Proof, Not Promises"). What it takes to run: RAM footprint, backup schedule, reverse proxy SSL setup.
7. **Slide 7 (`standard` / `framework`):** Advanced Power Tip. Real-world integration (e.g., automated backups with rclone, n8n webhook triggers, or custom domain routing).
8. **Slide 8 (`cta`):** Lead Magnet & Community CTA. "Comment 'FOSS' below and I'll send the full GitHub repo link, one-click docker-compose file, and setup blueprint to your DMs."

## Slide Constraints
- 7 to 10 slides total (prefer exactly 8).
- Exactly one core idea per slide.
- Slide 1: 8–14 words headline, scroll-stopping, high tension or counter-intuitive claim.
- Dense slides: Maximum 28–36 words of body text.
- Slide roles / layout variants:
  - `hook`: First slide billboard
  - `standard`: Context & explanation
  - `checklist`: 3-5 bullet action items / commands
  - `comparison`: SaaS vs FOSS or Old vs New
  - `diagram`: Structured 3-step pipeline flow
  - `framework`: Structured architectural model or code block
  - `takeaway`: Distilled summary or trade-off analysis
  - `cta`: Natural, non-manipulative call to action with comment trigger
- Map each factual statement to one or more `source_ids`.

## Output Schema (Strict JSON only)
```json
{
  "content_id": "IG-YYYY-MM-DD-001",
  "publication_date": "YYYY-MM-DD",
  "topic": "Tool Name: Open Source Alternative to [SaaS]",
  "pillar": "FOSS SaaS Alternatives|Trending GitHub Spotlight|Local AI & Edge Compute|Developer Power Tools & CLI|Self-Hosted Architecture|Open Source Economics & Contrarian",
  "angle": "How self-hosting [Tool] eliminates vendor lock-in and monthly SaaS burn",
  "hook": "Stop paying for [SaaS]. This 100% open source repo runs on your own hardware.",
  "slides": [
    {
      "slide_number": 1,
      "layout": "hook|standard|checklist|comparison|diagram|framework|takeaway|cta",
      "headline": "Slide headline",
      "body": "Slide explanation or supporting point",
      "proof_or_example": "Concrete repo stars, benchmark, or docker command",
      "source_ids": ["SRC-01"],
      "visual_direction": "Instruction for visual emphasis"
    }
  ],
  "caption": "120-220 word caption with front-loaded hook, setup steps, and DM lead-magnet trigger",
  "hashtags": ["#OpenSource", "#SelfHosted", "#DevTools", "#Docker", "#Linux", "#FOSS"],
  "alt_text": "Accessibility description for the carousel",
  "cta": "Comment 'FOSS' to get the full GitHub repo and docker-compose blueprint."
}
```
