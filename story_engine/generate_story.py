"""Generate one original English mythology Short script as validated JSON."""
from __future__ import annotations
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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
    combined = " ".join(s["narration_segment"].strip() for s in scenes).strip()
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    if normalize(combined) != normalize(data["narration"]):
        raise ValueError("Scene narration segments do not reconstruct narration.")


def main() -> int:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Configure GEMINI_API_KEY in GitHub Actions secrets.", file=sys.stderr)
        return 2
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=build_prompt(),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )
    try:
        data = json.loads(response.text or "")
        validate(data)
    except Exception as exc:
        print(f"ERROR: Story response failed validation: {exc}", file=sys.stderr)
        print(response.text or "<empty response>", file=sys.stderr)
        return 3
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"story-{datetime.now(timezone.utc):%Y%m%d}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated story draft saved: {path}")
    print(f"Title: {data['title']}; scenes: {len(data['scenes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
