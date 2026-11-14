from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "video_engine" / "build_composition.py"


class CompositionBuilderTests(unittest.TestCase):
    def test_builds_vertical_reel_inspired_composition(self) -> None:
        story = {
            "title": "Hanuman's Great Leap",
            "closing_question": "What gives Hanuman his strength?",
            "scenes": [
                {
                    "duration_seconds": 12,
                    "visual_description": "Hanuman stands on a mountain cliff overlooking the ocean.",
                    "characters": ["Hanuman"],
                    "setting": "mountain cliff",
                    "action": "Hanuman prepares to leap",
                    "emotion": "determined",
                    "camera": "gentle_push",
                    "props": ["mace"],
                    "narration_segment": "Hanuman stood at the edge of the mountain.",
                    "on_screen_text": "A mighty promise",
                },
                {
                    "duration_seconds": 12,
                    "visual_description": "Hanuman flies above the wide blue ocean.",
                    "characters": ["Hanuman"],
                    "setting": "ocean",
                    "action": "Hanuman leaps and flies across the waves",
                    "emotion": "determined",
                    "camera": "pan_right",
                    "props": ["ocean waves"],
                    "narration_segment": "Then he leapt across the endless sea.",
                    "on_screen_text": "The great leap",
                },
                {
                    "duration_seconds": 12,
                    "visual_description": "Hanuman sees the golden city of Lanka on the horizon.",
                    "characters": ["Hanuman"],
                    "setting": "Lanka palace",
                    "action": "Hanuman looks toward the distant city",
                    "emotion": "reverent",
                    "camera": "wide",
                    "props": ["golden palace"],
                    "narration_segment": "At last, Lanka appeared before him.",
                    "on_screen_text": "Lanka at last",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            story_path = root / "story.json"
            audio_path = root / "narration.wav"
            story_path.write_text(json.dumps(story), encoding="utf-8")
            audio_path.write_bytes(b"")
            subprocess.run(
                [sys.executable, str(BUILDER), str(story_path), str(audio_path)],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            html = (root / "video" / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-width="1080"', html)
        self.assertIn('data-height="1920"', html)
        self.assertIn('data-duration="36.000"', html)
        self.assertIn('data-composition-id="mythology-short"', html)
        self.assertIn("Hanuman", html)
        self.assertIn("The great leap", html)
        self.assertIn('window.__timelines["mythology-short"]', html)
        self.assertIn('class="caption"', html)
        self.assertIn('class="prop"', html)
        self.assertIn('rotation:-2', html)
        self.assertIn('rotation:-42', html)
        self.assertIn('rotation:42', html)
        self.assertIn('scale:0.94', html)


if __name__ == "__main__":
    unittest.main()
