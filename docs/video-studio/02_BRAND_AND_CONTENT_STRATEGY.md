# Video Studio — Brand and Content Strategy

| Field | Value |
|---|---|
| **Document** | `docs/video-studio/02_BRAND_AND_CONTENT_STRATEGY.md` |
| **Date** | 2026-10-11 |
| **Brand** | Signhify Studio |
| **Format** | Vertical 9:16, 1080×1920, 30 fps, 20–60 s |
| **Source of truth** | `data/brand.json` (read directly), the live product site, 9 published carousel renders |
| **Companions** | `00_EXECUTIVE_SUMMARY.md`, `01_TECHNICAL_RESEARCH.md` |

Everything below is built on verified facts. Where a fact could not be obtained, it is recorded as a limitation in §12 rather than estimated.

---

## 1. Verified Brand Identity

### 1.1 The product

**Signhify** — a 3D scroll-reactive website builder driven by a single prompt. Site header: *"Signhify Website Builder from a Single Prompt."*

| Attribute | Verified value | Source |
|---|---|---|
| Hero headline | Type a prompt. AI generates a complete scroll-reactive site with cinematic video, imagery, and motion — publish to a live URL in minutes. | Live site, verbatim |
| Core mechanism | Generate a cinematic video (~8 s) → extract hundreds of frames → native browser scroll replays them as 3D parallax | Live site |
| Site's own line on it | "No WebGL, no Three.js, no code — just native browser scroll with buttery-smooth frame interpolation." | Live site, verbatim |
| Frame density | 400+ frames/site | Live site |
| FPS control | 10–40, adjustable | Live site |
| Pipeline stages | Pick a preset → Describe → Generate keyframe → Animate (8 s video) → Build (extract frames) → Deploy (ZIP with HTML, CSS, JS) | Live site |
| Subhead proof points | AI Plans Starting at $5/mo · 5 to 300 Credits · 3D scroll studio · 6-agent swarm · 100% MIT code ownership | Live site, verbatim |
| Footer tagline | "3D Website Builder for cinematic scroll experiences — generated from a single prompt." | Live site, verbatim |
| Positioning line | Best Vibe Coding Value Guaranteed | Live site, verbatim |

### 1.2 Pro Tools

| Tool | Site description (condensed, not embellished) |
|---|---|
| Multi-Video Continuation | Chain multiple videos end-to-end for longer scroll animations |
| Full-Stack Export | Download a ZIP with frontend + backend starter; includes an Express API |
| Iterative Chat Editing | Chat with AI to change copy, move sections, adjust colors — live |
| Product Injection | Upload product photos and tell AI where to place them directly in 3D |
| Adjustable FPS | Slide between 10–40 FPS to control frame density and scroll speed |

### 1.3 Presets

Six ship on the site today:

`Cyberpunk Kinetic Watch` · `Zenith Spatial Headset` · `Titanium EV Supercar` · `Nova AI Code Copilot` · `Orbital Quantum Compute` · `Vortex Wireless Audio`

These are content assets, not decoration. Each is a 6-second product demo waiting to happen.

### 1.4 Pricing tiers

| Tier | Plan name | Price | Credits | Headline inclusions | Stated audience |
|---|---|---|---|---|---|
| Starter Vibe | Entry Pack | $5/mo | 5 | 3D Scroll Studio Builder & Simulator; 18+ God-Level Prompts & Templates; Client-Side BYOK AES-256 Key Vault; Full Source Code Ownership (100% MIT) | Indie creators, learning vibe coding, quick landing sites |
| Pro Builder | High Velocity | $50/mo | 75 | Full-Stack SaaS Builder (Auth + DB + Stripe); 480-Frame 3D Scroll Exports (WebP + Canvas); Multi-File Project Export (ZIP + GitHub Sync); BYOK Vault + Managed Claude/GPT-4 Models | Active indie hackers and founders shipping full-stack apps |
| Studio Scale | Most Chosen | $100/mo | 125 | Autonomous 6-Agent AI Swarm Orchestrator; 600-Frame Ultra 3D Parallax Video Pipelines; Multi-Tenant Supabase RLS Database Presets; Commercial Agency Reseller Rights | High-growth startups and creative agencies |
| Enterprise Fleet | Power Cluster | $200/mo | 300 | Dedicated Autonomous Swarm Cluster; Custom 3D WebGL / Three.js Shaders on Demand; Unlimited Workspace Team Seats; 1-on-1 Dedicated Engineering Retainer Access | Heavy vibe coding, dedicated agent clusters, custom WebGL shaders, high-frequency production pipelines |

