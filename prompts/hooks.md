# Hook Generator Prompt

## Goal
Generate 20 high-converting, non-clickbait Instagram carousel hooks for this verified topic.

## Patterns to Explore
1. Surprising consequence ("We did X and unexpectedly cut Y by 40%")
2. Hidden mechanism ("The hidden reason most agent pipelines break after 3 steps")
3. Common mistake ("The prompting habit that costs engineering teams hours")
4. Before/After contrast ("Agent architecture in 2024 vs 2026")
5. Nuanced contrarian ("Why faster LLMs won't solve your latency problem")
6. Time-saving framework ("The 3-table schema for reliable agent memory")
7. Concrete metric ("How 1 caching parameter dropped API bills by 70%")

## Banned Openers
- "You won't believe..."
- "This changes everything..."
- "The future is here..."
- "In today's fast-paced world..."

## Output Schema (Strict JSON only)
```json
{
  "hooks": [
    {
      "rank": 1,
      "hook": "Specific hook headline (under 14 words)",
      "pattern": "Surprising consequence",
      "score": 95,
      "rationale": "Strong numerical tension and specific mechanism."
    }
  ]
}
```
