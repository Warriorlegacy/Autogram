---
title: "Instagram AI Autopilot"
author: "Automation Blueprint"
date: "9 September 2026"
fontsize: 10.5pt
geometry: margin=0.8in
toc: true
toc-depth: 2
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Instagram AI Autopilot
## A zero-touch system for daily AI + Tech + Marketing carousel content

**Version:** 1.0 · **Date:** 9 September 2026  
**Goal:** Generate, design, quality-check, schedule, publish, measure, and continuously improve high-value Instagram carousel posts with no routine user intervention.

> **Important:** Automation can make publishing consistent, but it cannot guarantee follower growth. Growth depends on topic-market fit, originality, retention, saves/shares, profile conversion, distribution, and sustained experimentation. The system below is designed to maximize the quality and consistency of those inputs rather than promise a specific follower outcome.

---

# 1. What You Are Building

The finished system should behave like an autonomous content team:

**Researcher → Strategist → Writer → Fact Checker → Designer → QA Editor → Scheduler → Publisher → Analyst → Optimizer**

Every day it should:

1. Pull fresh information from trusted AI, technology, business, and marketing sources.
2. Detect topics that are interesting, useful, timely, or surprising.
3. Score the ideas against your audience and previous performance.
4. Pick one primary topic and optionally one backup.
5. Build an 8-10 slide carousel.
6. Generate a strong opening hook, concise explanations, examples, takeaways, caption, CTA, and accessibility text.
7. Check factual claims against the source material.
8. Render slides using a fixed brand template so text is crisp and consistent.
9. Run automated quality checks.
10. Upload the final assets to public URLs.
11. Create Instagram media containers.
12. Publish the carousel at the configured time.
13. Log the post, topic, source set, prompt version, and creative version.
14. Later ingest performance metrics and feed the results into the next day's topic and copy decisions.

The most important design decision is **separation of responsibilities**. Do not ask one giant model call to research, write, design, fact-check, and publish everything in one step. Structured intermediate outputs make the system observable, debuggable, and much more reliable.

---

# 2. Recommended Architecture

## 2.1 Reference stack

| Layer | Recommended option | Purpose |
|---|---|---|
| Orchestrator | **n8n** | Cron, branching, retries, API calls, state transitions |
| LLM | **OpenAI API** | Research synthesis, ideation, writing, fact checking, optimization |
| Research | RSS/Atom + official blogs + selected web/news/search API | Fresh source material |
| Visual assets | Image generation API and/or stock/licensed assets | Backgrounds, illustrations, diagrams |
| Slide rendering | **HTML/CSS + Playwright/Chromium** | Pixel-consistent 1080×1350 carousel images |
| Asset hosting | **S3-compatible storage or Cloudinary** | Public URLs for Meta publishing |
| Database | **Postgres/Supabase** | Content ledger, status, metrics, prompts, experiments |
| Instagram | **Meta Instagram Platform / Content Publishing API** | Official publishing |
| Alerts | Email/Telegram/Slack | Exceptions only; routine user intervention stays at zero |
| Monitoring | n8n logs + database + optional uptime tool | Detect failures and stale workflows |

### Why this stack

n8n acts as the control plane. The LLM should generate **structured JSON**, not final pixels. A deterministic renderer should turn that JSON into the actual image files. Instagram should be treated as a publishing endpoint, not as the place where creative generation happens.

---

# 3. Why the Pipeline Should Be Structured

A reliable automation has five layers.

## Layer A - Knowledge acquisition

Fresh sources are collected before writing starts.

Preferred source hierarchy:

1. Official company/product documentation.
2. Official company engineering or research blogs.
3. Government/regulatory/standards sources when relevant.
4. Original academic papers or conference pages.
5. High-quality journalism and analyst sources.
6. Secondary commentary only when it adds context.

The system should store the URL, title, publication date, publisher, and the exact evidence snippets used for important claims.

## Layer B - Content intelligence

The system turns raw information into candidate topics and scores them for:

- Timeliness
- Audience relevance
- Practical usefulness
- Novelty
- Emotional pull
- Save/share potential
- Simplicity
- Proof availability
- Brand fit
- Saturation / likelihood that the angle feels generic

## Layer C - Creative production

The model creates a slide-by-slide narrative. The renderer handles typography and layout.

## Layer D - Distribution

The publishing workflow validates media, creates child containers, creates the carousel container, waits for readiness, and calls the publish endpoint.

## Layer E - Learning

The system compares results to historical baselines and uses those findings to alter future topic selection, opening hooks, slide density, CTAs, and posting mix.

---

# 4. Instagram API Requirements

Meta's current Instagram API supports professional accounts - businesses and creators - for publishing content. The Instagram Login setup uses scopes including `instagram_business_basic` and `instagram_business_content_publish`. The API does not support consumer/personal accounts. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