| Also verified | Value |
|---|---|
| Top-ups | Spark 25/$10 · Surge 60/$20 · Fleet 150/$45 · Vault 400/$100 |
| Annual billing | Save 20% |
| Payment methods | Stripe, Apple Pay, UPI, PayPal, bank wire |

### 1.5 Studio positioning and founder

| Field | Value |
|---|---|
| Brand name | Signhify Studio |
| Name line | Piyush Raj Singh \| Full A.I. Engineering Studio |
| Handle | `@signhify.studio` (see §12 for the discrepancy) |
| Website | `https://signhify.dpdns.org` |
| Watermark | `SIGNHIFY.STUDIO` |
| Footer text | `@SIGNHIFY.STUDIO · SIGNHIFY.DPDNS.ORG` |
| Sign-off | "My name is Piyush Raj Singh. Stop posting. Start shipping." |
| Positioning | Signhify Studio is a FULL A.I. ENGINEERING STUDIO and creators of the Signhify AI 3D Website Builder (signhify.dpdns.org). We engineer cinematic scroll-reactive websites from a single prompt, autonomous software systems, and viral short-form engines. |
| Founder | Piyush Raj Singh — AI systems engineer based in Varanasi, India. Registered MSME, Govt. of India (UDYAM). |
| Stated competition | Lovable.dev, Bolt.new, Replit, Cursor |

**Voice:** authoritative, architectural, hyper-practical, zero-fluff, contrarian, open-source-first.

**Target audience:** Software Engineers & Systems Developers · Tech Founders & Solopreneurs · DevOps & Self-Hosting Enthusiasts · AI Builders & Prompt Engineers

---

## 2. Visual System

### 2.1 Colour tokens

Read from `data/brand.json`. These are injected as CSS custom properties at render time, never re-typed into a template.

| Token | HEX / value | Role in video |
|---|---|---|
| `bg` | `#F8F6F0` | Full-bleed background. Warm off-white, never pure white |
| `card_bg` | `#FFFFFF` | Content cards, the only raised surface |
| `card_border` | `rgba(0, 0, 0, 0.08)` | Card hairline. Present but quiet |
| `primary` | `#111111` | Headlines, structural rules, dominant ink |
| `accent` | `#E05A36` | Eyebrow labels, the `✳` bullet, editorial emphasis |
| `accent_hover` | `#CC4C29` | Darkened accent for press/hover states |
| `highlight` | `#16A34A` | Verification states, "free", "automated", confirmed numbers |
| `text` | `#111111` | Body copy |
| `text_muted` | `#666666` | Secondary copy, captions, footnotes |

### 2.2 Colour discipline — area ratios

The reference carousel is not orange-heavy. It is ink-heavy with accents as punctuation.

| Colour | Target share of frame | Where it appears |
|---|---|---|
| `#F8F6F0` + white cards | ~85% | Background and card fields |
| `#111111` | ~10% | Headlines, rules, icon glyphs |
| `#E05A36` | ~4% | Eyebrow line only |
| `#16A34A` | ~1% | Verification chips, dot indicators |

Orange is a punctuation mark. If a frame shows more orange than ink, it is wrong.

### 2.3 Font roles

| Role | Family | Weight | Tracking | Line height | Where |
|---|---|---|---|---|---|
| Display headline | Plus Jakarta Sans | 800 | `-0.02em` | 1.05 | The single claim on a frame |
| Section headline | Plus Jakarta Sans | 700 | `-0.01em` | 1.15 | Card titles, beat headlines |
| Body | Inter | 400 | `0` | 1.45 | Explanations, subtitles |
| Code / data | JetBrains Mono | 500 | `0` | 1.6 | Numbers, filenames, commands, chrome |
| Eyebrow / chrome | JetBrains Mono | 500 | `0.15em`, uppercase | 1.2 | All micro-labels and persistent chrome |
| Hand annotation | Caveat | 400 | `0` | 1.2 | Sparingly — emphasis notes only |
| Stamp | Anton | 400 | `0.01em`, uppercase | 0.95 | Frame-stamp moments, section numbers |

`hand` and `stamp` are accents, not system fonts. Two of five roles appearing in one frame means the frame has no hierarchy.

