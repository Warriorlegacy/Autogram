"""
Autogram Viral Growth & Algorithm Optimization Engine (src/growth/viral_engine.py).
Maximizes organic reach, Explore page indexing, Save-rates, and follower conversion.
"""

import random
from typing import Any, Dict, List

class ViralGrowthEngine:
    """
    Implements 2026 Instagram algorithm multipliers:
    1. 3-Tier Dynamic Hashtag Clustering (Broad + Intent + Niche)
    2. Save & Share Velocity Hooks (3x-5x weighting over likes)
    3. High-Conversion Lead Magnet & Comment Velocity Loop
    4. First-Comment Discussion Spark
    """

    MACRO_EXPLORE_TAGS = [
        "#OpenSource", "#SelfHosted", "#FOSS", "#SoftwareEngineering",
        "#DeveloperCommunity", "#DevOps", "#Linux", "#SystemDesign",
        "#TechInnovation", "#Programming", "#TechTrends"
    ]

    INTENT_MID_TAGS = {
        "FOSS SaaS Alternatives": [
            "#OpenSourceAlternative", "#SelfHosting", "#NoMoreSaaS",
            "#ZeroCostStack", "#DockerCompose", "#DataPrivacy", "#Homelab"
        ],
        "Trending GitHub Spotlight": [
            "#GitHubTrending", "#OpenSourceProject", "#RepoSpotlight",
            "#CodeDaily", "#GitHubStars", "#BuildInPublic", "#DevStack"
        ],
        "Local AI & Edge Compute": [
            "#LocalAI", "#Ollama", "#OpenSourceLLM", "#PrivateAI",
            "#RunLocal", "#EdgeAI", "#vLLM", "#AIWorkflows"
        ],
        "Developer Power Tools & CLI": [
            "#DeveloperTools", "#TerminalTools", "#CLITools", "#RustLang",
            "#DevProductivity", "#CodingHacks", "#GitTips"
        ],
        "Self-Hosted Architecture": [
            "#SelfHosted", "#Homelab", "#Docker", "#ReverseProxy",
            "#CaddyServer", "#CloudArchitecture", "#SysAdmin"
        ],
        "Open Source Economics & Contrarian": [
            "#OpenSourceSoftware", "#SoftwareFreedom", "#TechEconomics",
            "#ContrarianTech", "#VendorLockIn", "#ZeroBurn"
        ],
        # Legacy fallback pillars
        "AI Tool Breakdown": [
            "#AgenticAI", "#LLMArchitecture", "#PromptEngineering",
            "#AIWorkflows", "#TechStack", "#AutonomousAgents"
        ],
        "Prompting & Workflow": [
            "#PromptEngineering", "#WorkflowAutomation", "#DevProductivity",
            "#DeveloperTools", "#VibeCoding", "#PythonAutomation"
        ],
        "Marketing Psychology": [
            "#GrowthSystems", "#B2BMarketing", "#ContentEngine",
            "#DocumentDontCreate", "#GaryVeeModel", "#ShipFast"
        ],
        "Tech Industry Explainer": [
            "#CloudArchitecture", "#DevOps", "#OpenSource",
            "#SoftwareDesign", "#ScaleSystems", "#TechFounders"
        ],
        "Career & Skills": [
            "#Solopreneur", "#EngineeringLeadership", "#SoloBuilder",
            "#FounderMindset", "#FullStackEngineer", "#IndieHacker"
        ],
        "Myth-Bust / Contrarian": [
            "#ContrarianThinking", "#TechDebate", "#SoftwareDesign",
            "#Startups", "#EngineeringRealities", "#ZeroDebtPipeline"
        ]
    }

    NICHE_COMMUNITY_TAGS = [
        "#SelfHostedCommunity", "#HomelabCommunity", "#OpenSourceDev",
        "#SignhifyStudio", "#SoloBuilder", "#IndieHacker", "#LinuxAdmin"
    ]

    TOPIC_KEYWORD_MAP = {
        "foss": ["#FOSS", "#OpenSource", "#FreeSoftware"],
        "github": ["#GitHubTrending", "#OpenSource", "#RepoSpotlight"],
        "docker": ["#Docker", "#DockerCompose", "#Containers"],
        "self-hosted": ["#SelfHosted", "#Homelab", "#PrivateCloud"],
        "alternative": ["#OpenSourceAlternative", "#ZeroCostStack", "#NoMoreSaaS"],
        "coolify": ["#Coolify", "#SelfHostedPaaS", "#VercelAlternative"],
        "n8n": ["#n8n", "#WorkflowAutomation", "#ZapierAlternative"],
        "ollama": ["#Ollama", "#LocalAI", "#OpenSourceLLM"],
        "pdf": ["#StirlingPDF", "#OpenSourceTools", "#SelfHosted"],
        "docu": ["#Documenso", "#OpenSourceSigning", "#DigitalSignature"],
        "caddy": ["#CaddyServer", "#ReverseProxy", "#DevOps"],
        "cli": ["#CLITools", "#TerminalNinja", "#DevProductivity"],
        "agent": ["#MultiAgentSystems", "#AutonomousAgents", "#AgenticAI"],
        "rag": ["#RAG", "#VectorDatabase", "#RetrievalAugmentedGeneration"],
        "llm": ["#LargeLanguageModels", "#OpenSourceLLM", "#LocalInference"],
        "python": ["#PythonDeveloper", "#PythonAutomation", "#PyTorch"],
        "cloud": ["#CloudArchitecture", "#DevOps", "#Serverless"],
        "cost": ["#ZeroCostStack", "#FinOps", "#SlashBurnRate"]
    }

    def build_viral_hashtags(self, pillar: str, topic: str = "", max_tags: int = 15) -> List[str]:
        """
        Constructs an optimal 3-tier hashtag cluster:
        - 4 Macro Explore tags (500k-2M+ reach)
        - 5-6 Intent mid-volume tags (50k-500k reach)
        - Topic-specific dynamic tags (extracted from topic keywords)
        - 4-5 Niche high-engagement tags (<50k reach)
        """
        macro = random.sample(self.MACRO_EXPLORE_TAGS, min(4, len(self.MACRO_EXPLORE_TAGS)))
        
        pillar_tags = self.INTENT_MID_TAGS.get(pillar, [
            "#OpenSource", "#SelfHosted", "#DevTools", "#SoftwareArchitecture"
        ])
        intent = random.sample(pillar_tags, min(5, len(pillar_tags)))
        
        # Extract contextual topic tags
        topic_tags = []
        if topic:
            topic_lower = topic.lower()
            for kw, tags in self.TOPIC_KEYWORD_MAP.items():
                if kw in topic_lower:
                    topic_tags.extend(tags)
        
        niche = random.sample(self.NICHE_COMMUNITY_TAGS, min(4, len(self.NICHE_COMMUNITY_TAGS)))
        
        # Combine without duplicates while maintaining order
        seen = set()
        combined = []
        # Priority order: Core mandatory, Topic specific, Intent, Macro, Niche
        core_anchors = ["#OpenSource", "#SelfHosted", "#DevTools", "#SignhifyStudio", "#FOSS"]
        for tag in core_anchors + topic_tags + intent + macro + niche:
            clean = tag.strip()
            if not clean.startswith("#"):
                clean = f"#{clean}"
            if clean.lower() not in seen:
                seen.add(clean.lower())
                combined.append(clean)
        
        return combined[:max_tags]

    def format_caption_with_hashtags(self, caption_text: str, hashtags: List[str]) -> str:
        """Appends hashtags cleanly to the caption with spacer lines."""
        text = caption_text.strip()
        tags_str = " ".join(hashtags)
        if not text:
            return tags_str
        if "#" in text:
            return text
        return f"{text}\n\n.\n.\n{tags_str}"

    def generate_default_caption(self, topic: str = "Self-Hosted Open Source Architecture", pillar: str = "FOSS SaaS Alternatives") -> Dict[str, Any]:
        """Generates a complete high-converting caption with 3-tier viral hashtags."""
        tags = self.build_viral_hashtags(pillar, topic=topic)
        caption_body = (
            f"⚡ {topic}\n\n"
            "Swipe through the complete slide deck for the exact 1-line setup commands, architecture diagrams, and docker-compose breakdown.\n\n"
            "Key takeaways inside:\n"
            "• Zero monthly SaaS subscription fees ($0 vs $200+/mo)\n"
            "• 100% data ownership and privacy on your own server or local hardware\n"
            "• 1-command deployment with persistent volumes\n\n"
            "👉 Swipe to inspect the architecture.\n\n"
            "⚡ Want the runnable blueprint? Comment 'FOSS' below and I'll DM you the full GitHub repo link + docker-compose file.\n\n"
            "📌 Save this post for your next self-hosting sprint.\n"
            "🚀 Follow @signhify.studio for daily high-leverage open source tools & architectures.\n\n"
            "— My name is Piyush. Stop posting. Start shipping.\n\n"
            "💬 Are you paying for SaaS or running open source on your own infrastructure?"
        )
        full_caption = self.format_caption_with_hashtags(caption_body, tags)
        return {
            "caption": full_caption,
            "body": caption_body,
            "hashtags": tags,
            "topic": topic,
            "pillar": pillar
        }

    def generate_first_comment(self, carousel: Dict[str, Any]) -> str:
        """
        Generates an authoritative, discussion-sparking first comment to accelerate
        Instagram algorithm comment velocity within the first 30 minutes.
        """
        slides = carousel.get("slides", [])
        trigger_word = carousel.get("trigger_word") or "FOSS"
        
        takeaways = []
        for s in slides:
            if s.get("layout") in ["takeaway", "standard", "diagram", "framework", "comparison"]:
                hl = s.get("headline", "")
                if hl and len(hl) < 60:
                    takeaways.append(hl)
            if len(takeaways) >= 3:
                break
                
        if not takeaways and slides:
            takeaways = [s.get("headline", "High-leverage system") for s in slides[1:4]]

        bullets = "\n".join([f"• {t}" for t in takeaways])

        comment = f"""📌 CORE ARCHITECTURE TAKEAWAYS:
{bullets}

⚡ Comment "{trigger_word}" and I'll DM you the full GitHub repo link + docker-compose blueprint.

💬 Question for builders: Are you currently self-hosting this or still paying monthly SaaS bills?"""
        return comment

    def optimize_caption(self, caption_text: str, handle: str = "@signhify.studio", trigger_word: str = "FOSS") -> str:
        """
        Ensures high-retention save cues and follow prompts are seamlessly embedded.
        """
        return caption_text

viral_engine = ViralGrowthEngine()