For carousel publishing, the official flow is container-based: create individual child media containers, create one carousel container referencing those children, then publish the carousel container. The carousel can contain up to **10 images, videos, or a mixture**. Meta also states that media used in publishing attempts must be hosted on a public server at the time of publication. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) and [Meta sample publishing repository](https://github.com/fbsamples/reels_publishing_apis)

Meta's current documentation collection describes an API-published post limit of **100 posts in a moving 24-hour period**, with carousels counted as one post. It also provides a `content_publishing_limit` endpoint for checking current usage. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

### Practical implication

Your automation should publish one high-quality carousel per day rather than attempting volume. One post/day is far below the documented publishing ceiling and leaves room for retries and emergency operations.

### Important media rule

Generate your carousel images into a stable public URL structure such as:

`https://cdn.example.com/instagram/2026-09-09/post-9f3a/slide-01.jpg`

Do not rely on a private local file path. Meta must be able to fetch the media when the publishing container is processed. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

---

# 5. Content Strategy for AI + Tech + Marketing

The account should feel like a **high-signal intelligence feed**, not an AI-news repost page.

## 5.1 Four content pillars

### Pillar 1 - AI that changes how people work

Examples:

- New model capabilities and what they actually enable.
- Agent workflows.
- Prompt engineering that produces measurable outcomes.
- Automation patterns.
- AI tools for founders, marketers, creators, developers, and operators.

### Pillar 2 - Technology explained simply

Examples:

- How a new infrastructure trend works.
- Why a technical shift matters commercially.
- Cloud, chips, data centers, cybersecurity, developer tools, robotics.
- “What this means in practice” explainers.

### Pillar 3 - Marketing + growth

Examples:

- Positioning.
- Behavioral psychology.
- Content strategy.
- Acquisition loops.
- Conversion frameworks.
- AI-powered marketing workflows.

### Pillar 4 - Founder/operator playbooks

Examples:

- What to automate first.
- How to build internal AI systems.
- Mistakes that waste engineering time.
- Metrics that matter.
- How to turn an idea into a repeatable system.

## 5.2 Content mix

Use a rolling distribution rather than repeating the same format:

| Format | Target share |
|---|---:|
| Breaking / timely explainer | 20% |
| Evergreen educational | 30% |
| Practical playbook | 25% |
| Contrarian insight / myth busting | 15% |
| Case study / teardown | 10% |

## 5.3 The “save-worthy” rule

Every carousel should contain at least one thing people can keep and use later:

- Checklist
- Framework
- Prompt
- Comparison table
- Decision tree
- Step-by-step process
- Mental model
- Formula
- Tool stack
- Examples

---

# 6. The Daily Content Engine

## 6.1 Daily sequence

**06:30 - Research window**

Collect the newest source material.

**06:40 - Topic scoring**

Generate 10-20 candidates, score them, eliminate weak angles.

**06:50 - Select winner**

Choose one primary topic using both content opportunity and source quality.

**07:00 - Draft**

Generate the 8-10 slide narrative.

**07:10 - Fact check**

Validate every important factual statement.

**07:15 - Creative rendering**

Build the slides.

**07:20 - QA**

Check readability, overflow, duplicate claims, unsupported statistics, awkward language, and aspect ratio.

**07:25 - Pre-publish staging**

Upload assets and create containers only when the publish schedule is close enough to fit your operational window.

**19:30 - Publish**

Publish the carousel at the configured time.

**Next day / rolling window - Analytics**

Pull post metrics and update the content intelligence database.

> Times above are examples. The system should make them environment variables so they can be changed without editing workflow logic.

---

# 7. Prompt Stack

Do not use one prompt for everything. Use role-specific prompts with machine-readable outputs.

---

## 7.1 SYSTEM PROMPT - Brand Brain

Use this as the persistent system instruction for your content-writing model.

```text
You are the editorial intelligence engine for a premium Instagram account focused on AI, technology, marketing, automation, and modern business.

MISSION
Create genuinely useful, highly shareable Instagram content that makes complex subjects feel obvious, practical, and memorable.

AUDIENCE
Founders, builders, marketers, operators, tech professionals, students, ambitious creators, and business-minded people who want practical understanding rather than hype.

BRAND POSITIONING
High-signal. Intelligent. Modern. Direct. Curious. Evidence-led. Slightly contrarian when the evidence supports it. Never fake certainty.

CONTENT PRINCIPLES
1. Teach something real.
2. Prefer original synthesis over recycled news.
3. Explain why a development matters, not merely what happened.
4. Every factual claim must be supported by a source in the research packet.
5. Never invent statistics, studies, quotes, product capabilities, dates, or company announcements.
6. Separate facts, interpretations, and predictions.
7. Avoid generic openings such as “AI is changing the world.”
8. Use concise language and concrete examples.
9. The first slide must create a curiosity gap without using clickbait deception.
10. Each subsequent slide must make the reader feel that continuing was worth it.
11. The final slide must produce a clear takeaway and a natural CTA.
12. Optimize for saves and shares, not empty engagement bait.
13. Do not overuse emojis, hashtags, or slang.
14. Never copy source wording. Synthesize it.
15. When evidence is weak, say so.

STYLE
Use short sentences. Prefer strong nouns and verbs. Remove filler. Avoid corporate jargon. Use simple analogies where they sharpen understanding. Sound confident because the reasoning is clear, not because the tone is loud.

INSTAGRAM CAROUSEL LOGIC
Slide 1: Hook / tension / surprising claim.
Slide 2: Context - why this matters.
Slide 3: Core concept explained simply.
Slide 4: Mechanism or example.
Slide 5: Practical implication.
Slide 6: Framework / comparison / checklist.
Slide 7: What people are getting wrong.
Slide 8: What to do next.
Slide 9: The distilled takeaway.
Slide 10: CTA / save / share / follow prompt.

You may use fewer than 10 slides if the topic is naturally complete earlier. Never add filler simply to hit 10 slides.
```

---

## 7.2 RESEARCH PROMPT - Source Synthesizer

```text
INPUT
You will receive a packet of recent source records. Each record may contain:
- source_title
- publisher
- published_at
- url
- excerpt
- source_type

TASK
Identify the strongest content opportunities for an Instagram audience interested in AI, technology, marketing, automation, and modern business.

RULES
- Prefer primary/original sources.
- Treat claims from secondary sources as unverified until corroborated.
- Do not turn an announcement into a story unless there is a meaningful “why it matters.”
- Look for practical implications, counterintuitive findings, important shifts, and useful frameworks.
- Avoid topics that are already saturated unless you can identify a substantially better angle.

OUTPUT ONLY JSON using this schema:
{
  "candidates": [
    {
      "topic": "",
      "angle": "",
      "pillar": "AI|Tech|Marketing|Founder",
      "why_now": "",
      "reader_benefit": "",
      "evidence_strength": 0,
      "novelty_score": 0,
      "save_share_score": 0,
      "practicality_score": 0,
      "saturation_risk": 0,
      "overall_score": 0,
      "sources": ["url1", "url2"]
    }
  ]
}
```

---

## 7.3 TOPIC SELECTION PROMPT

```text
Select exactly one winning topic from the candidate set.

Optimize for:
1. Audience relevance.
2. Evidence quality.
3. Novelty of angle.
4. Utility.
5. Save/share potential.
6. Clear explanation within 8-10 slides.
7. Low misinformation risk.

Penalize:
- Generic AI news.
- Topics requiring unsupported claims.
- Topics whose value depends entirely on breaking-news freshness.
- Topics that cannot produce an actionable takeaway.

Return JSON:
{
  "winner": {...candidate...},
  "reason": "",
  "backup_topic": {...candidate...}
}
```

---

## 7.4 CAROUSEL ARCHITECT PROMPT

```text
Build a carousel around the winning topic.

GOAL
Make the reader think:
“I learned something useful in under two minutes, and I want to save this.”

CONSTRAINTS
- 7-10 slides.
- One core idea per slide.
- Maximum 24-32 words on dense slides; preferably less.
- Slide 1: 8-14 words.
- Use one compelling example or analogy.
- Include at least one practical framework/checklist/comparison.
- Do not repeat the same point in different words.
- Include exact source URLs for every externally verifiable claim.

OUTPUT JSON:
{
  "title": "",
  "angle": "",
  "slides": [
    {
      "slide": 1,
      "type": "hook",
      "headline": "",
      "body": "",
      "proof_or_example": "",
      "source_ids": [],
      "visual_direction": ""
    }
  ],
  "caption": "",
  "cta": "",
  "alt_text": ""
}
```

---

## 7.5 FACT-CHECK PROMPT

```text
You are the final fact-checking gate.

Compare every externally verifiable claim in the draft against the provided source packet.

Classify each claim as:
- VERIFIED: directly supported by a source.
- PARTIALLY_VERIFIED: generally supported but wording is too strong.
- UNSUPPORTED: no evidence found.
- CONFLICTING: credible sources disagree.

For PARTIALLY_VERIFIED, rewrite the claim conservatively.
For UNSUPPORTED, delete it or replace it with an explicitly labeled interpretation.
For CONFLICTING, surface the uncertainty instead of choosing a convenient answer.

Also flag:
- Numbers
- Dates
- Product capabilities
- Named customer claims
- “First”, “largest”, “fastest”, “only”, or similar superlatives
- Quotes
- Predictions stated as facts

Output JSON:
{
  "pass": true,
  "claims": [
    {
      "claim": "",
      "status": "VERIFIED|PARTIALLY_VERIFIED|UNSUPPORTED|CONFLICTING",
      "source_ids": [],
      "replacement_text": ""
    }
  ],
  "required_edits": []
}
```

---

## 7.6 HOOK GENERATOR PROMPT

```text
Generate 20 Instagram carousel hooks for the same verified topic.

A great hook must create tension, curiosity, surprise, specificity, or a useful promise.

DO NOT use:
- “You won’t believe…”
- “This changes everything…”
- “The future is here…”
- empty superlatives
- deceptive bait

Hook patterns to explore:
1. Surprising consequence
2. Hidden mechanism
3. Common mistake
4. Before/after contrast
5. “Most people think X. The more accurate version is Y.”
6. Practical business implication
7. Counterintuitive metric
8. “Here is what nobody explains about X.”
9. Time-saving framework
10. “If you understand X, you can predict Y.”

Return a ranked JSON array with a score and one-sentence rationale for each hook.
```

---

## 7.7 CAPTION PROMPT

```text
Write an Instagram caption for the finished carousel.

Requirements:
- First two lines must stand alone as a strong preview.
- 120-220 words unless the topic clearly needs less.
- Add useful context not already duplicated slide-for-slide.
- No empty motivational language.
- End with one clear CTA.
- Use 3-6 highly relevant hashtags only if they add discoverability.
- Do not keyword-stuff.

Tone: intelligent, conversational, premium, practical.
```

---

## 7.8 QUALITY GATE PROMPT

```text
Evaluate the final carousel as a ruthless Instagram editor.

Score 0-100:
- Hook strength
- Clarity
- Information density
- Practical value
- Originality
- Evidence quality
- Narrative flow
- Save-worthiness
- Share-worthiness
- Visual brevity
- CTA quality

Automatic rejection rules:
- Any unsupported factual claim.
- Any obvious hallucination.
- Any slide with too much text.
- Hook is generic.
- More than one core idea per slide.
- CTA feels desperate or manipulative.
- Duplicate information.
- No clear reader benefit.

Return:
{
  "approved": true,
  "score": 0,
  "rejection_reasons": [],
  "edits": []
}
```

---

## 7.9 ANALYTICS OPTIMIZER PROMPT

```text
You are the growth scientist for an Instagram educational account.

Given the last 30-90 posts and their metrics, determine what should change next.

Do not optimize purely for likes.
Prioritize, in order:
1. Shares
2. Saves
3. Qualified profile visits / follows
4. Comments that demonstrate understanding
5. Reach
6. Likes

Segment findings by:
- Pillar
- Topic type
- Hook pattern
- Slide count
- CTA
- Posting time
- Content freshness

Return:
{
  "keep_doing": [],
  "stop_doing": [],
  "test_next": [],
  "winning_patterns": [],
  "losing_patterns": [],
  "next_week_content_mix": {},
  "hook_strategy": [],
  "design_strategy": []
}
```

---

# 8. The God-Level Daily Mega Prompt

This is the full orchestration prompt. It should receive **structured research + your brand profile + historical performance**, and return a publish-ready content package.

```text
ROLE
You are the autonomous editorial director of a premium Instagram publication about AI, technology, marketing, automation, and modern business.

MISSION
Create exactly one publish-ready Instagram carousel that teaches something genuinely useful, is evidence-led, visually scannable, and optimized for saves/shares and qualified follower growth.

INPUTS
BRAND_PROFILE:
{{brand_profile_json}}

AUDIENCE_PROFILE:
{{audience_profile_json}}

RESEARCH_PACKET:
{{research_packet_json}}

HISTORICAL_PERFORMANCE:
{{performance_summary_json}}

CONTENT_MEMORY:
{{recent_topics_and_hooks_json}}

TODAY:
{{current_date}}

PREFERRED_LANGUAGE:
English

WORKFLOW
STEP 1 - DISCOVER
Review all sources. Identify 10-20 potentially valuable topics.

STEP 2 - SCORE
Score every candidate using:
- evidence_strength
- novelty
- practical_value
- save_share_potential
- timeliness
- audience_fit
- simplicity
- saturation_risk

STEP 3 - SELECT
Choose one topic that has enough evidence and can be taught clearly in 7-10 slides.
Avoid duplicate topics from the recent content memory.

STEP 4 - FIND THE ANGLE
Do not summarize the news. Find the strongest useful interpretation:
“What changes for the reader because of this?”

STEP 5 - BUILD THE NARRATIVE
Use:
1. Hook
2. Context
3. Explanation
4. Mechanism/example
5. Implication
6. Framework/checklist/comparison
7. What people get wrong
8. Action
9. Takeaway
10. CTA

STEP 6 - WRITE
Use compact, spoken-language copy.
Avoid jargon unless you define it.
Use concrete examples.
Never invent data or quotes.

STEP 7 - FACT CHECK
Every factual statement must map to at least one source ID.
If unsupported, delete or qualify it.

STEP 8 - DESIGN DIRECTION
For each slide specify:
- visual hierarchy
- illustration idea
- icon/diagram idea
- background treatment
- typography emphasis
- whether an image is actually needed

STEP 9 - CAPTION
Write a caption that adds context instead of repeating the carousel.

STEP 10 - CTA
Choose one CTA based on content type:
- Save this framework.
- Share with a teammate/founder/marketer.
- Follow for tomorrow’s breakdown.
- Comment with a specific question.

STEP 11 - SELF-CRITIQUE
Score the content from 0-100.
Reject yourself if:
- the hook is generic
- the post is obvious
- factual confidence is low
- the reader cannot use the information
- slide text is too dense
- the topic is materially duplicated in recent posts

STEP 12 - FINALIZE
Return only the JSON package below.

OUTPUT SCHEMA
{
  "content_id": "",
  "publication_date": "YYYY-MM-DD",
  "topic": "",
  "pillar": "AI|Tech|Marketing|Founder",
  "angle": "",
  "hook": "",
  "slides": [
    {
      "slide_number": 1,
      "headline": "",
      "body": "",
      "micro_cta": "",
      "source_ids": [],
      "visual_direction": "",
      "layout": "hook|standard|diagram|comparison|checklist|takeaway|cta"
    }
  ],
  "caption": "",
  "hashtags": [],
  "alt_text": "",
  "source_list": [
    {
      "source_id": "",
      "title": "",
      "url": "",
      "publisher": "",
      "published_at": ""
    }
  ],
  "qa": {
    "score": 0,
    "approved": true,
    "notes": []
  }
}
```

### Important implementation rule

Do not pass this mega prompt raw into your publishing node and blindly publish. It is the **creative director**. Your workflow should still have separate validation nodes for JSON schema checks, source verification, image rendering, and final publishing.

---

# 9. Carousel Design System

## 9.1 Default canvas

Use a vertical 4:5 composition with a fixed pixel size of **1080 × 1350** for the design renderer.

Keep important text inside generous safe margins. Use the first slide as the visual “billboard”; make subsequent slides simpler.

## 9.2 Design tokens

Put all visual constants in one JSON or CSS file:

```json
{
  "canvas": {"width": 1080, "height": 1350},
  "spacing": {"outer": 90, "inner": 64, "gap": 32},
  "radius": 28,
  "headline_max_chars": 70,
  "body_max_chars": 220,
  "footer_height": 80,
  "brand_name": "YOUR_BRAND"
}
```

Choose your exact typography and colors once. Do not let the model freestyle the visual identity daily.

## 9.3 Slide templates

Create 6-8 deterministic templates:

**Template A - Hook**

Large headline + one visual cue + tiny source/date footer.

**Template B - Explanation**

Headline + two-column explanation.

**Template C - Diagram**

Simple flow with 3-5 nodes.

**Template D - Comparison**

Old way vs new way, or A vs B.

**Template E - Checklist**

Four to six short items with check icons.

**Template F - Framework**

Three-step or four-step process.

**Template G - Takeaway**

One bold statement + two supporting lines.

**Template H - CTA**

One simple action request.

### Rule: content model vs design engine

The LLM chooses the **template type** and supplies copy. It does not place pixels. HTML/CSS/Playwright places pixels.

This prevents:

- Tiny unreadable fonts.
- Misaligned typography.
- Inconsistent spacing.
- AI-generated text glitches.
- Brand drift.

---

# 10. Automated Image Generation and Rendering

## 10.1 Recommended method

Use AI image generation only for **visual ingredients**, not for the final text-bearing carousel slide.

For example:

- Abstract tech illustrations.
- Futuristic server imagery.
- Editorial hero images.
- Isometric diagrams when exact text is unnecessary.
- Background textures.

Then render the final slide in HTML/CSS.

## 10.2 Rendering pipeline

```text
Carousel JSON
    ↓
Template selector
    ↓
HTML generator
    ↓
CSS design system
    ↓
Playwright / Chromium
    ↓
1080×1350 PNG/JPEG
    ↓
Image validation
    ↓
Upload to CDN
```

## 10.3 Visual prompt

```text
Create an editorial-quality visual asset for an Instagram carousel about:
{{topic}}

VISUAL IDEA:
{{visual_direction}}

STYLE
Premium technology editorial, minimal, sophisticated, high contrast, modern, cinematic but not cliché, clean geometry, realistic lighting where appropriate, no UI text, no logos, no watermark, no letters unless explicitly required.

COMPOSITION
Leave a clear negative-space region for overlaid headline text.

DO NOT
- Add fake words
- Add fake logos
- Add random interface labels
- Put the final carousel copy inside the generated image

OUTPUT
One 4:5-safe visual suitable for a 1080×1350 Instagram slide background.
```

---

# 11. The n8n Workflow

## 11.1 Production workflow overview

```text
[CRON]
   ↓
[Load brand + memory]
   ↓
[Fetch fresh sources]
   ↓
[Normalize + deduplicate]
   ↓
[Research synthesis]
   ↓
[Topic scoring]
   ↓
[Topic selection]
   ↓
[Carousel generation]
   ↓
[Fact check]
   ↓
[Quality gate]
   |-- FAIL → regenerate with corrections
   +-- PASS
        ↓
[Generate supporting visuals]
        ↓
[Render HTML/CSS slides]
        ↓
[Image QA]
        |-- FAIL → adjust template / regenerate
        +-- PASS
             ↓
[Upload assets]
             ↓
[Meta child containers]
             ↓
[Meta carousel container]
             ↓
[Poll status]
             ↓
[Publish]
             ↓
[Verify + log]
             ↓
[Analytics collector]
             ↓
[Performance learning]
```

## 11.2 Suggested n8n nodes

1. **Schedule Trigger**
2. **Postgres - Load Brand Config**
3. **HTTP Request - Source Fetchers**
4. **Code - Clean/Normalize Sources**
5. **LLM - Research Synthesis**
6. **LLM - Topic Scoring**
7. **LLM - Content Architect**
8. **LLM - Fact Check**
9. **IF - Approved?**
10. **LLM - Revision** (only on failed QA)
11. **HTTP/Image API - Visual Assets**
12. **Code - Render HTML**
13. **Execute Command / HTTP - Playwright Renderer**
14. **Code - File/Dimension Validation**
15. **S3/Cloudinary - Upload**
16. **HTTP Request - Meta Child Containers**
17. **HTTP Request - Meta Carousel Container**
18. **Wait / Poll**
19. **HTTP Request - Meta Publish**
20. **Postgres - Log Publication**
21. **Scheduler / analytics workflow**

## 11.3 Retry logic

Every external operation should have:

- Timeout.
- Exponential backoff.
- Maximum retry count.
- Idempotency key / content ID where possible.
- Error classification.
- Persistent failure record.

Never let a transient API error create a duplicate post.

---

# 12. Meta Instagram Publishing Flow

The current API flow is container-based. Meta's documentation describes creating a media container, checking readiness, then calling `media_publish`; for carousels, create child containers first and then a parent carousel container. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

Below is a simplified example. Replace version/account/token placeholders with the values from your Meta app.

## 12.1 Create each child image container

```bash
curl -X POST \
  "https://graph.instagram.com/{{API_VERSION}}/{{IG_USER_ID}}/media" \
  -d "image_url={{PUBLIC_IMAGE_URL}}" \
  -d "is_carousel_item=true" \
  -d "access_token={{IG_ACCESS_TOKEN}}"
```

Store each returned container ID.

## 12.2 Create the carousel container

```bash
curl -X POST \
  "https://graph.instagram.com/{{API_VERSION}}/{{IG_USER_ID}}/media" \
  -d "media_type=CAROUSEL" \
  -d "children={{CHILD_ID_1}},{{CHILD_ID_2}},{{CHILD_ID_3}},{{CHILD_ID_4}}" \
  -d "caption={{URL_ENCODED_CAPTION}}" \
  -d "access_token={{IG_ACCESS_TOKEN}}"
```

You can reference up to 10 child items in one carousel. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## 12.3 Check container status

```bash
curl \
  "https://graph.instagram.com/{{API_VERSION}}/{{CAROUSEL_CONTAINER_ID}}?fields=status_code,status&access_token={{IG_ACCESS_TOKEN}}"
```

Wait until the container is ready.

## 12.4 Publish

```bash
curl -X POST \
  "https://graph.instagram.com/{{API_VERSION}}/{{IG_USER_ID}}/media_publish" \
  -d "creation_id={{CAROUSEL_CONTAINER_ID}}" \
  -d "access_token={{IG_ACCESS_TOKEN}}"
```

Meta's current reference examples use this two-stage container/publish architecture, with an additional child-container stage for carousels. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## 12.5 Check publishing quota

```bash
curl \
  "https://graph.instagram.com/{{API_VERSION}}/{{IG_USER_ID}}/content_publishing_limit?access_token={{IG_ACCESS_TOKEN}}"
```

Use this before publishing to prevent avoidable failures. Meta documents a rolling publishing limit and a dedicated endpoint to inspect current usage. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

---

# 13. Database and Data Model

A small Postgres database makes the automation dramatically easier to operate.

## 13.1 `brand_config`

```text
id
brand_name
positioning
audience
voice_rules
banned_phrases
preferred_ctas
design_version
posting_timezone
posting_time
created_at
updated_at
```

## 13.2 `source_records`

```text
id
source_url
title
publisher
published_at
source_type
content_hash
retrieved_at
trust_score
raw_excerpt
```

## 13.3 `content_items`

```text
id
publication_date
topic
pillar
angle
hook
content_json
caption
status
prompt_version
design_version
source_ids
created_at
published_at
instagram_media_id
```

Statuses:

```text
IDEA
DRAFTING
FACT_CHECK
DESIGNING
QA
STAGED
PUBLISHED
FAILED
RETIRED
```

## 13.4 `post_metrics`

```text
content_id
instagram_media_id
captured_at
reach
impressions
likes
comments
saves
shares
profile_visits
follows
engagement_rate
```

## 13.5 `experiments`

```text
id
content_id
variable
variant
hypothesis
result
winner
```

---

# 14. Scheduling Strategy

## 14.1 Two schedules, not one

Use two distinct automations.

### Workflow A - Production

Runs early enough to generate and QA the next post.

### Workflow B - Publishing

Runs at the exact scheduled posting time.

This separation avoids a dangerous design where a slow research or image-generation step delays your actual post.

## 14.2 Recommended operating pattern

Create content at least several hours before publication. Then stage it and publish later.

For example:

```text
06:30 - generate content
07:30 - stage assets
07:45 - finish Meta containers if operationally appropriate
19:30 - publish
19:35 - verify
```

Because media/container validity and platform behavior can change, your implementation should keep the creation-to-publish window conservative and test the exact flow in your account before relying on it at scale. Meta documents container processing/status and publishing constraints. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## 14.3 Time optimization

Do not hardcode one posting time forever. Let the analytics layer maintain a rolling estimate for:

- Best weekday.
- Best posting hour.
- Best pillar by weekday.
- Best hook style by audience segment.

Then test, for example:

```text
Week A: 19:30
Week B: 20:00
Week C: 12:30
```

Keep other variables as stable as possible when testing time.

---

# 15. Analytics and Self-Optimization

## 15.1 What to optimize for

The account's north-star signal should be **qualified attention**.

A useful hierarchy is:

**Shares + Saves → Profile Visits + Follows → Comments → Reach → Likes**

Likes are useful, but educational content often shows its value more clearly through saves and shares.

## 15.2 Rolling score

Create a normalized content score such as:

```text
Content Score =
  0.30 * Save Rate
+ 0.30 * Share Rate
+ 0.20 * Follow Conversion
+ 0.10 * Comment Rate
+ 0.10 * Reach Efficiency
```

Use your own historical baseline instead of arbitrary platform-wide numbers.

## 15.3 Avoid winner-chasing

A post can perform well because of timing, a news event, or external sharing. Do not conclude that one creative variable caused the result from a single observation.

Use rolling cohorts:

- 10 posts per pillar.
- 10 posts per hook family.
- Multiple weeks per posting-time test.

## 15.4 Automated learning loop

Every night or every 2-3 days:

1. Pull post metrics.
2. Normalize them against the account's recent baseline.
3. Group by content type.
4. Ask the analytics prompt what patterns are emerging.
5. Update `brand_config` experiments.
6. Feed those learnings into tomorrow's topic selection.

---

# 16. Quality Gates and Failure Handling

Zero-touch does **not** mean zero safeguards.

## 16.1 Hard-stop rules

Automatically block publication when:

- LLM output is not valid JSON.
- A source URL is missing for a material factual claim.
- Fact check returns unsupported/conflicting claims that were not resolved.
- The carousel contains more than 10 items.
- An image is not the expected aspect ratio.
- Image fetch/upload fails.
- Meta container processing does not reach a publishable state.
- Daily publishing quota is unexpectedly close to exhaustion.
- The content is materially duplicated from a recent post.
- The model produces unsafe, defamatory, or legally risky language.
- The design renderer reports text overflow.

## 16.2 Regeneration loop

Use bounded retries:

```text
First failure:
  explain exact issue → regenerate

Second failure:
  switch to simpler template / shorter copy → regenerate

Third failure:
  mark FAILED → do not publish
```

The safest zero-touch behavior is **fail closed**: when the system is uncertain, skip a post rather than publish a bad one.

## 16.3 Exception alert

Send an alert only for:

- repeated production failure;
- Meta publishing failure;
- database failure;
- expired credentials;
- missing source feed;
- suspiciously low posting success rate.

Routine content should require no human message.

---

# 17. Folder Structure

A clean project might look like:

```text
instagram-ai-autopilot/
|-- README.md
|-- .env.example
|-- docker-compose.yml
|-- n8n/
|   |-- workflow-daily-production.json
|   |-- workflow-publish.json
|   +-- workflow-analytics.json
|-- prompts/
|   |-- system_brand.md
|   |-- research.md
|   |-- topic_selection.md
|   |-- carousel_architect.md
|   |-- fact_check.md
|   |-- hooks.md
|   |-- caption.md
|   |-- quality_gate.md
|   +-- analytics_optimizer.md
|-- renderer/
|   |-- templates/
|   |   |-- hook.html
|   |   |-- standard.html
|   |   |-- checklist.html
|   |   +-- comparison.html
|   |-- css/
|   |   +-- design-system.css
|   |-- render.js
|   +-- validate.js
|-- src/
|   |-- research/
|   |-- content/
|   |-- instagram/
|   |-- analytics/
|   +-- db/
|-- data/
|   |-- brand.json
|   +-- content-memory.json
+-- output/
    +-- YYYY-MM-DD/
        |-- content.json
        |-- caption.txt
        |-- slide-01.jpg
        |-- slide-02.jpg
        +-- manifest.json
```

---

# 18. Environment Variables

Create an `.env` file locally or store these in your deployment platform's secret manager.

```bash
# LLM
OPENAI_API_KEY=...

# Instagram / Meta
IG_USER_ID=...
IG_ACCESS_TOKEN=...
META_API_VERSION=...

# Storage
S3_ENDPOINT=...
S3_BUCKET=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
PUBLIC_CDN_BASE=...

# Database
DATABASE_URL=...

# Scheduler
TIMEZONE=Asia/Kolkata
POSTING_TIME=19:30

# Optional alerts
ALERT_WEBHOOK_URL=...
```

Never hardcode tokens in prompts, JavaScript, HTML files, or n8n workflow JSON that is exported to source control.

---

# 19. Implementation Blueprint

## Phase 1 - Foundation

1. Create/verify an Instagram Professional account.
2. Create/configure the Meta developer application.
3. Complete the Instagram login/publishing permission setup.
4. Store the account ID and access credentials securely.
5. Verify that a single test image can be published through the official API.

Meta's current Instagram API documentation explicitly targets professional business/creator accounts for content publishing. [Meta Instagram API documentation](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## Phase 2 - Content engine

1. Stand up n8n.
2. Create the Postgres schema.
3. Add your brand profile.
4. Add source feeds.
5. Add research + topic-selection prompts.
6. Generate structured carousel JSON.
7. Add fact checking.

## Phase 3 - Design engine

1. Create 6-8 HTML/CSS slide templates.
2. Build the renderer.
3. Add font and spacing rules.
4. Add image assets.
5. Add text-overflow validation.
6. Create one sample carousel.

## Phase 4 - Publishing engine

1. Upload images to S3/Cloudinary.
2. Create child containers.
3. Create carousel container.
4. Poll readiness.
5. Publish.
6. Verify and log the returned media ID.

## Phase 5 - Self-optimization

1. Ingest performance metrics.
2. Calculate normalized scores.
3. Feed history into the analytics optimizer.
4. Store winning hooks, themes, formats, and times.
5. Use those outputs to improve future content.

---

# 20. 90-Day Content Framework

Do not let the daily generator choose random topics forever. Use a strategic learning plan.

## Days 1-30: Establish signal

Goal: discover which subjects and hooks your audience responds to.

Prioritize:

- AI explainers.
- AI tools with practical workflows.
- Marketing frameworks.
- Simple tech breakdowns.
- Founder/operator lessons.

Track every post against a hook family.

## Days 31-60: Double down

Increase the frequency of the top 20% performing topic families.

Introduce:

- More comparisons.
- More practical checklists.
- More “what this means for you” content.
- 1-2 deeper case studies each week.

## Days 61-90: Build a recognizable point of view

Move beyond news explanation into proprietary synthesis.

Examples:

- “What most AI agents get wrong.”
- “The hidden economics behind AI automation.”
- “The 5-layer AI stack I would build today.”
- “Why most AI marketing systems produce mediocre content.”
- “A framework for deciding what to automate.”

The long-term goal is not to become an AI news account. It is to become a **trusted explainer and operator-oriented intelligence brand**.

---

# 21. Operating Checklist

## Before launch

- [ ] Instagram account is Professional.
- [ ] Meta app and publishing permissions are configured.
- [ ] API publishing works for a test image.
- [ ] Public asset hosting works.
- [ ] Carousel creation works.
- [ ] Postgres database exists.
- [ ] n8n workflows are active.
- [ ] Prompts are versioned.
- [ ] Brand design system is fixed.
- [ ] Quality gates are enabled.
- [ ] Failure alerts are configured.

## Daily automated checks

- [ ] Fresh source material exists.
- [ ] Selected topic has strong evidence.
- [ ] No recent duplicate.
- [ ] Fact check passes.
- [ ] Slide count is valid.
- [ ] All images render correctly.
- [ ] Assets are public.
- [ ] Meta quota is healthy.
- [ ] Container status becomes publishable.
- [ ] Publish returns a media ID.
- [ ] Publication is logged.

---

# 22. Reference Prompts in One Place

This section is the compact copy/paste set for your implementation.

## Prompt A - Topic scorer

```text
Score each candidate topic from 0-100 for audience fit, evidence strength, novelty, practicality, save/share potential, timeliness, and saturation risk. Penalize unsupported claims and generic angles. Return strict JSON only.
```

## Prompt B - Hook engine

```text
Generate 20 non-clickbait hooks for this topic. Favor surprise, specificity, hidden mechanisms, practical consequences, mistakes, contrasts, and useful promises. Reject generic “AI is changing everything” language. Rank by curiosity + clarity + credibility.
```

## Prompt C - Carousel writer

```text
Turn this verified topic into a 7-10 slide Instagram carousel. One idea per slide. Short sentences. Slide 1 must be irresistible but truthful. Include one mechanism, one example, one actionable framework, one distilled takeaway, and one natural CTA. Map each factual claim to source IDs. Return JSON only.
```

## Prompt D - Fact checker

```text
Audit every factual statement against the supplied sources. Mark VERIFIED, PARTIALLY_VERIFIED, UNSUPPORTED, or CONFLICTING. Rewrite conservative claims where necessary. Never allow unsupported statistics, quotes, dates, or product capabilities to pass.
```

## Prompt E - Design planner

```text
For each slide, choose one layout from: hook, standard, diagram, comparison, checklist, takeaway, CTA. Specify a visual that supports the idea, not decoration. Keep the final composition simple enough to understand in 1-2 seconds while scrolling.
```

## Prompt F - Caption writer

```text
Write a premium, conversational Instagram caption of 120-220 words. Add context rather than repeating every slide. Make the first two lines strong. End with one clear CTA. Use only a few relevant hashtags when useful.
```

## Prompt G - Quality gate

```text
Act as a ruthless final editor. Score hook strength, clarity, usefulness, originality, evidence quality, narrative flow, save-worthiness, share-worthiness, and visual brevity. Reject anything generic, unsupported, repetitive, manipulative, or too dense. Return strict JSON.
```

## Prompt H - Analytics optimizer

```text
Analyze the previous 30-90 posts. Identify winning topic families, hooks, CTAs, slide structures, design patterns, weekdays, and posting times. Focus on saves, shares, profile conversion, and follows rather than likes alone. Output concrete tests for the next 7 days.
```

---

# Final Recommended System

If building this from scratch today, the production design I would use is:

**n8n + Postgres + OpenAI API + official Meta Instagram publishing API + S3/Cloudinary + HTML/CSS/Playwright renderer + scheduled analytics workflow.**

The workflow should be:

**Research → Rank → Write → Fact-check → Render → QA → Upload → Publish → Measure → Learn.**

The most important quality principle is this:

> **Automate the mechanics aggressively; automate judgment conservatively.**

In practice that means the system can run without daily human intervention, while still refusing to publish when the evidence, creative quality, or API state is not good enough.

## Sources

- Meta / Instagram API documentation collection (current): https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
- Meta sample: Reels Publishing API / carousel publishing: https://github.com/fbsamples/reels_publishing_apis

---

## Appendix: Example Daily Brand Profile

```json
{
  "brand_name": "YOUR BRAND",
  "positioning": "The practical intelligence account for AI, technology, marketing, automation, and modern business.",
  "audience": [
    "founders",
    "developers",
    "marketers",
    "operators",
    "students",
    "ambitious creators"
  ],
  "voice": [
    "intelligent",
    "clear",
    "practical",
    "modern",
    "evidence-led",
    "slightly contrarian"
  ],
  "avoid": [
    "generic hype",
    "fake urgency",
    "unsupported statistics",
    "overused motivational language",
    "keyword stuffing",
    "excessive emojis"
  ],
  "default_carousel_size": 9,
  "default_posting_time": "19:30",
  "timezone": "Asia/Kolkata"
}
```

## Appendix: Example source packet item

```json
{
  "source_id": "SRC-2026-09-09-001",
  "source_title": "Example official announcement",
  "publisher": "Official publisher",
  "published_at": "2026-09-09T08:00:00+05:30",
  "url": "https://example.com/source",
  "excerpt": "Trusted source excerpt goes here.",
  "source_type": "primary",
  "trust_score": 0.98
}
```

## Appendix: Example final content object

```json
{
  "content_id": "IG-2026-09-09-001",
  "publication_date": "2026-09-09",
  "topic": "A practical AI workflow",
  "pillar": "AI",
  "angle": "What changes operationally, not just technically",
  "hook": "The biggest AI productivity gain is not another chatbot.",
  "slides": [
    {"slide_number":1,"headline":"The biggest AI productivity gain is not another chatbot.","body":"","layout":"hook","source_ids":[]},
    {"slide_number":2,"headline":"The real shift is workflow compression.","body":"One system can remove handoffs between research, drafting, checking, and delivery.","layout":"standard","source_ids":["SRC-2026-09-09-001"]}
  ],
  "caption": "Your caption goes here.",
  "hashtags": ["#AI", "#Automation", "#Marketing"],
  "alt_text": "An educational carousel explaining an AI workflow.",
  "qa": {"score": 94, "approved": true, "notes": []}
}
```

---

**End of guide.**