### 2.4 Type scale — 9:16 video

Measured from the 9 reference carousel renders and re-scaled for motion legibility. These are studio conventions read off published assets, not a vendor spec.

| Element | Size at 1080 wide | Notes |
|---|---|---|
| Frame headline | 76–92 px | Max 3 lines. Break long headlines rather than shrink |
| Card title | 40–52 px | |
| Body / subtitle | 30–34 px | This is the caption floor — see §8.3 |
| Eyebrow mono | 22–26 px | Always uppercase, always `✳` prefixed |
| Card body | 26–30 px | |
| Chip / status mono | 18–22 px | e.g. `VERIFIED FREE TOOL / RESOURCE` |
| Persistent chrome | 18–22 px mono | `© 2026`, handle, frame counter |
| Caption (burned-in) | 44–56 px | Sits above the platform's own caption line |

### 2.5 The signature — four non-negotiables

Every frame carries all four. This combination is what makes a Reel identifiable as Signhify Studio at a glance.

| # | Element | Spec |
|---|---|---|
| 1 | **Blueprint grid** | Faint square grid on `#F8F6F0`. Hairline, low-contrast, full bleed. 60–80 px pitch. Suggests engineering without ever competing with type |
| 2 | **Orange eyebrow** | `✳ SYSTEM ARCHITECTURE`, `✳ STEP BREAKDOWN`, `✳ COST MODEL`. Mono, uppercase, `#E05A36`, always the first thing on the frame above the headline |
| 3 | **White card** | `#FFFFFF`, `rgba(0,0,0,0.08)` border, 16–24 px radius, soft low shadow. Type sits on the card, never directly on the grid |
| 4 | **Monospace chrome** | `© 2026` top-left · `@SIGNHIFY.STUDIO` top-centre · `NN / NN` frame counter top-right. Footer: `@SIGNHIFY.STUDIO · PIYUSH | GROWTH SYSTEMS` plus a progress dot row |

The chrome is persistent for the full duration. It is the brand's passive watermark — a viewer who screenshots any single frame still gets the handle and the counter.

### 2.6 Layout — carousel to video

The reference system is 1080×1350. Video is 1080×1920. Horizontal rules transfer directly; vertical rules do not.

| Property | Carousel 1080×1350 | Video 1080×1920 | Transfer |
|---|---|---|---|
| Side margin | 80 px | 80 px | Identical. Never change this |
| Top chrome band | 0–110 px | 0–110 px | Identical |
| Eyebrow baseline | ~256 px (slide 01) / ~442 px (slide 05) | ~420 px | Fixed top position for video — the eyebrow should not drift between frames |
| Headline block | Below eyebrow, 3 lines max | Below eyebrow, 3 lines max | Identical |
| Card block | Centred, max ~920 px wide | Centred, max 920 px wide | Identical width |
| Footer chrome | y 1200–1310 | y 1800–1910 | Pinned to bottom, not to a ratio |
| Free vertical space | Minimal | 570 px more than the carousel | **Spend it on one idea per frame. Not on bigger type** |

**The 9:16 problem, stated plainly:** the reference layout is already vertically dense. Adding 570 px does not license an extra paragraph — it licenses a longer beat. Video frames must hold **one** claim, the way a carousel slide does. The extra height buys dwell time, not density.

Motion rule for the layout: content animates within its zone. Cards rise and fade, never slide across the frame. The chrome never moves. Horizontal drift fights the frame counter and makes the composition feel unstable.

### 2.7 Resolving the logo-green vs orange-accent tension

**The facts.** The logo (`assets/signhify-logo-vector.png`) is a rounded-square app icon: near-black `#111111` fill, mint-green border, gradient atom/orbit glyph running green → cyan in the `#16A34A` family. Orange `#E05A36` does not appear anywhere in the mark. Yet orange is the brand's `accent` token and leads every published slide as the eyebrow colour.

**Why this is not a conflict.** Read the 9 reference renders and the two colours already have separate jobs:

| Colour | Job in the published system | Evidence |
|---|---|---|
| `#E05A36` orange | Editorial voice — the eyebrow, the `✳` bullet, the section marker. Human, instructional | `✳ SYSTEM ARCHITECTURE`, `✳ STEP BREAKDOWN` |
| `#16A34A` green | System state — verified, free, automated, confirmed | `● 100% AUTOMATED & FREE`, `VERIFIED FREE TOOL / RESOURCE` |

