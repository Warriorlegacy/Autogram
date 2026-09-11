# Makerzz.space - Reverse-Engineering Blueprint

**Source:** https://makerzz.space/
**Prepared:** September 10, 2026

## Scope

This document reverse-engineers the publicly observable product architecture and workflow of Makerzz.space at a **product and systems-design level**. It does not reproduce proprietary source code, private implementation details, credentials, or hidden backend behavior.

The key architectural takeaway is that Makerzz is best understood as an **agentic social-media operations pipeline** rather than a simple content generator: it coordinates research, strategy, generation, rendering, approvals, scheduling, publishing, and analytics through persistent state.

---

## 1. Product Model

The core lifecycle can be represented as:

```text
Social profile
    -> niche / competitor intelligence
    -> content strategy
    -> content generation
    -> rendering
    -> approval
    -> scheduling
    -> publishing
    -> analytics / learning
```

A useful 9-stage conceptual pipeline is:

```text
P0  Setup / Brief
 -> P1  Profile + Niche Scan
 -> P2  Strategy + Calendar
 -> P3  Script
 -> P4  Avatar Video
 -> P5  Edit Plan
 -> P6  Carousel
 -> P7  Schedule + Publish
 -> P8  Report
```

Each stage should create durable state/output that the next stage can validate before starting.

---

## 2. Reference Architecture

```text
                    +---------------------+
                    |    Web Application  |
                    | Studio / Calendar   |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |   Run Orchestrator  |
                    |   State Machine     |
                    +----------+----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        +-----------+    +------------+    +-------------+
        | AI Engine |    | Web/Trend  |    | Social APIs |
        |           |    | Research   |    |             |
        +-----------+    +------------+    +-------------+
              |                |                |
              +----------------+----------------+
                               |
                               v
                    +---------------------+
                    | Persistent Run Store|
                    |                     |
                    | brief               |
                    | scan                |
                    | angles              |
                    | strategy            |
                    | scripts             |
                    | prompts             |
                    | assets              |
                    | receipts            |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    | Rendering Workers   |
                    | Images / Video       |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    | Scheduler / Queue   |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    | Social Publishing   |
                    +---------------------+
```

---

## 3. Core Design Principle: Persistent State Machine

The most important architectural idea is **resumability**.

A run should have durable state such as:

```json
{
  "run_id": "run_2026_09_10_001",
  "status": "P3",
  "brand_id": "brand_123",
  "current_phase": "script",
  "approval_mode": "approve",
  "credits_reserved": 12,
  "credits_spent": 52
}
```

Phase state can be tracked independently:

```text
P0 -> completed
P1 -> completed
P2 -> completed
P3 -> waiting_for_approval
P4 -> locked
P5 -> locked
...
```

### Gate rule

A phase can start only when its predecessor's output is persisted and validated.

This prevents duplicated work and billing when long-running jobs are interrupted.

### Example: asynchronous video rendering

```text
Submit provider job
    -> save provider_job_id
    -> worker / scheduler polls job
    -> browser can close safely
    -> job state is recovered later
    -> asset is stored once complete
```

The same pattern should be used for image rendering, carousel batches, uploads, and publishing jobs.

---

## 4. Durable Run Storage

A conceptual run structure is:

```text
run/
|- brief
|- profile-read
|- blind-spots
|- angles
|- week
|- carousel/
|  |- prompts
|  `- slides/
|     |- 01.png
|     |- 02.png
|     `- ...
|- reel/
|  |- script.txt
|  `- edit-plan
|- captions
`- receipts
```

For production, the better implementation is a database plus object storage:

```text
PostgreSQL
    |- users
    |- brands
    |- social_accounts
    |- runs
    |- phases
    |- approvals
    |- content_items
    |- assets
    |- publish_jobs
    |- analytics
    `- credit_transactions

Object Storage
    |- scripts/
    |- images/
    |- videos/
    |- reports/
    `- exports/
```

The filesystem metaphor is useful for organizing artifacts, but the durable system should not depend on local ephemeral storage.

---

## 5. Content Intelligence Engine

The research layer should transform profile, niche, audience, and competitor information into ranked content opportunities.

```text
Instagram / platform profile
          +
        niche
          +
     competitors
          +
       audience
          |
          v
   Content extraction
          |
          v
  Competitor discovery
          |
          v
  Content clustering
          |
     +----+----+
     |         |
    Hooks    Topics / Formats
     |         |
     +----+----+
          |
          v
 Performance / opportunity scoring
          |
          v
     Growth angles
```

A useful output shape is:

```json
{
  "angle": "AI automation for small businesses",
  "score": 87,
  "evidence": ["...", "..."],
  "format": "carousel",
  "hook_pattern": "...",
  "audience_problem": "...",
  "recommended_cta": "..."
}
```

