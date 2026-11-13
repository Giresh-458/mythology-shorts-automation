# Pipeline status

| Stage | Status | Notes |
|---|---|---|
| Scheduled cloud workflow | Implemented | Daily at 19:00 IST; manual dispatch supported |
| Story generation | Implemented | Gemini API; requires GitHub secret |
| Structured scene plan | Implemented | 3–6 scenes with narration segments |
| Story validation | Implemented | Word count, duration, scene count, narration alignment |
| Visual assets | Not implemented | Reusable original SVG character system planned |
| Voice generation | Not implemented | Verify English quality, API access, commercial terms and free quota |
| HyperFrames render | Not implemented | Integrate and test CLI in GitHub runner |
| Publishing | Not implemented | YouTube OAuth and API setup required |
| Fully automated daily video | NOT READY | Do not enable publishing until all stages pass tests |

The workflow must stop safely when credentials or free quotas are unavailable. No paid fallback is permitted.