They are already a working two-accent system. The tension is only apparent because it reads as two candidates for the same role.

**Recommendation — formalise the split, do not recolour anything.**

1. **Green = machine truth.** The logo, verification chips, confirmed numbers, free-tier and open-source badges. Green marks something that was actually observed or checked.
2. **Orange = human voice.** Eyebrows, annotations, calls to action, the part of the video where the person speaks. Orange marks instruction.
3. **Never recolour the logo to orange.** Recolouring a mark to match a UI accent breaks recognition. The logo stays green permanently.
4. **Never place orange inside the logo lockup.** The mark is self-contained.
5. **The logo lives in two places only** — the avatar and the end card. On the end card, place the green logo on `#F8F6F0`, centred, with the orange eyebrow above it. Different zones, no clash.
6. **If a single dominant hue is ever needed**, it is `#111111` at ~10%, with orange ≤4% and green ≤1%. Ink dominates; accents punctuate.

This is the lazy fix and the correct one: no asset is redrawn, no token changes, and the existing 9 published slides already comply.

---

## 3. Content Pillars

### 3.1 The six local pillars

From `data/brand.json`:

1. FOSS SaaS Alternatives
2. Trending GitHub Spotlight
3. Local AI & Edge Compute
4. Developer Power Tools & CLI
5. Self-Hosted Architecture
6. Open Source Economics & Contrarian

These describe what the **studio** does. They do not describe the **product**. Holding both at once without a rule produces two disconnected accounts.

### 3.2 Reconciliation

The product is not a seventh pillar. It is the recurring **artefact** that pillars 1 and 6 produce. That is the structural fix: pillars stay exactly as written, and the product enters through them rather than beside them.

| Pillar | Product angle that belongs inside it | Content shape |
|---|---|---|
| 1. FOSS SaaS Alternatives | The builder itself ships MIT, 100% source ownership. The comparison axis is licence and code ownership, not capability claims | "I own the code. Here is what that changes." |
| 2. Trending GitHub Spotlight | The OSS dependencies the builder runs on. HyperFrames (Apache-2.0) is a verified spotlight item with a licence story worth telling | "Apache-2.0, no thresholds, 40+ commands." |
| 3. Local AI & Edge Compute | The `$0-compute` technique from reference slide 05 — LLM-structured JSON plus programmatic Chromium rendering. BYOK AES-256 key vault means keys never leave the device | "The model writes structure. Chromium draws pixels." |
| 4. Developer Power Tools & CLI | `hyperframes render`, `hyperframes check` as a fail-closed QA gate, `ffprobe` verification | "Three commands, one Reel, zero guesses." |
| 5. Self-Hosted Architecture | Multi-tenant Supabase RLS database presets. Self-hosting the builder | "Multi-tenant, row-level, self-hosted." |
| 6. Open Source Economics & Contrarian | MIT ownership plus a $5 entry tier as the economic argument. Licence cliffs — the Remotion 3-employee finding | "The cheapest plan in this category is the one you can leave." |

### 3.3 The product-demo slotting rule

**Rule: one product demo per five posts. Maximum.**

| Slot | Content |
|---|---|
| 1 of 5 | Product demo — the builder, a preset, a pipeline stage |
| 4 of 5 | Transferable technique the viewer can apply without buying anything |

Rationale, and it is a retention argument rather than a moral one: engineers save technique posts and scroll past product posts. If the ratio inverts, the account reads as an ad feed and the saves — the only durable signal on a technical account — stop accruing. The product is the proof that the technique works. It does not need to be the subject.

**Content shapes by pillar weight**

| Pillar | Share | Primary format |
|---|---|---|
| Developer Power Tools & CLI | 25% | Screen recording with burned-in terminal |
| Local AI & Edge Compute | 20% | Architecture diagram build, beat by beat |
| FOSS SaaS Alternatives | 15% | Side-by-side cost or licence comparison |
| Open Source Economics & Contrarian | 20% | Talking head over white card, contrarian claim |
| Trending GitHub Spotlight | 10% | Repo card → what it replaces |
| Self-Hosted Architecture | 10% | Diagram → deploy steps |

Product-demo posts are drawn from within these shares, not added on top.

---

## 4. Audience-Specific Formats

One account, four audiences. The pillars serve all four; the format and the CTA shift.

