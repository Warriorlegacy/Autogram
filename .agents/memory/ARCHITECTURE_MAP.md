# REPOSITORY ARCHITECTURAL SYMBOL MAP
> Auto-generated structural index. AGENTS: Consult this index instead of scanning directories.

### `build_blueprint_pdf.py`
  - def build()

### `build_master_spec_pdf.py`
  - def build_pdf(output_path)

### `compile_blueprint_pdf.py`
  - def build_blueprint_pdf(output_path)

### `compile_pdf.py`
  - def build_pipeline_pdf(output_path)

### `dashboard_api.py`
  - def get_brand_config()
  - class NormalizeApiPrefixMiddleware [methods: __init__, __call__]
  - def read_env()
  - def write_env_key(key, value)
  - def redact(val)
  - def read_schedule()
  - def write_schedule(data)
  - def get_next_scheduled_run()
  - def get_output_runs()
  - def scheduler_worker()
  - def run_pipeline_subprocess(mode, topic, pillar, queue_id, content_format)
  - def health()
  - def api_status()
  - def api_schedule()
  - def api_schedule_delete(item_id)
  - def api_schedule_execute(item_id)
  - def api_scheduler_toggle()
  - def api_publish()
  - def api_publish_story()
  - def api_publish_reel()
  - def api_publish_shorts()
  - def api_publish_video()
  - def api_mpt_status()
  - def api_caption_generate()
  - def api_generate()
  - def api_token_refresh()
  - def api_instagram_auto_dm()
  - def api_instagram_auto_dm_stats()
  - def api_env_get()
  - def api_env_set()
  - def api_runs()
  - def api_memory()
  - def api_pipeline_status()
  - def api_pipeline_run()
  - def api_pipeline_stop()
  - def api_webhook_autopilot()
  - def api_cron_auto_dm()
  - def api_blueprint_markdown()
  - def api_blueprint_pdf()
  - def api_webhook_instagram()
  - def api_cron_status()
  - def api_proof_gates()
  - def api_trends_candidates()
  - def api_topics_suggest()
  - def api_platform_assets(platform_id)
  - def api_calculator_evaluate()
  - def get_current_user_from_request()
  - def api_auth_login()
  - def api_auth_signup()
  - def api_auth_me()
  - def api_auth_logout()
  - def api_auth_pricing()
  - def api_auth_users()
  - def api_auth_update_user_tier(user_id)
  - def api_get_providers()
  - def api_save_provider()
  - def api_detect_models()
  - def api_set_active_provider()
  - def api_set_media_model()
  - def api_test_provider()
  - def api_generate_image()
  - def api_get_prompts()
  - def api_get_templates()
  - def api_output_file(filepath)
  - def dashboard()
  - def health_check()
  - def root()
  - def init_daemon()

### `free_host.py`
  - class Handler [methods: __init__, translate_path, do_GET, end_headers]
  - def main()

### `generate_pdf_guide.py`
  - def generate_pdf()

### `orchestrator.py`
  - def _mpt_storage()
  - def _slot_precheck(dry_run, fmt, needs_ig_quota)
  - def _run_guarded(label, dry_run, fn)
  - def run_pipeline(dry_run, custom_topic, custom_pillar)
  - def run_story_pipeline(dry_run, custom_topic, custom_pillar)
  - def run_reel_pipeline(dry_run, custom_topic, custom_pillar)
  - def run_shorts_pipeline(dry_run, custom_topic, custom_pillar)
  - def run_video_pipeline(dry_run, custom_topic, custom_pillar)
  - def run_scheduler(dry_run)
  - def main()

### `pipeline_runner.py`
  - def purge_old_artifacts(target_dir, max_age_hours)
  - def execute_autonomous_run(topic, pillar, dry_run, destinations)
  - def main()

### `setup_meta_token.py`
  - def update_env_file(key, value)
  - def main()

### `test_meta_connection.py`
  - def print_header(text)
  - def verify_meta_connection()

### `js/app.js`
  (scripts / configuration)

### `js/auth.js`
  (scripts / configuration)

### `js/carousel-simulator.js`
  (scripts / configuration)

### `js/premium.js`
  (scripts / configuration)

### `js/roi-calculator.js`
  (scripts / configuration)

### `js/three-scene.js`
  (scripts / configuration)

### `renderer/render.py`
  - def resolve_theme(carousel_data)
  - class CarouselRenderer [methods: __init__, render_slide_html, render_carousel, render_story]
  - def render_sample(output_dir)

