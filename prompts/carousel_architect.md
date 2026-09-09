# Carousel Architect Prompt

## Goal
Build a cohesive, save-worthy 7–10 slide Instagram carousel around the winning topic and verified sources.
Make the reader think: "I learned something useful in under two minutes, and I want to save this for my team."

## Slide Constraints
- 7 to 10 slides total.
- Exactly one core idea per slide.
- Slide 1: 8–14 words headline, scroll-stopping, high tension or counter-intuitive claim.
- Dense slides: Maximum 28–36 words of body text.
- Include 1 compelling mechanism or analogy.
- Include at least 1 practical framework, comparison, or checklist slide.
- Slide roles / layout variants:
  - `hook`: First slide billboard
  - `standard`: Context & explanation
  - `checklist`: 3-5 bullet action items
  - `comparison`: Old way vs New way, or Approach A vs Approach B
  - `diagram`: Structured 3-step pipeline flow
  - `framework`: Structured rule or model
  - `takeaway`: Distilled summary
  - `cta`: Natural, non-manipulative call to action
- Map each factual statement to one or more `source_ids`.

## Output Schema (Strict JSON only)
```json
{
  "content_id": "IG-YYYY-MM-DD-001",
  "publication_date": "YYYY-MM-DD",
  "topic": "Topic title",
  "pillar": "AI|Tech|Marketing|Founder",
  "angle": "Operational angle",
  "hook": "Opening claim on slide 1",
  "slides": [
    {
      "slide_number": 1,
      "layout": "hook|standard|checklist|comparison|diagram|framework|takeaway|cta",
      "headline": "Slide headline",
      "body": "Slide explanation or supporting point",
      "proof_or_example": "Concrete data or company example",
      "source_ids": ["SRC-01"],
      "visual_direction": "Instruction for visual emphasis"
    }
  ],
  "caption": "120-220 word caption with front-loaded hook",
  "hashtags": ["#AI", "#TechStack", "#Automation", "#Engineering"],
  "alt_text": "Accessibility description for the carousel",
  "cta": "Specific CTA sentence"
}
```