| Audience | What they save | What they ignore | Format that lands | CTA that fits |
|---|---|---|---|---|
| **Software Engineers & Systems Developers** | Exact commands, file paths, diffs, measurable claims | Feature tours, pricing pages, anything without a reproducible step | Terminal capture, real file tree, 30–40 s, no voice or TTS | `Comment "BLUEPRINT"` |
| **Tech Founders & Solopreneurs** | Cost math, time-to-ship, what it replaces | Architecture depth beyond the decision point | White-card numbers, a build-to-live-URL trace, 40–60 s | Site link + Starter tier |
| **DevOps & Self-Hosting Enthusiasts** | Deployment reality, resource cost, licence terms | Growth narrative, anything cloud-managed by default | Diagram plus deploy command, 40–60 s | `Comment "FOSS"` |
| **AI Builders & Prompt Engineers** | Prompt structure, JSON schema, why output differed | Business framing, credit economics | Schema build with visible structure, 20–40 s | `Comment "BLUEPRINT"` |

**Rule for mixed-audience frames:** lead with the command or the number. It is the one thing all four audiences can use.

---

## 5. Hook Library

The first 1.5 seconds. Every example below is written inside the brand voice and against the 16-entry banned list. No hype, no manufactured urgency, no claim that was not observed.

| # | Pattern | Example first line |
|---|---|---|
| 1 | Cost inversion | "This whole pipeline costs $0 to run. Here is every layer." |
| 2 | Contrarian claim | "Most AI automation creates debt. Build zero-debt pipelines instead." |
| 3 | Mechanism reveal | "No WebGL. No Three.js. Native browser scroll, hundreds of frames." |
| 4 | Line-item teardown | "400 frames. 8 seconds of source video. 10 lines of extraction." |
| 5 | Constraint first | "1080×1920 at 30 fps on CPU. No cloud, no credits. Here is the cost." |
| 6 | Licence audit | "One licence decides your entire render stack. I read both." |
| 7 | Artefact proof | "Prompt on the left. Live scroll site on the right. One take." |
| 8 | Failure autopsy | "The QA gate killed this render before it shipped. Here is the failure." |
| 9 | Deviation disclosure | "I got the brand wrong on the first pass. This is the diff." |
| 10 | Myth correction | "The model does not need to render your text. It needs to structure it." |
| 11 | Numbered teardown | "Three reasons most vibe-coded landing pages collapse in production." |
| 12 | Spec to ship | "Preset to keyframe to 8-second video to deployable ZIP. Watch each stage." |
| 13 | Schema reveal | "This JSON schema is the whole carousel. No template language." |
| 14 | Stack as artefact | "Six files. No framework. Here is the entire render." |
| 15 | Reframe | "Your text generator does not have a typography problem. It has a rendering problem." |
| 16 | Direct address | "If you deploy anything for free, your licence is a bug waiting to ship." |

**Hook rules**

| Rule | Reason |
|---|---|
| State a verifiable fact in the first 1.5 s | The audience is engineers — they discount unverifiable openings immediately |
| No number you have not measured | Reference slide 05's `$0 Compute Cost` is legitimate because it was measured |
| No countdown, no "before you scroll", no deadline | `fake urgency` is on the banned list |
| Never open on the logo | The logo is a close, not an open |
| One claim per hook | Two claims is no claim |

---

## 6. Script Structure Templates

### 6.1 Short form — 20–40 s

| Beat | Time | Job | Visual | Caption on |
|---|---|---|---|---|
| Hook | 0.0–2.5 s | One verifiable claim | Full-bleed headline, chrome already on | Yes |
| Turn | 2.5–6.0 s | Name the mechanism | Card enters with the mechanism | Yes |
| Mechanism A | 6.0–13.0 s | First step, real artefact | Terminal or diagram build | Yes |
| Mechanism B | 13.0–20.0 s | Second step | Same card system, new card | Yes |
| Proof | 20.0–29.0 s | Show the artefact or the measurement | Card or render | Yes |
| Limit | 29.0–34.0 s | State what it does not do | Muted `#666666` copy | Yes |
| CTA | 34.0–40.0 s | One action | End card, logo, handle | Yes |

### 6.2 Long form — 40–60 s

