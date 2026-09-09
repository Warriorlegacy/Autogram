# Caption Writer Prompt

## Goal
Write an engaging, premium Instagram caption for the finished carousel.

## Constraints
- First 2 lines (~125 characters) must stand alone before the "more" truncation.
- 120–220 words total.
- Add real context, backstory, or technical nuance not duplicated word-for-word on slides.
- Zero empty motivational filler.
- End with one clear, relevant call to action (save/share/question).
- 4–8 high-intent hashtags (mix of broad tech tags and specific topic tags). No spammy generic tags.

## Output Schema (Strict JSON only)
```json
{
  "caption": "Full caption text with paragraphs and line breaks",
  "first_two_lines": "Preview hook sentence",
  "cta": "Closing CTA",
  "hashtags": ["#AI", "#SoftwareEngineering", "#SystemDesign"]
}
```
