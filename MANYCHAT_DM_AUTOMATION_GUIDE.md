# ManyChat & DM Automation Master Guide for @signhify.studio

> **Objective:** Convert every comment into a high-engagement viral signal and direct follower, powering the **100k followers in 15 days** growth flywheel.

---

## 1. Why DM Automation is Mandatory for 100k Followers

1. **Algorithmic Explosion:** When 100+ people comment `"FOSS"` or `"PROMPT"`, Instagram's recommendation algorithm flags the post as exceptionally valuable and pushes it onto the **Explore Feed** and **Reels Suggestions**.
2. **High Follower Conversion (65–85%):** Rather than hoping viewers visit your profile, the automated DM delivers value directly into their inbox alongside an invitation to follow.
3. **Zero-Friction Value Delivery:** Users get the exact 1-line Docker command, docker-compose blueprint, or full ChatGPT prompt code in seconds.

---

## 2. Prerequisites (5-Minute Setup)

1. **Instagram Account Type:** Your `@signhify.studio` profile must be a **Creator** or **Business** account (Settings → Account Type → Switch to Professional Account).
2. **Connected Facebook Page:** Meta Graph API requires your Instagram account to be linked to a Facebook Page (even a blank page works).
3. **ManyChat Free Account:** Sign up at [manychat.com](https://manychat.com) (the free tier supports up to 1,000 active contacts and unlimited comment automations).

---

## 3. Step-by-Step ManyChat Automation Configuration

### Trigger 1: The `"FOSS"` Keyword Automation

#### Step A: Create Trigger
1. In ManyChat dashboard, go to **Automation** → **+ New Flow** → **Start from Scratch**.
2. Set Trigger: **Instagram** → **User comments on your Post or Reel**.
3. Target: Select **All Posts & Reels** (so every future scheduled post works automatically).
4. Keyword matching: Select **Comment contains specific words** and enter:
   - `FOSS`
   - `foss`
   - `self-host`
   - `docker`

#### Step B: Public Comment Reply (Randomize 4 Variations)
ManyChat allows you to add multiple public comment replies to avoid repetitive spam detection:
- `Variation 1:` *"Just sent the full Docker setup & GitHub link to your DMs! 🚀"*
- `Variation 2:` *"Check your DMs! The 1-click self-host blueprint is on the way ⚡"*
- `Variation 3:` *"Sent! Enjoy the free alternative. Let me know if you hit any setup snags 🛠️"*
- `Variation 4:` *"DM sent! Stop paying SaaS bills and start shipping 📦"*

#### Step C: Direct Message (DM) Content
Configure the first message sent to their inbox:
```text
Hey builder! 👋 

Here is the complete self-hosting blueprint and 1-line Docker setup from today's carousel:

📦 Tool: Stirling-PDF / Coolify / Open-WebUI
⚡ Command: docker compose up -d
🔗 Master Vault: https://github.com/signhify/open-source-vault

(Tap the button below to copy the full config file)
```
- **Action Button 1:** `Open GitHub Blueprint 📦` → URL: `https://github.com/signhify/open-source-vault`
- **Action Button 2:** `Follow @signhify.studio 🚀` → URL: `https://instagram.com/signhify.studio`

---

### Trigger 2: The `"PROMPT"` Keyword Automation

#### Step A: Create Trigger
1. In ManyChat, create a new flow titled **Viral Prompt Delivery**.
2. Set Trigger: **Instagram** → **User comments on your Post or Reel**.
3. Target: **All Posts & Reels**.
4. Keywords:
   - `PROMPT`
   - `prompt`
   - `code`
   - `megaprompt`

#### Step B: Public Comment Reply (Randomize 3 Variations)
- `Variation 1:` *"Just sent the complete prompt code & variables to your DMs! 🔥"*
- `Variation 2:` *"Check your inbox! The copy-paste prompt architecture is in your DMs ⚡"*
- `Variation 3:` *"Sent! Copy and paste it straight into ChatGPT or Claude 📋"*

#### Step C: Direct Message (DM) Content
```text
Here is the full copy-paste prompt code + variables from today's breakdown! 🚀

🧠 Framework: Chain-of-Density / Tree-of-Thoughts / SoT
🎯 Best Models: GPT-4o, Claude 3.5 Sonnet, o3-mini
📋 Master Prompt Vault: https://github.com/signhify/prompt-vault

Make sure to replace [INPUT_DATA] before running!

⚡ Follow @signhify.studio for daily tested AI prompt architectures!
```
- **Action Button 1:** `Copy Prompt Code 📋` → URL: `https://github.com/signhify/prompt-vault`
- **Action Button 2:** `Join Free Discord / Community 💬`

---

## 4. Where to Host Your Free Lead Magnet Content (100% Free)

You need a public link to send in the DMs. The best options that build credibility:

| Platform | Best For | Why It Converts |
|---|---|---|
| **GitHub Repository** | FOSS docker-compose files & bash scripts | High credibility with developers; stars your repo. |
| **Public Notion Page** | Prompt collections & cheat sheets | Clean mobile UI, easy to read and copy. |
| **Google Drive Folder** | PDF cheat sheets & guides | Instant 1-tap mobile preview. |

**Recommended Setup:**
Create two public GitHub repositories under your account:
1. `github.com/signhify/open-source-vault` (contains `docker-compose.yml` templates for Coolify, Stirling-PDF, n8n, etc.)
2. `github.com/signhify/prompt-vault` (contains markdown files for Chain-of-Density, Tree-of-Thoughts, AST SQL Guard, etc.)

---

## 5. Instagram Safety & Rate-Limit Rules

To keep your account 100% safe while handling high comment volume:
1. **Always use 3+ randomized public comment replies** in ManyChat so Instagram doesn't flag identical responses as robotic spam.
2. **Add a 5–10 Second Delay:** In ManyChat, insert a "Typing Delay" (5 seconds) before sending the first message.
3. **Avoid Shortened URLs:** Do not use `bit.ly` or `tinyurl.com`. Use full domain names (`github.com/...` or `notion.site/...`), which Meta trusts.
4. **Never DM Unprompted:** Only message users who explicitly left a comment with the trigger keyword.

---

## 6. How Autogram Integrates Automatically

Autogram already formats every caption and slide to drive this automation:
- **Slide 7/10:** *"Want the full setup guide & docker-compose blueprint? Comment FOSS below."*
- **Caption Bottom:** *"⚡ Want the full GitHub repo + docker-compose file? Comment 'FOSS' or 'PROMPT' below and I'll send it straight to your DMs."*
- **First Comment:** Automatically posted within 3 seconds of publication to seed the comment section and remind users of the trigger words.
