"""Generate one original English mythology Short using Gemini, then Groq as fallback."""
from __future__ import annotations
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types
from google.genai import errors

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OUT_DIR = Path("output/stories")


def build_prompt() -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    return """
Create ONE engaging, original English-language short-form story based on a traditional
Indian mythology episode. Date: DATE_PLACEHOLDER.
Requirements:
- 30–60 seconds, approximately 80–135 spoken words.
- Respect the source tradition. Never invent a quotation and attribute it to scripture.
- Prefer an identifiable episode from the Ramayana, Mahabharata, Puranas, or a
  well-known Krishna/Hanuman/Shiva tradition.
- If details differ across traditions, do not present disputed details as universal.
- Accurate hook, clear narrative, meaningful takeaway or curiosity question.
- General audience; no graphic violence; no fabricated "secret facts".
Return JSON only:
{
 "title":"short title","tradition":"source tradition or epic","episode":"episode name",
 "fact_note":"tradition-specific detail or uncertainty",
 "narration":"complete spoken script",
 "scenes":[{"scene_number":1,"duration_seconds":8,
 "visual_description":"2D Indian puppet-animation direction",
 "narration_segment":"exact corresponding narration",
 "on_screen_text":"short caption"}],
 "closing_question":"audience engagement question"
}
Use 3–6 scenes. Total scene duration 30–60 seconds. Scene narration segments in order
must reproduce narration exactly, apart from whitespace.
""".replace("DATE_PLACEHOLDER", today)


def validate(data: dict) -> None:
    required = {"title", "tradition", "episode", "fact_note", "narration", "scenes", "closing_question"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    words = re.findall(r"\b[\w’'-]+\b", data["narration"])
    if not 65 <= len(words) <= 155:
        raise ValueError(f"Narration has {len(words)} words; expected 65–155.")
    scenes = data["scenes"]
    if not isinstance(scenes, list) or not 3 <= len(scenes) <= 6:
        raise ValueError("Expected 3–6 scenes.")
    if any(not isinstance(s.get("duration_seconds"), (int, float)) for s in scenes):
        raise ValueError("Every scene needs numeric duration_seconds.")
    duration = sum(s["duration_seconds"] for s in scenes)
    if not 30 <= duration <= 60:
        raise ValueError(f"Scene duration is {duration}s; expected 30–60s.")
    if any(not all(k in s for k in ("narration_segment", "visual_description", "on_screen_text")) for s in scenes):
        raise ValueError("Every scene needs narration_segment, visual_description and on_screen_text.")
    combined = " ".join(s["narration_segment"].strip() for s in scenes).strip()
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    if normalize(combined) != normalize(data["narration"]):
        raise ValueError("Scene narration segments do not reconstruct narration.")


def parse_and_validate(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^\`\`\`(?:json)?\s*|\s*\`\`\`$", "", text, flags=re.I)
    data = json.loads(text)
    validate(data)
    return data


def generate_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    client = genai.Client(api_key=api_key)
    transient_codes = {408, 429, 500, 502, 503, 504}
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.8,
                ),
            )
            return parse_and_validate(response.text or "")
        except errors.APIError as exc:
            code = getattr(exc, "code", None)
            if code not in transient_codes or attempt == 4:
                raise
            delay = min(60, 8 * (2 ** attempt))
            print(f"Gemini temporary error HTTP {code}; retry {attempt + 1}/4 in {delay}s.", flush=True)
            time.sleep(delay)


def generate_groq(prompt: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured; cannot use Groq fallback.")
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You write careful, source-respectful Indian mythology stories. Return only valid JSON matching the requested schema."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1500]
        raise RuntimeError(f"Groq API HTTP {exc.code}: {detail}") from exc
    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError("Groq returned no completion choices.")
    return parse_and_validate(choices[0].get("message", {}).get("content", ""))


def main() -> int:
    prompt = build_prompt()
    data = None
    provider = None
    gemini_error = None
    if os.getenv("GEMINI_API_KEY"):
        try:
            print(f"Generating story with Gemini ({GEMINI_MODEL})...", flush=True)
            data = generate_gemini(prompt)
            provider = "Gemini"
        except Exception as exc:
            gemini_error = exc
            print(f"Gemini failed: {exc}. Trying Groq fallback...", file=sys.stderr, flush=True)
    else:
        gemini_error = RuntimeError("GEMINI_API_KEY is not configured.")
        print("Gemini key absent; trying Groq fallback.", flush=True)

    if data is None:
        if not os.getenv("GROQ_API_KEY"):
            print(f"ERROR: No story provider succeeded. Gemini: {gemini_error}. Add GROQ_API_KEY to GitHub Actions secrets to enable fallback.", file=sys.stderr)
            return 4
        try:
            print(f"Generating story with Groq ({GROQ_MODEL})...", flush=True)
            data = generate_groq(prompt)
            provider = "Groq"
        except Exception as exc:
            print(f"ERROR: Groq fallback also failed: {exc}", file=sys.stderr)
            return 5

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"story-{datetime.now(timezone.utc):%Y%m%d}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated story draft saved: {path}")
    print(f"Provider: {provider}; title: {data['title']}; scenes: {len(data['scenes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