### `renderer/validate.py`
  - class ValidationError [methods: ]
  - def validate_slide_content(slide)
  - def validate_image_file(image_path, expected_width, expected_height)

### `scratch/audit_buttons.py`
  (scripts / configuration)

### `scratch/audit_clickables.py`
  (scripts / configuration)

### `scratch/audit_js_calls.py`
  (scripts / configuration)

### `scratch/debug_qa.py`
  (scripts / configuration)

### `scratch/inspect_all_calls.py`
  (scripts / configuration)

### `scratch/inspect_backend_core.py`
  (scripts / configuration)

### `scratch/inspect_buttons.py`
  (scripts / configuration)

### `scratch/inspect_dashboard_actions.py`
  (scripts / configuration)

### `scratch/inspect_db.py`
  (scripts / configuration)

### `scratch/inspect_funcs_detail.py`
  - def find_func(name)

### `scratch/inspect_images.py`
  (scripts / configuration)

### `scratch/inspect_index_buttons.py`
  (scripts / configuration)

### `scratch/inspect_more_funcs.py`
  - def print_fn(name)

### `scratch/inspect_pipeline_subproc.py`
  (scripts / configuration)

### `scratch/inspect_routes.py`
  (scripts / configuration)

### `scratch/list_routes.py`
  (scripts / configuration)

### `scratch/patch_dashboard_full.py`
  (scripts / configuration)

### `scratch/print_pub_sched.py`
  - def print_func(name)

### `scratch/sync_assets.py`
  (scripts / configuration)

### `scratch/test_backend_fixes.py`
  (scripts / configuration)

### `scratch/test_cloudflare_ai.py`
  (scripts / configuration)

### `scratch/test_cloudflare_generate.py`
  (scripts / configuration)

### `scratch/test_free_uploaders.py`
  (scripts / configuration)

### `scratch/test_live_urls.py`
  (scripts / configuration)

### `scratch/test_multi_providers.py`
  - def main()

### `scratch/test_openrouter.py`
  (scripts / configuration)

### `scratch/test_openrouter_generate.py`
  (scripts / configuration)

### `scratch/test_publish_client.py`
  (scripts / configuration)

### `scratch/verify_all_handlers.py`
  (scripts / configuration)

### `scratch/verify_all_templates.py`
  - def main()

### `scratch/verify_all_themes.py`
  - def main()

### `scratch/verify_dom_ids.py`
  (scripts / configuration)

### `scratch/verify_endpoints.py`
  (scripts / configuration)

### `scripts/check_cronjobs.py`
  (scripts / configuration)

### `scripts/generate_repo_map.py`
  - def parse_python_symbols(filepath)
  - def generate_map(root_dir)

### `scripts/pipeline_reels.py`
  - def generate_reel_content(topic)
  - def download_visual(prompt, output_path)
  - def to_ass_time(sec)
  - def _events_for_words(words, chunk_size)
  - def compile_word_level_ass(audio_path, ass_path)
  - def render_ffmpeg(image_path, audio_path, ass_path, output_path)
  - def execute_reels_pipeline(topic)

### `scripts/publish_instagram.py`
  - def publish_reel_to_instagram(video_url, caption)

### `scripts/setup_cronjob_org.py`
  - def create_slot_job(api_key, title, hour, minute)
  - def create_render_keepalive(api_key)
  - def main()

### `scripts/storage_helper.py`
  - def _upload_transfer_sh(local_file_path)
  - def upload_to_supabase(local_file_path)

### `scripts/sync_cronjobs.py`
  - def list_jobs()

### `src/__init__.py`
  (scripts / configuration)

### `src/config.py`
  - class Settings [methods: ]

### `src/analytics/__init__.py`
  (scripts / configuration)

### `src/analytics/optimizer.py`
  - class AnalyticsOptimizer [methods: __init__, calculate_content_score, update_memory_with_post]

### `src/auth/__init__.py`
  (scripts / configuration)

### `src/auth/licensing.py`
  - def get_salt()
  - def get_owner_key()
  - def is_owner_key(key)
  - def generate_license(client_name, tier, days)
  - def verify_license(license_key)
  - def get_active_license_status()
  - def main()

### `src/auth/user_manager.py`
  - def get_db()
  - def hash_password(password, salt)
  - def verify_password(password, password_hash)
  - def generate_session_token(user_id, username, role)
  - def verify_session_token(token)
  - class UserManager [methods: __init__, init_db, seed_admin_user, register_user, authenticate_user, get_user_by_id, list_users, update_tier]

