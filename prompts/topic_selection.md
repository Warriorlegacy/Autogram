# Topic Selection Prompt

## Task
Select exactly one winning primary topic from the candidate set, plus one backup topic.

## Optimization Criteria
1. Audience relevance (builders, tech leads, marketers).
2. Evidence quality & verifiable facts.
3. Novelty of angle (avoid recycled AI news).
4. Utility (actionable takeaway or mental model).
5. Save and share potential.
6. Clear explanation achievable within 7–10 slides.
7. Zero misinformation risk.

## Penalties
- Generic news summaries with no operational takeaway (-30).
- Unverifiable speculative claims (-40).
- Duplicate of topics covered in the last 30 days (-50).

## Output Schema (Strict JSON only)
```json
{
  "winner": {
    "topic": "Winning topic title",
    "pillar": "AI|Tech|Marketing|Founder",
    "angle": "Specific operational angle",
    "why_now": "Context reason",
    "sources": ["source_ids or urls"]
  },
  "reason": "Detailed justification why this will perform well on Instagram",
  "backup_topic": {
    "topic": "Backup topic title",
    "pillar": "AI|Tech|Marketing|Founder",
    "angle": "Operational angle",
    "sources": ["source_ids or urls"]
  }
}
```
