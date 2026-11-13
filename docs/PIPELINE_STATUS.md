# Pipeline status

| Stage | Status | Notes |
|---|---|---|
| Scheduled cloud workflow | Implemented | Daily at 19:00 IST; manual dispatch supported |
| Story generation | Implemented | Gemini API; requires GEMINI_API_KEY |
| Structured scene plan | Implemented | Scene narration, characters, setting, action, emotion, camera, props and captions |
| Story validation | Implemented | Word count, duration, scene count, narration reconstruction and production fields |
| English narration | Integrated, unverified | Local HyperFrames/Kokoro TTS using male English voice am_michael, slowed to 0.90 |
| Portrait vector composition | Prototype | Flat geometric characters, expressions, props, warm backgrounds and GSAP timeline motion |
| HyperFrames rendering | Integrated, unverified | Standard quality preset on GitHub-hosted runner |
| Video validation | Improved basic gate | Checks MP4 exists, 30–60 s, 1080×1920 and audio stream |
| Word-level subtitles | Not implemented | Scene-level narration captions only |
| Background music / SFX | Not implemented | Requires curated, licence-verified free assets and a mix stage |
| Visual QA against reference | Not implemented | Requires rendered frame snapshots and human/reference comparison |
| YouTube publishing | Not implemented | OAuth authorization required; remains disabled |
| Instagram/Facebook publishing | Not implemented | API/account eligibility must be checked |
| Production-ready daily videos | NOT VERIFIED | Run workflow and inspect the MP4 before relying on the schedule |

The daily video workflow is .github/workflows/daily-video-draft.yml. The story-only workflow is manual-only to avoid duplicate daily generation.

The workflow intentionally does not pass a Groq key or use a paid fallback. If the Gemini free quota is exhausted, the run stops. Check current Gemini free-tier availability and quota in AI Studio. The current Kokoro voice is not an exact clone of the Reel narrator and does not provide the same Telugu-accented voice in English.
