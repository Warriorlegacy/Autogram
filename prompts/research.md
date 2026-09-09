# Research Synthesis Prompt

## Input
A packet of recent source records containing:
- source_title
- publisher
- published_at
- url
- excerpt
- source_type

## Task
Identify the strongest content opportunities for an Instagram audience interested in AI, technology, marketing, automation, and modern business.

## Rules
- Prefer primary and original sources.
- Treat claims from secondary sources as unverified until corroborated.
- Do not turn an announcement into a story unless there is a meaningful "why it matters".
- Look for practical implications, counterintuitive findings, important architectural shifts, and reusable frameworks.
- Avoid topics that are already saturated or duplicated in recent memory.

## Output Schema (Strict JSON only)
```json
{
  "candidates": [
    {
      "topic": "Concise topic title",
      "angle": "Specific, opinionated take or mechanism",
      "pillar": "AI|Tech|Marketing|Founder",
      "why_now": "Why this matters today",
      "reader_benefit": "What the reader can do or understand after reading",
      "evidence_strength": 0.0,
      "novelty_score": 0.0,
      "save_share_score": 0.0,
      "practicality_score": 0.0,
      "saturation_risk": 0.0,
      "overall_score": 0.0,
      "sources": ["url1", "url2"]
    }
  ]
}
```
