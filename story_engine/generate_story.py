"""Generate one original English mythology Short with Gemini only; never switch providers."""
from __future__ import annotations
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types
from google.genai import errors

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
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
- Visual direction is critical: every scene must depict a DIFFERENT, specific moment from the narration.
- Name every visible character explicitly (e.g. Hanuman, Rama, Sita, Ravana); never say only "a hero" or "a figure".
- State the exact setting (ocean, Ashoka grove, palace, forest, mountain, battlefield, etc.) and a visible physical action/pose.
- Match the analysed reference: clean flat 2D vector cut-out animation, rounded geometric character silhouettes, large expressive eyes, simple readable mouth shapes, warm golden/cream palette, ornate palace/courtyard staging, foreground props and gentle camera movement.
- Include visual details that distinguish characters: clothing colours, crowns, jewellery, weapons/props, expressions and gestures.
- Give each scene a distinct physical action and readable pose. Do not reuse the same pose, camera framing, or background in consecutive scenes.
- Keep visual_description concise but concrete enough for a vector illustrator to draw; avoid abstract phrases such as "devotion shines" or "a powerful moment".
Return JSON only:
{
 "title":"short title","tradition":"source tradition or epic","episode":"episode name",
 "fact_note":"tradition-specific detail or uncertainty",
 "narration":"complete spoken script",
 "scenes":[{"scene_number":1,"duration_seconds":8,
 "visual_description":"specific flat 2D vector cut-out animation frame: named characters, rounded geometric silhouettes, setting, visible action, pose, costume, expression and props",
 "characters":["explicit character names"],"setting":"specific place","action":"visible physical action",
 "narration_segment":"exact corresponding narration",
 "emotion":"one of calm, happy, surprised, determined, sad, reverent",
 "camera":"one of gentle_push, pan_left, pan_right, wide, close_up",
 "props":["specific visible prop names; empty array if none"],
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
    scene_fields = ("narration_segment", "visual_description", "on_screen_text", "characters", "setting", "action", "emotion", "camera", "props")
    if any(not all(k in s for k in scene_fields) for s in scenes):
        raise ValueError(f"Every scene needs these production fields: {scene_fields}.")
    allowed_emotions = {"calm", "happy", "surprised", "determined", "sad", "reverent"}
    allowed_cameras = {"gentle_push", "pan_left", "pan_right", "wide", "close_up"}
    if any(s["emotion"] not in allowed_emotions for s in scenes):
        raise ValueError("Scene emotion must be one of the documented values.")
    if any(s["camera"] not in allowed_cameras for s in scenes):
        raise ValueError("Scene camera must be one of the documented values.")
    if any(not isinstance(s["characters"], list) or not isinstance(s["props"], list) for s in scenes):
        raise ValueError("Scene characters and props must be JSON arrays.")
    if any(len(str(s.get("visual_description", "")).split()) < 8 for s in scenes):
        raise ValueError("Every scene needs a concrete, drawable visual description.")
    combined = " ".join(s["narration_segment"].strip() for s in scenes).strip()
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    if normalize(combined) != normalize(data["narration"]):
        raise ValueError("Scene narration segments do not reconstruct narration.")


def parse_and_validate(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
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


def main() -> int:
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is not configured. No provider fallback is enabled.", file=sys.stderr)
        return 4
    try:
        print(f"Generating story with Gemini ({GEMINI_MODEL})...", flush=True)
        data = generate_gemini(build_prompt())
    except Exception as exc:
        print(f"ERROR: Gemini story generation failed: {exc}", file=sys.stderr, flush=True)
        return 5

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"story-{datetime.now(timezone.utc):%Y%m%d}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Validated story draft saved: {path}")
    print(f"Provider: Gemini; title: {data['title']}; scenes: {len(data['scenes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