| Beat | Time | Job | Visual | Caption on |
|---|---|---|---|---|
| Hook | 0.0–3.0 s | Same discipline as short form | Headline | Yes |
| Turn | 3.0–7.0 s | Mechanism named | Card | Yes |
| Step 1 | 7.0–15.0 s | | Card or capture | Yes |
| Step 2 | 15.0–23.0 s | | Card or capture | Yes |
| Step 3 | 23.0–31.0 s | | Card or capture | Yes |
| Proof | 31.0–41.0 s | Artefact or measurement | Card | Yes |
| **Failure / limit** | 41.0–48.0 s | What breaks, what was cut | Muted card | Yes |
| CTA | 48.0–58.0 s | One action | End card | Yes |

**Structural rules for both**

| Rule | Detail |
|---|---|
| The limit beat is mandatory | Claiming only strengths reads as marketing and is the fastest route to being scrolled past by engineers |
| Captions on everything | Autoplay is silent by default. A Reel with no burned-in captions fails the mobile-legibility floor in §8.3 |
| Chrome never animates | It is present from frame 1 and does not move |
| One card at a time | Cards cross-dissolve, never stack |
| CTA is one action | Two CTAs is zero CTAs |

---

## 7. Format Specs

| Property | Value | Status |
|---|---|---|
| Dimensions | 1080 × 1920 | Verified via `ffprobe` on the smoke render |
| Aspect | 9:16 vertical | |
| Frame rate | 30 fps constant | Verified (`r_frame_rate` = 30/1) |
| Duration | 20–60 s | Target |
| Video codec | H.264 | Verified |
| Pixel format | yuv420p | Convention — standard for platform delivery |
| Container | MP4, `+faststart` | Convention |
| Audio codec | AAC | Convention |
| Audio rate | 48 kHz, 192 kbps | Convention |
| Bitrate | 6–15 Mbps VBR | Convention — not measured |
| Renderer | HyperFrames CLI v0.8.58, local headless Chrome, seek-per-frame + FFmpeg | Deterministic |
| QA gate | `hyperframes check` — runtime, layout, motion, WCAG AA contrast, snapshots | Passes 5/5 on the smoke render |

Rows marked *Verified* came from the empirical run. Rows marked *Convention* are studio settings, not measured outputs.

---

## 8. Safe Areas and Mobile Legibility

### 8.1 Why this is a design constraint, not a formatting one

A Reel is watched on a phone, in portrait, usually with the sound off, usually one-handed. Every element outside the comfortable reading zone is either covered by platform UI or too small to parse at arm's length.

### 8.2 Safe zones at 1080 × 1920

| Zone | Range | Use |
|---|---|---|
| Top reserved | y 0–110 | Chrome only: `© 2026`, handle |
| Primary safe | y 180–1560 | Eyebrow, headline, cards, captions. **Everything load-bearing lives here** |
| Bottom reserved | y 1560–1920 | CTA, logo, footer chrome, progress dots |
| Left/right margin | x 80–1000 | Hard content boundary |
| Right rail clearance | x 960–1080 | Keep text and any meaningful mark out of this band |

These are engineering conventions chosen with headroom, not published Instagram specifications. Platform UI changes without notice. Treat them as margins with slack, not as a spec to fill edge to edge.

### 8.3 Legibility rules

| Rule | Value |
|---|---|
| Caption floor | 44 px burned-in, 56 px preferred |
| Body floor | 30 px at 1080 wide |
| Chrome floor | 18 px |
| Minimum contrast | WCAG AA 4.5:1 for body, 3:1 for large type |
| Contrast enforcement | `hyperframes check` — fail-closed, do not override |
| Lines per card | 3 maximum |
| Words per card | 24 maximum |
| Words in a burned-in caption line | 7 maximum |
| Reading time budget | ≥1.8 s per caption beat at 30 fps |

**Verify, do not eyeball.** Pull the rendered MP4, run `ffprobe` for dimensions and codec, and open frames at the beat boundaries. A Reel that renders is not a Reel that is legible.

---

## 9. What Must Never Be Claimed

This is the fabrication ban. It extends the 16-entry `avoid` list in `brand.json` with product-specific honesty rules.

### 9.1 The 16 banned phrases

`generic hype` · `fake urgency` · `unsupported statistics` · `overused motivational language` · `keyword stuffing` · `game-changer` · `unlock the power of` · `in today's fast-paced world` · `dive into` · `at its core` · `seamless` · `robust` · `revolutionary tool` · `next-gen AI` · `ultimate secret` · `must-have app`

Scrub against this exact list **at generation time and again at QA time**. `robust` is the trap — it is ordinary engineering vocabulary and will survive a casual read.

