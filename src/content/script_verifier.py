"""
Strict spoken-script verifier (Makerzz P3 gate).

The spoken script MUST be a plain verbal file. It must NOT contain:
  - bracket section tags       [HOOK] [CTA] [BEAT 1]
  - parenthetical directions   (pause) (smile)
  - timecodes                  00:14  0:14  1:02:33
  - markdown                   **bold** ## Header - bullet
  - emoji (any non-text pictographs)
  - "Beat N:" / "CTA:" style labels

The verifier is FAIL-CLOSED: if the script fails, the caller must regenerate
via the LLM with precise feedback — never silently strip markers post-hoc.

Also validates spoken cadence: <= 2.5 words per second of estimated read time
(~15 characters per second for English TTS pacing).
"""

import re
from dataclasses import dataclass, field

MAX_WORDS_PER_SECOND = 2.5
CHARS_PER_SECOND = 15  # approximate TTS pacing baseline

# Bracket section tags: [HOOK], [CTA], [BEAT 1], [SCENE], etc.
_BRACKET_TAG = re.compile(r"\[[A-Za-z0-9 #_\-']+\]")

# Parenthetical stage directions: (pause), (smile), (beat) ...
_PAREN_DIRECTION = re.compile(r"\((?:[a-zA-Z ]{2,30})\)")

# Timecodes: 00:14, 0:14, 1:02:33
_TIMECODE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")

# Markdown artifacts
_MD_BOLD = re.compile(r"\*\*[^*\n]+\*\*")
_MD_ITALIC = re.compile(r"(?<!\*)\*[^*\n]+\*(?!\*)")
_MD_HEADER = re.compile(r"^#{1,6}\s", re.MULTILINE)
_MD_BULLET = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_MD_LINK = re.compile(r"\[[^\]]+\]\([^)]+\)")

# "Beat 1:" / "CTA:" / "HOOK:" label lines
_LABEL_LINE = re.compile(r"^\s*(?:beat|cta|hook|scene|intro|outro)\s*\d*\s*:\s*$", re.IGNORECASE | re.MULTILINE)

# Emoji / pictographs (Unicode ranges)
_EMOJI = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F000-\U0001F02F"
    "\U00002600-\U000026FF"
    "\U0001F900-\U0001F9FF"
    "\uFE0F"
    "\u2764"
    "]+"
)


@dataclass
class ScriptVerification:
    """Result of the P3 script gate. Persisted as script_verification.json."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    word_count: int = 0
    estimated_seconds: float = 0.0
    words_per_second: float = 0.0
    cadence_ok: bool = True
    clean_text: str = ""

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": self.violations,
            "word_count": self.word_count,
            "estimated_seconds": round(self.estimated_seconds, 2),
            "words_per_second": round(self.words_per_second, 3),
            "cadence_ok": self.cadence_ok,
        }


def verify_script(text: str, max_words_per_second: float = MAX_WORDS_PER_SECOND) -> ScriptVerification:
    """Run the full P3 verifier against a spoken script. FAIL-CLOSED."""
    violations: list[str] = []

    if not text or not text.strip():
        return ScriptVerification(
            passed=False,
            violations=["Script is empty."],
            cadence_ok=False,
        )

    # 1. Bracket section tags
    for m in _BRACKET_TAG.finditer(text):
        violations.append(f"Bracket section tag found: {m.group(0)!r}")

    # 2. Parenthetical stage directions
    for m in _PAREN_DIRECTION.finditer(text):
        violations.append(f"Stage direction found: {m.group(0)!r}")

    # 3. Timecodes
    for m in _TIMECODE.finditer(text):
        violations.append(f"Timecode found: {m.group(0)!r}")

    # 4. Markdown
    for m in _MD_BOLD.finditer(text):
        violations.append(f"Markdown bold found: {m.group(0)!r}")
    for m in _MD_ITALIC.finditer(text):
        # Skip single asterisks that are likely multiplication/footnote in prose
        token = m.group(0)
        if re.fullmatch(r"\*[\w .,!?'-]+\*", token):
            violations.append(f"Markdown italic found: {token!r}")
    for m in _MD_HEADER.finditer(text):
        violations.append("Markdown header found (## ...)")
    for m in _MD_BULLET.finditer(text):
        violations.append("Markdown bullet list found ('- ' line)")
    for m in _MD_LINK.finditer(text):
        violations.append(f"Markdown link found: {m.group(0)!r}")

    # 5. Label lines (Beat 1:, CTA:, ...)
    for m in _LABEL_LINE.finditer(text):
        violations.append(f"Section label line found: {m.group(0).strip()!r}")

    # 6. Emoji
    for m in _EMOJI.finditer(text):
        violations.append(f"Emoji/pictograph found: {m.group(0)!r}")

    # 7. Cadence check (spoken speed <= 2.5 words/second)
    clean = _strip_speakers(text)
    words = re.findall(r"[A-Za-z0-9'’\-]+", clean)
    word_count = len(words)
    estimated_seconds = max(1.0, len(clean) / CHARS_PER_SECOND)
    wps = word_count / estimated_seconds
    cadence_ok = wps <= max_words_per_second
    if not cadence_ok:
        violations.append(
            f"Spoken cadence too fast: {wps:.2f} words/sec exceeds max {max_words_per_second}"
        )

    return ScriptVerification(
        passed=len(violations) == 0,
        violations=violations,
        word_count=word_count,
        estimated_seconds=estimated_seconds,
        words_per_second=wps,
        cadence_ok=cadence_ok,
        clean_text=text.strip(),
    )


def _strip_speakers(text: str) -> str:
    """Remove 'Speaker:' prefixes only for cadence math (not a violation)."""
    return re.sub(r"^\s*[A-Z][A-Za-z ]{0,30}:\s*", "", text, flags=re.MULTILINE)


def build_retry_feedback(violations: list[str]) -> str:
    """Precise feedback for the LLM to regenerate a compliant script."""
    rules = "\n".join(f"- {v}" for v in violations[:20])
    return (
        "The previous spoken script was REJECTED by the strict verifier.\n"
        "Violations found:\n"
        f"{rules}\n\n"
        "Rewrite the script as PURE spoken text:\n"
        "  - No bracket tags like [HOOK] or [CTA]\n"
        "  - No stage directions like (pause)\n"
        "  - No timecodes, no markdown, no emoji, no 'Beat 1:' labels\n"
        "  - Natural conversational sentences only, spoken aloud verbatim\n"
    )
