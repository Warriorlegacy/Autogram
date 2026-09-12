"""
Configuration management for Autogram engine.
Loads settings from environment variables and .env file with safe defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

BASE_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # LLM Settings (Supports 100% Free Providers: Gemini, Groq, Ollama, or Zero-Cost Built-In)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    claude_api_key: str | None = Field(default=None, alias="CLAUDE_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    huggingface_api_key: str | None = Field(default=None, alias="HUGGINGFACE_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    github_copilot_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GITHUB_COPILOT_TOKEN", "GH_COPILOT_TOKEN", "COPILOT_TOKEN")
    )
    nvidia_nim_api_key: str | None = Field(default=None, alias="NVIDIA_NIM_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")
    llm_provider: str = Field(default="auto", alias="LLM_PROVIDER") # auto, groq, openrouter, gemini, cloudflare, nvidia, ollama, builtin
    llm_model: str = Field(default="gemini-2.5-flash", alias="LLM_MODEL")

    # Image Generation Settings (Pollinations FLUX.1 free, Cloudflare Workers AI, Google Imagen 3, or OpenAI DALL-E 3)
    image_provider: str = Field(default="pollinations", alias="IMAGE_PROVIDER") # pollinations, cloudflare, imagen, dalle, none
    image_style: str = Field(default="cyber-minimalist", alias="IMAGE_STYLE") # cyber-minimalist, 3d-isometric, photorealistic-dark, conceptual-ai
    cloudflare_account_id: str | None = Field(default=None, alias="CLOUDFLARE_ACCOUNT_ID")
    cloudflare_api_token: str | None = Field(default=None, alias="CLOUDFLARE_API_TOKEN")

    # Video Generation (local MoneyPrinterTurbo render server — $0: edge-tts + Pexels free + FFmpeg)
    mpt_base_url: str = Field(default="http://127.0.0.1:8080", alias="MPT_BASE_URL")
    pexels_api_key: str | None = Field(default=None, alias="PEXELS_API_KEY")

    # Meta Instagram Graph API
    ig_user_id: str | None = Field(default=None, alias="IG_USER_ID")
    ig_access_token: str | None = Field(default=None, alias="IG_ACCESS_TOKEN")
    meta_api_version: str = Field(default="v23.0", alias="META_API_VERSION")

    # Storage (S3 / R2 / Cloudinary / Local)
    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_region: str = Field(default="auto", alias="S3_REGION")
    public_cdn_base: str = Field(default="http://localhost:8000", alias="PUBLIC_CDN_BASE")
    imgbb_api_key: str | None = Field(default="f0ee2a304a71d5b2da983153c2284b73", alias="IMGBB_API_KEY")

    # Database
    database_url: str = Field(default="sqlite:///autopilot.db", alias="DATABASE_URL")

    # Scheduling
    timezone: str = Field(default="Asia/Kolkata", alias="TIMEZONE")
    posting_time: str = Field(default="19:30", alias="POSTING_TIME")

    # Alerts
    alert_webhook_url: str | None = Field(default=None, alias="ALERT_WEBHOOK_URL")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    # Monetization & Access Control (Owner Free VIP Access vs Paid Client Licensing)
    autogram_owner_key: str = Field(default="autogram_owner_vip_2026", alias="AUTOGRAM_OWNER_KEY")
    autogram_client_key: str | None = Field(default=None, alias="AUTOGRAM_CLIENT_KEY")
    autogram_secret_salt: str = Field(default="autogram_master_monetization_secret_2026_salt", alias="AUTOGRAM_SECRET_SALT")
    upi_id: str = Field(default="6202442690@jio", alias="UPI_ID")
    whatsapp_number: str = Field(default="6202442690", alias="WHATSAPP_NUMBER")
    stripe_starter_url: str = Field(default="https://buy.stripe.com/starter_tier", alias="STRIPE_STARTER_URL")
    stripe_growth_url: str = Field(default="https://buy.stripe.com/growth_tier", alias="STRIPE_GROWTH_URL")
    stripe_enterprise_url: str = Field(default="https://buy.stripe.com/enterprise_tier", alias="STRIPE_ENTERPRISE_URL")

    # Dry-Run
    dry_run: bool = Field(default=True, alias="DRY_RUN")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