### 9.2 Fabrication ban — never claim these

| # | Never claim | Why |
|---|---|---|
| 1 | Any follower, like, view, save, or engagement number | The Instagram profile is auth-walled. No data was obtainable |
| 2 | Signups, revenue, MRR, churn, or paying-customer counts | No metrics exist |
| 3 | Team size or headcount | Unverified |
| 4 | Customer names, logos, or testimonials | None exist |
| 5 | Uptime, SLA, or availability | Unverified |
| 6 | Render speed on a production composition | Only a 120-frame blank composition was timed, at 15.3 s |
| 7 | "Lovable is 2D only", "Bolt cannot do X", or any competitor capability claim | These are the site's own marketing assertions, unverified |
| 8 | That portfolio or Venture Lab apps work | Link existence was observed. Functionality was not tested |
| 9 | Frame counts, FPS, credits, or pricing not listed in §1.4 | Only the values in this document are approved |
| 10 | Any speedup multiple — "10× faster", "3× cheaper" | No comparative benchmark was run |
| 11 | A post-level performance claim about any past Reel or carousel | Unmeasurable |
| 12 | That `@signhify.studio` is the live handle | Discrepancy unresolved — see §12 |

### 9.3 If a number is not in this document, it does not go in a caption.

---

## 10. CTA Ladder

One ladder, mapped to the real tiers. Each rung earns the next.

| Rung | Offer | Audience state | CTA copy | Where it sends |
|---|---|---|---|---|
| 0 | The blueprint | Curious, not buying | `Comment "BLUEPRINT" or "FOSS"` | Comment DM — the runnable artefact |
| 1 | Starter Vibe — $5/mo, 5 credits | Tried the technique, wants a tool | "Entry Pack is $5. Five credits, MIT code you own." | `signhify.dpdns.org` |
| 2 | Pro Builder — $50/mo, 75 credits | Building a real product | "Full-Stack SaaS Builder: auth, DB, Stripe, 480-frame exports." | `signhify.dpdns.org` |
| 3 | Studio Scale — $100/mo, 125 credits | Shipping for clients | "6-agent swarm, Supabase RLS presets, agency reseller rights." | `signhify.dpdns.org` |
| 4 | Enterprise Fleet — $200/mo, 300 credits | High-frequency production | "Dedicated swarm cluster, custom shaders, team seats, engineering retainer." | Direct conversation |

### 10.1 Rules

| Rule | Detail |
|---|---|
| Rung 0 is the default | Four posts in five carry the comment CTA, not the link |
| Never price-hop | Do not move a viewer from rung 0 to rung 3 in one video |
| Name the exact verified inclusion | `$5/mo, 5 credits, 100% MIT` is verifiable. "Best value" is not |
| Enterprise is mentioned, never pushed | It is one of four tiers, not the destination |
| Site link goes in the caption and on the end card | `@SIGNHIFY.STUDIO · SIGNHIFY.DPDNS.ORG` is the footer text of record |
| Use the lead magnet verbatim | `Comment "BLUEPRINT" or "FOSS" for the full runnable code.` — from `brand.json` |

---

## 11. Concept Rubric

Score every video idea before it is scripted. Seven axes, weighted, 1–5 each.

### 11.1 Weights

| Axis | Weight | Question |
|---|---|---|
| Audience relevance | 20% | Does one of the four named audiences save this? |
| Educational value | 20% | Does the viewer leave able to do something they could not do? |
| Product relevance | 15% | Does it connect to the builder without pitching it? |
| Differentiation | 15% | Has this been said better by someone else? |
| Visual storytelling potential | 15% | Can it carry a frame without a talking head? |
| Verifiability | 10% | Can every claim be checked against a real artefact? |
| Short-video explainability | 5% | Does it survive at 20–40 s? |
| **Total** | **100%** | |

### 11.2 Scoring anchors

| Score | Audience relevance | Educational value | Product relevance | Differentiation | Visual potential | Verifiability | Explainability |
|---|---|---|---|---|---|---|---|
| **5** | Hits all four audiences | Viewer can rebuild it from this frame alone | Directly demonstrates a pipeline stage | Nobody else has made this argument | Motion carries the idea without narration | Every claim traced to an observed artefact | Unmistakable in 20 s |
| **4** | Hits two audiences | Clear takeaway, some assembly required | Shows a real artefact from the builder | Familiar topic, sharper angle than usual | Strong visual spine, light narration | Claims checkable, one needs sourcing | Clear in 30 s |
| **3** | Hits one audience | Informative but not actionable | Adjacent — brand-adjacent, product-adjacent | Familiar topic, familiar take | Depends on captions to carry it | Mostly checkable, one soft claim | Loses something at 40 s |
| **2** | Audience unclear | Tells rather than teaches | Name-drop only | Well-trodden | Static frames | Soft claims present | Needs 90 s |
| **1** | Wrong audience | No takeaway | Off-product | Nothing new | Unusable visually | Unverifiable | Does not fit the format |