The engine should produce **evidence-backed opportunities**, not just a list of generic ideas.

---

## 6. Strategy Engine

The strategy layer converts intelligence into a calendar.

```text
Growth angles
Audience
Brand voice
Capacity
Platforms
Historical performance
        |
        v
  Strategy engine
        |
        +-- topic selection
        +-- format selection
        +-- frequency
        +-- platform adaptation
        +-- timing
        `-- content diversity
        |
        v
30-day content calendar
```

A database representation could be:

```text
content_calendar
|- id
|- brand_id
|- date
|- time
|- platform
|- content_type
|- angle_id
|- topic
|- status
|- content_id
`- publish_job_id
```

Posting times can include bounded randomness rather than always landing on round-minute timestamps.

---

## 7. Modular Content Generation

Avoid one giant prompt. Use specialized generation stages:

```text
Angle Generator
    -> Topic Generator
    -> Hook Generator
    -> Script Generator
    -> Caption Generator
    -> Carousel Generator
    -> Visual Prompt Generator
    -> Platform Adapter
```

### Reel output

```text
Hook
-> spoken script
-> B-roll / visual plan
-> captions
-> CTA
```

### LinkedIn output

```text
Hook
-> insight
-> example
-> analysis
-> CTA
```

### Carousel structure

```text
Slide 1 = pattern interrupt
Slide 2 = problem
Slide 3 = explanation
Slide 4 = example
Slide 5 = framework
Slide 6 = mistake / warning
Slide 7 = takeaway
Slide 8 = CTA
```

The same underlying idea should be adapted, not mechanically copied, across platforms.

---

## 8. Separate Script from Edit Plan

A particularly strong design decision is to separate literal spoken text from production instructions.

### Script

Contains only words the avatar / voice should speak.

### Edit plan

Contains timing, visuals, B-roll, captions, transitions, SFX, and other editing instructions.

Example:

```text
script.txt

"Most businesses are using AI backwards."
```

```text
edit-plan.json

0:00-0:03
Visual: creator close-up
Caption: Most businesses are using AI backwards.

0:03-0:07
Visual: workflow animation
B-roll: automation dashboard
```

Keeping stage directions out of the literal spoken script reduces unwanted speech artifacts and makes provider integrations more deterministic.

---

## 9. Rendering Architecture

Rendering should be asynchronous.

```text
API
 |
 v
Job Queue
 |
 +-- Image Worker
 +-- Video Worker
 +-- Carousel Worker
 `-- Thumbnail Worker
```

For video:

```text
Generate script
    -> validate
    -> submit provider job
    -> save provider_job_id
    -> queue / poll
    -> download finished asset
    -> store asset
    -> create asset record
    -> phase = COMPLETE
```

Workers should be idempotent wherever possible.

---

## 10. Approval System

A high-quality automation system should allow control per stage instead of a single all-or-nothing autopilot toggle.

Example:

```json
{
  "scan": "approve",
  "strategy": "approve",
  "script": "auto",
  "avatar": "auto",
  "edit": "approve",
  "carousel": "approve",
  "publish": "approve"
}
```

This lets a user gradually increase automation as confidence grows.

---

## 11. Credit Ledger

Credits should be represented by an append-only transaction ledger, not only a mutable balance.

```text
credit_transactions
|- id
|- user_id
|- run_id
|- type
|- action
|- amount
|- balance_after
|- provider_cost
`- created_at
```

Example:

```text
+500  PURCHASE
 -40  NICHE_SCAN
 -12  SCRIPT
 -30  CAROUSEL
 -24  SLIDE_RENDER
----------------
 394  BALANCE
```

Before expensive operations, the system should quote the expected cost, reserve or authorize the spend, and then record the actual transaction.

---

## 12. Social Publishing Abstraction

Do not build the core product around one monolithic publisher.

Use a provider interface:

```typescript
interface SocialProvider {
  connect();
  disconnect();
  validate();
  uploadMedia();
  createPost();
  schedulePost();
  getPost();
  getAnalytics();
}
```

Provider adapters can then support:

```text
InstagramProvider
TikTokProvider
YouTubeProvider
LinkedInProvider
FacebookProvider
ThreadsProvider
XProvider
PinterestProvider
...
```

The abstraction is important because platform APIs differ in media requirements, scheduling, permissions, analytics, and publishing behavior.

---

## 13. Scheduler and Publishing Reliability

Publishing should use explicit job states:

```text
scheduled
   -> publishing
   -> published
```

Failure path:

```text
scheduled
   -> publishing
   -> failed
   -> retry
```

Use an idempotency key such as:

```text
brand_id + content_id + platform + scheduled_slot
```

This helps prevent duplicate posts when workers retry after uncertain provider responses.

---

## 14. Analytics and Learning Loop

The system becomes much more valuable when analytics feed the next strategy cycle.

