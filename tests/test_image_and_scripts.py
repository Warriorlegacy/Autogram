import pytest
from pathlib import Path
from src.content.script_writer import script_writer
from src.content.image_generator import image_generator

def test_script_writer_caption():
    sample_carousel = {
        "topic": "Why Context Caching Cuts LLM Costs",
        "pillar": "AI Tool Breakdown",
        "slides": [
            {
                "slide_number": 1,
                "headline": "How 1 API Parameter Cut Our Production Bill by 78%",
                "body": "Re-evaluating 10,000 prompt tokens on every loop is wasteful. Here is the KV-cache fix."
            },
            {
                "slide_number": 2,
                "headline": "The Hidden Cost of Static Tokens",
                "body": "Parsing system instructions over and over multiplies inference latency."
            },
            {
                "slide_number": 3,
                "headline": "Naive Re-Prompting vs Prompt Caching",
                "body": "Comparing traditional execution with cached state pointers."
            }
        ]
    }

    result = script_writer.generate_caption(sample_carousel)
    assert "caption" in result
    assert "hook" in result
    assert "hashtags" in result
    assert len(result["hashtags"]) >= 5
    assert "How 1 API Parameter Cut Our Production Bill by 78%" in result["caption"]
    assert "#AIEngineering" in result["caption"] or "#AutogramAI" in result["caption"]

def test_script_writer_reels_script():
    sample_carousel = {
        "topic": "Why Multi-Agent Orchestration Outperforms Monolithic LLMs",
        "pillar": "AI Tool Breakdown",
        "slides": [
            {
                "slide_number": 1,
                "headline": "Stop Doing Everything in One Giant Prompt",
                "body": "State management beats context stuffing."
            },
            {
                "slide_number": 2,
                "headline": "The Single-Prompt Failure Mode",
                "body": "When tasks exceed 8,000 tokens, monolithic prompts hallucinate."
            }
        ]
    }

    reel = script_writer.generate_reels_script(sample_carousel)
    assert "title" in reel
    assert "segments" in reel
    assert len(reel["segments"]) >= 4
    assert "formatted_text" in reel
    assert "HOOK" in reel["formatted_text"]
    assert "CALL TO ACTION" in reel["formatted_text"]

def test_image_generator_prompt_enhancement():
    enhanced = image_generator._enhance_prompt("A minimalist data server rack", style_preset="cyber-minimalist")
    assert "minimalist data server rack" in enhanced
    assert "dark obsidian" in enhanced