### `src/content/__init__.py`
  (scripts / configuration)

### `src/content/cloud_render.py`
  - def _ffmpeg()
  - def _ffprobe()
  - def _ffpath(p)
  - def _ffquote(p)
  - def ensure_anton_font(dest_dir)
  - def pexels_portrait_clips(query, count)
  - def edge_tts_synthesize(text, mp3_path, srt_path, voice)
  - def assemble_reel(clips, audio_path, srt_path, dest, audio_duration, watermark_text)
  - def render_cloud_reel(narration, subject, dest, voice)
  - def render_reel_auto(script, subject, dest, voice_name, timeout_s)

### `src/content/fact_checker.py`
  - class FactChecker [methods: verify_carousel]

### `src/content/free_knowledge_engine.py`
  - def synthesize_topic_carousel(topic, sources)
  - def get_scheduled_daily_carousel(day_index)
  - def get_rich_synthesized_carousel(topic, sources)

### `src/content/generator.py`
  - class ContentGenerator [methods: __init__, _load_prompt, _load_brand, _build_user_prompt, generate_with_gemini, _parse_json_response, generate_with_groq, generate_with_openrouter, generate_with_github_models, generate_with_cloudflare_ai, generate_with_nvidia_nim, generate_with_ollama, generate_with_openai, _normalize_carousel, generate_with_huggingface, generate_carousel, _free_narration, generate_reel_script, generate_story_content]

### `src/content/image_generator.py`
  - class ImageGenerator [methods: __init__, _enhance_prompt, generate_with_pollinations, generate_with_imagen, generate_with_dalle, generate_with_cloudflare, generate_image]

### `src/content/mpt_client.py`
  - def _mpt_base_url()
  - class MoneyPrinterTurboClient [methods: __init__, is_available, create_video, get_task, wait_for_task, download_video, render_reel]
  - def watermark_reel(video_path, text)

### `src/content/providers_manager.py`
  - class ProvidersManager [methods: __init__, _ensure_file, load_config, save_config, get_all_providers, add_or_update_custom_provider, set_active_text_model, set_active_image_model, set_active_video_model, detect_models_from_endpoint]

### `src/content/quality_gate.py`
  - class QualityGate [methods: __init__, _load_banned_phrases, evaluate]

### `src/content/script_writer.py`
  - class ScriptWriter [methods: __init__, generate_caption, generate_caption_for_topic, generate_first_comment, generate_reels_script, generate_edit_plan, generate_x_thread, generate_linkedin_post]

### `src/db/database.py`
  - class Database [methods: __init__, get_connection, init_schema, record_source, save_content_item, update_publication_status, get_recent_topics]

### `src/growth/__init__.py`
  (scripts / configuration)

### `src/growth/viral_engine.py`
  - class ViralGrowthEngine [methods: build_viral_hashtags, format_caption_with_hashtags, generate_default_caption, generate_first_comment, optimize_caption]

### `src/instagram/__init__.py`
  (scripts / configuration)

### `src/instagram/dm_automator.py`
  - class InstagramDMAutomator [methods: __init__, _init_state, _load_gate, _save_gate, is_follower_verified, mark_gate_pending, is_gate_pending, mark_gate_delivered, is_follow_claim, load_processed_comments, record_processed_comment, get_stats, fetch_recent_media_ids, fetch_comments_for_media, send_public_reply, send_private_dm, match_keyword, process_comment, _deliver_gated_blueprint, scan_and_automate]

### `src/instagram/publisher.py`
  - class InstagramPublisher [methods: __init__, dry_run, dry_run, check_publishing_limit, create_item_container, wait_until_ready, create_carousel_container, publish_media, publish_carousel, create_story_container, publish_story, create_reel_container, publish_reel, post_comment]

### `src/instagram/token_manager.py`
  - class TokenManager [methods: __init__, refresh_token]

### `src/ops/__init__.py`
  (scripts / configuration)

### `src/ops/guardian.py`
  - class SlotSkipped [methods: ]
  - def with_retries(fn, attempts, delays, sleeper)
  - def ensure_quota(check_fn, need, limit)
  - def send_alert(message)
  - def janitor(output_base, mpt_storage, output_days, mpt_hours)

### `src/research/__init__.py`
  (scripts / configuration)

