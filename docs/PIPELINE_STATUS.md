# Pipeline status

| Stage | Status | Notes |
|---|---|---|
| Scheduled cloud workflow | Implemented | Daily at 19:00 IST; manual dispatch supported |
| Story generation | Implemented | Gemini API; requires GitHub secret |
| Structured scene plan | Implemented | 3–6 scenes with narration segments |
| Story validation | Implemented | Word count, duration, scene count, narration alignment |
| English narration | Integrated, unverified | HyperFrames CLI TTS voice `af_nova`; test and verify voice/model license for monetized use |
| Portrait animation composition | Implemented, unverified | Reusable stylized puppet illustration with scene transitions |
| HyperFrames rendering | Integrated, unverified | Runs on GitHub-hosted runner; runner quota and runtime apply |
| Video validation | Basic | Checks file exists and ffprobe can read duration |
| YouTube publishing | Not implemented | OAuth authorization required; remains disabled |
| Instagram/Facebook publishing | Not implemented | API/account eligibility must be checked |
| Production-ready daily videos | NOT VERIFIED | Run workflow manually and inspect the MP4 before enabling scheduled use |

The daily video workflow is `.github/workflows/daily-video-draft.yml`. The story-only workflow is manual-only to avoid duplicate daily generation.

No paid fallback is configured. If API quota is exhausted, TTS fails, or rendering fails, the workflow stops. Check TTS model/voice and asset licenses before commercial monetization.