```text
Platform APIs
     |
     v
Analytics collector
     |
     v
Normalized metrics
     |
     v
Performance analyzer
     |
     v
What worked / why
     |
     v
New hypotheses
     |
     v
Next content calendar
```

Normalized metrics may include:

```text
views
likes
comments
shares
saves
followers
watch_time
engagement_rate
clicks
```

Only report metrics that are actually returned by the connected platform or otherwise verifiably sourced.

---

## 15. MVP Recommendation

Do not launch with every platform.

A practical first release is:

```text
Instagram + LinkedIn
```

Core flow:

```text
Account connection
    -> profile analysis
    -> competitor research
    -> content strategy
    -> 30-day calendar
    -> daily content
    -> carousel generation
    -> reel script
    -> image / video generation
    -> approval
    -> automatic publishing
    -> analytics
    -> learning loop
```

Add additional platforms later through provider adapters.

---

## 16. Recommended Technology Stack

### Frontend

```text
Next.js
React
TypeScript
Tailwind CSS
```

### Backend

```text
Next.js API routes / Node.js
TypeScript
```

### Data

```text
PostgreSQL
Prisma
Redis
BullMQ
```

### Storage

```text
S3-compatible object storage
```

### Auth / payments / monitoring

```text
Auth provider (e.g. Clerk or Auth.js)
Stripe
Sentry
```

### AI / rendering

```text
LLM API
Web research / search API
Image generation provider
Avatar / video generation provider
```

### Deployment

```text
Vercel or equivalent web hosting
Dedicated worker infrastructure for long-running jobs
```

---

## 17. Suggested Codebase Structure

```text
/apps
  /web
  /worker

/packages
  /ai
  /content-engine
  /strategy-engine
  /social
  /rendering
  /scheduler
  /billing
  /analytics
  /storage
  /shared

/database
  schema.prisma

/infrastructure
  queues
  cron
```

---

## 18. Domain Model

```text
User
 `- Brand
     |- SocialAccount
     |- BrandVoice
     |- Competitor
     |- ContentStrategy
     |- Calendar
     |- Content
     |    |- Script
     |    |- Caption
     |    |- Carousel
     |    `- Video
     |- Run
     |    `- Phase
     |- PublishJob
     `- Analytics

User
 `- CreditAccount
      `- CreditTransaction
```

---

## 19. What to Copy vs. Improve

### Strong concepts to reproduce

- Persistent state machine
- Phase gates
- Resume-able runs
- Approval per stage
- Append-only credit ledger
- Separate script and edit plan
- Asynchronous rendering
- Idempotent publishing
- Real analytics only
- Provider abstraction
- Run history
- Cost visibility before expensive actions

### Concepts to improve rather than copy literally

- Start with fewer platforms
- Do not copy exact pricing
- Do not depend on a local filesystem for durability
- Do not copy proprietary prompts
- Do not copy exact UI wording
- Build your own ranking and competitor-scoring logic
- Build platform adapters around official API capabilities

---

# 20. Tailored Architecture for an AI / Tech / Marketing Instagram

For an automated content brand in AI, technology, and marketing, the system can be specialized around a permanent **Brand Brain** and a continuously refreshed **Trend Intelligence** layer.

```text
                     YOUR BRAND
                         |
                         v
                +----------------+
                |  Brand Brain   |
                | niche / voice  |
                | audience / goal|
                +-------+--------+
                        |
                        v
              +---------------------+
              | Trend Intelligence  |
              | AI + Tech +         |
              | Marketing           |
              +----------+----------+
                         |
                         v
                  CONTENT ENGINE
                         |
            +------------+------------+
            |            |            |
            v            v            v
          REELS      CAROUSELS      POSTS
            |            |            |
            +------------+------------+
                         |
                         v
                   QUALITY GATE
                         |
                         v
                  APPROVAL / AUTO
                         |
                         v
                     INSTAGRAM
                         |
                         v
                     ANALYTICS
                         |
                         v
                   LEARNING LOOP
                         |
                         +-----------> next content
```

The automation should behave like an **operator / state machine**, not a single giant prompt.

---

## 21. Bottom Line

The most reusable insight from reverse-engineering Makerzz is not a particular AI model or visual template. It is the orchestration pattern:

```text
Research
  -> strategy
  -> generation
  -> deterministic artifacts
  -> asynchronous rendering
  -> approval gates
  -> idempotent publishing
  -> analytics
  -> learning
  -> next cycle
```

That architecture is suitable for building a robust automated social-media operating system and can be specialized for a single Instagram brand before expanding into a multi-platform SaaS.

---

## Reference

Public product site: https://makerzz.space/

This document is an architectural/product reverse-engineering based on publicly observable behavior and documentation. It should not be treated as a statement of Makerzz's private source-code implementation.