### `src/research/deep_researcher.py`
  - class DeepResearcher [methods: __init__, _extract_github_repo, fetch_github_details, fetch_github_readme_snippet, extract_docker_command, research_topic]

### `src/research/fetcher.py`
  - class SourceFetcher [methods: __init__, load_seed_records, fetch_rss_feed, fetch_trending_niche_signals, fetch_github_trending, acquire_sources]

### `src/research/scorer.py`
  - class TopicScorer [methods: __init__, load_memory, score_candidate, select_best_topic]

### `src/research/trend_analyzer.py`
  - class TrendAnalyzer [methods: __init__, calculate_viral_metrics, _generate_viral_hook, filter_viral_candidates]

### `src/storage/__init__.py`
  (scripts / configuration)

### `src/storage/uploader.py`
  - class AssetUploader [methods: __init__, _upload_to_freeimage, _upload_to_catbox, _upload_to_litterbox, _upload_to_0x0, _upload_to_uguu, _upload_to_imgbb, upload_slide_images, upload_story_image, upload_video_file]

### `src/youtube/__init__.py`
  (scripts / configuration)

### `src/youtube/shorts_publisher.py`
  - class YouTubeShortsPublisher [methods: __init__, _format_title, get_credentials, upload_short]

### `tests/__init__.py`
  (scripts / configuration)

### `tests/test_auth_and_providers.py`
  - def client()
  - def test_admin_user_seeded()
  - def test_api_auth_login_success(client)
  - def test_api_auth_login_failure(client)
  - def test_api_auth_signup_and_me(client)
  - def test_api_auth_pricing(client)
  - def test_api_providers_get(client)
  - def test_api_providers_detect_models_missing_url(client)
  - def test_api_prompts_library(client)
  - def test_api_templates_catalog(client)
  - def _admin_token(client)
  - def test_api_auth_users_regression(client)
  - def test_api_admin_users_alias(client)
  - def test_api_providers_test_validation(client)
  - def test_api_generate_image_validation(client)
  - def test_api_auth_logout(client)
  - def test_api_non_admin_users_forbidden(client)
  - def test_api_providers_set_active(client)
  - def test_api_health(client)
  - def test_themes_css_landing()
  - def test_themes_css_components()
  - def test_premium_js_has_tilt()

### `tests/test_blueprint_and_gate.py`
  - def automator(tmp_path, monkeypatch)
  - def test_blueprint_keyword_matching()
  - def test_gate_first_touch_withholds_link(automator)
  - def test_verified_follower_gets_instant_dm(automator)
  - def test_gate_claim_delivers_blueprint(automator)
  - def test_foss_flow_ungated_regression(automator)
  - def test_studio_positioning_strings()
  - def test_mpt_payload_uses_anton_font()
  - def test_blueprint_assets_committed()

### `tests/test_cloud_render.py`
  - def test_pexels_missing_key_raises(monkeypatch)
  - def test_ffquote_keeps_filter_paths_colon_free()
  - def test_render_auto_prefers_mpt_when_available()
  - def test_render_auto_falls_back_to_cloud()
  - def test_assemble_filter_has_no_drive_colons(tmp_path)

### `tests/test_content_generation.py`
  - def test_source_fetcher()
  - def test_topic_scorer()
  - def test_content_generation_and_qa()
  - def test_all_six_pillars_generation()

### `tests/test_deep_research.py`
  - def test_deep_research_saas_contrast()
  - def test_deep_research_prompt_framework()
  - def test_deep_research_n8n()

### `tests/test_dm_automator.py`
  - def automator(tmp_path)
  - def test_keyword_matching(automator)
  - def test_process_comment_foss(automator)
  - def test_process_comment_prompt(automator)
  - def test_deduplication_skips_processed(automator)
  - def test_get_stats(automator)
  - def test_scan_and_automate_dry_run(automator)

### `tests/test_growth_engine.py`
  - def test_viral_hashtags_clustering()
  - def test_first_comment_generation()
  - def test_topic_aware_viral_hashtags()
  - def test_caption_and_hashtag_enforcement_in_publisher()
  - def test_api_caption_generate_endpoint()
  - def test_publish_endpoint_auto_generates_caption_and_hashtags(monkeypatch)
  - def test_webhook_autopilot_auth()

### `tests/test_guardian.py`
  - def test_with_retries_succeeds_after_two_failures()
  - def test_with_retries_reraises_after_exhaustion()
  - def test_ensure_quota_skips_and_returns()
  - def test_send_alert_falls_back_to_log(tmp_path, monkeypatch)
  - def test_janitor_removes_old_keeps_fresh(tmp_path)