### 11.3 Decision rules

| Weighted score | Decision |
|---|---|
| ≥ 4.00 | Ship. Script it |
| 3.20 – 3.99 | Revise. Identify the weakest axis and rework it, or cut |
| < 3.20 | Reject |

**Hard gates — no score override:**

| Gate | Rule |
|---|---|
| Verifiability | Must score ≥ 3. An unprovable idea does not ship, regardless of total |
| Product relevance | Must score ≥ 2. Below that it is off-account content |
| Banned-phrase scan | Must return zero hits against the 16-entry list |
| Claim audit | Every claim in the script maps to §1 of this document or to an observed artefact |

---

## 12. Research Limitations

Recorded so no downstream document mistakes an unknown for a fact.

| # | Limitation | Consequence |
|---|---|---|
| 1 | **`instagram.com/signhify.studio` was blocked by an auth wall at research time** | No post-level analysis is possible. No follower count, engagement rate, retention curve, or top-post identification. Any document claiming these is fabricating them |
| 2 | **Handle discrepancy, unresolved** | `brand.json` and all 9 carousel watermarks say `@signhify.studio`. The website footer links Instagram as `/piyushrajsingh.golu` and LinkedIn as `/in/piyushraj-singh`. Which is live is unknown. On-screen chrome uses `@SIGNHIFY.STUDIO` because 9 published assets already carry it. Resolve before the next brand touch |
| 3 | **No business metrics exist** | No signups, revenue, team size, testimonials, uptime, or churn were obtainable. None are asserted in these documents |
| 4 | **Competitor claims are marketing assertions** | "Lovable: Basic 2D only" and the rest of the pricing-page comparison are the site's own words, unverified, and excluded from the fabrication ban's approved claims |
| 5 | **Portfolio and Venture Lab were not exercised** | Four portfolio entries (Signhify AI, Veepee Engineers, GymFlow, AutoReels AI) and 10 Venture Lab apps were observed to exist. Functionality was not tested |
| 6 | **Product claims are vendor claims** | Frame counts, FPS ranges, credit values, and tier inclusions are taken from the site's own marketing. They are internally consistent and are the approved source, but they were not independently measured |
| 7 | **Visual specs were read off published renders** | Grid pitch, type sizes, and safe zones in §2 and §8 are measured from the 9 carousel images and studio conventions. They are not a vendor design specification |
| 8 | **Safe zones are engineering conventions** | The values in §8.2 carry headroom for platform UI. They are not published Instagram specifications and platform UI changes without notice |
| 9 | **Only a blank composition has been timed** | 15.3 s for 120 frames. No production render has been measured. No per-Reel SLA is committed |

---

## 13. One-Page Operating Summary

| Decision | Answer |
|---|---|
| Light or dark video? | **Light.** `#F8F6F0` background, always |
| Palette rotation? | One palette. Vary layout, never hue |
| Type hierarchy | Five roles. Two appearing in one frame means no hierarchy |
| Logo colour | Never change it. Green is machine truth |
| Orange usage | Eyebrows and annotations only, ~4% of frame area |
| Product demo frequency | 1 in 5 posts, maximum |
| Default CTA | `Comment "BLUEPRINT" or "FOSS"` |
| Hook discipline | One verifiable fact in the first 1.5 s |
| Mandatory beat | The limit beat. Always |
| Ship threshold | Weighted rubric ≥ 4.00 with verifiability ≥ 3 |
| QA gate | `hyperframes check`, fail-closed, no override |
| Sign-off | "My name is Piyush Raj Singh. Stop posting. Start shipping." |

---

*Compiled 2026-10-11 from `data/brand.json`, the live product site at `signhify.dpdns.org`, and 9 published carousel renders. Every colour, price, credit value, and capability listed here is traceable to one of those three sources. Everything that could not be verified is in §12, not in the strategy.*