### `tests/test_image_and_scripts.py`
  - def test_script_writer_caption()
  - def test_script_writer_reels_script()
  - def test_script_writer_x_thread()
  - def test_script_writer_linkedin_post()
  - def test_image_generator_prompt_enhancement()
  - def test_publisher_dry_run_and_boolean_container()
  - def test_uploader_public_cdn_fallback()
  - def test_uploader_imgbb_prioritization_and_key()
  - def test_landing_theme_picker_markup()
  - def test_three_scene_theme_reactivity()

### `tests/test_licensing.py`
  - def test_owner_key_bypass()
  - def test_missing_or_blank_key()
  - def test_client_license_generation_and_validation()
  - def test_tampered_license_signature()
  - def test_expired_license_key()
  - def test_active_environment_status()

### `tests/test_orchestrator.py`
  - def test_full_pipeline_dry_run()

### `tests/test_posting_and_scheduling.py`
  - def client()
  - def test_get_output_runs_prioritizes_dated_runs()
  - def test_api_publish_dry_run_instant(client)
  - def test_api_publish_with_custom_caption(client)
  - def test_api_schedule_execute_endpoint(client)
  - def test_api_scheduler_toggle(client)
  - def test_uploader_dry_run_and_render_fallback()
  - def test_dashboard_html_features_and_buttons()

### `tests/test_reel_pipeline.py`
  - def _test_client()
  - def test_publisher_reel_dry_run_and_container()
  - def test_reel_script_generation()
  - def test_mpt_client_unavailable_server()
  - def test_uploader_video_dry_run_fabricates_url()
  - def test_api_mpt_status_endpoint()
  - def test_api_publish_reel_endpoint_dry_run()
  - def test_publish_media_cap_guard_blocks_at_quota()
  - def test_publish_media_cap_guard_allows_headroom()
  - def test_reel_caption_promotes_agency()
  - def test_watermark_reel_burns_text(tmp_path)
  - def test_execute_queued_reel_item()

### `tests/test_reels_spec.py`
  - def test_to_ass_time_format()
  - def test_karaoke_events_highlight_each_word_once()
  - def test_publish_facade_rejects_local_paths()

### `tests/test_renderer.py`
  - def test_validate_slide_content()
  - def test_carousel_rendering(tmp_path)
  - def test_all_theme_variants_render(tmp_path)

### `tests/test_responsive_ui.py`
  - def client()
  - def test_dashboard_html_has_mobile_responsive_elements()
  - def test_dashboard_html_no_double_api_calls()
  - def test_wsgi_middleware_normalizes_double_api(client)
  - def test_synthesize_endpoint_exists(client)
  - def test_schedule_toggle_endpoint(client)

### `tests/test_run_guards.py`
  - def no_janitor_side_effects()
  - def test_story_quota_skip_returns_manifest()
  - def test_story_proceeds_with_headroom()
  - def test_run_guarded_alerts_and_reraises()
  - def test_run_guarded_passthrough_no_alert()
  - def test_run_guarded_slot_skipped_stays_silent()

### `tests/test_story_pipeline.py`
  - def client()
  - def test_publisher_story_methods()
  - def test_story_content_generation()
  - def test_story_image_rendering(tmp_path)
  - def test_schedule_json_has_seven_story_slots_and_queue()
  - def test_api_publish_story_endpoint(client)
  - def test_execute_queued_story_item(client)

### `tests/test_trend_analyzer.py`
  - def test_trend_analyzer_high_viral_scoring_saas_killer()
  - def test_trend_analyzer_high_viral_scoring_prompt_framework()
  - def test_trend_analyzer_rejects_boring_slop()
  - def test_trend_analyzer_filter_candidates()

### `tests/test_workflows_and_copilot.py`
  - def test_workflow_files_exist()
  - def test_workflow_contents()
  - def test_github_copilot_token_in_settings()
  - def test_github_models_preset_in_providers()
  - def test_github_models_missing_token_raises(monkeypatch)

### `tests/test_youtube_shorts.py`
  - def _test_client()
  - def test_youtube_shorts_publisher_dry_run()
  - def test_youtube_shorts_title_formatting()
  - def test_youtube_shorts_live_mode_missing_credentials()
  - def test_api_publish_shorts_endpoint_dry_run()
  - def test_api_publish_dual_video_endpoint_dry_run()
