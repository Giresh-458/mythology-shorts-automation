# Mythology Shorts Automation

Cloud-first project for original English-language Indian mythology Shorts.

## Current status

**Stage 1 (story drafts) is scaffolded.** This is not yet a complete video factory: visuals, voice generation, animation/rendering, quality checks, and publishing still need to be implemented and tested.

## Design goals

- One original English mythology Short per day (initial target: 30–60 seconds)
- Daily scheduled execution using GitHub Actions
- No local rendering on the creator's computer
- No paid APIs; workflows must stop rather than incur charges
- Original scripts, meaningful creative variation, and careful treatment of source traditions
- Never publish automatically until the complete pipeline passes quality checks

## Stage 1: Generate a story draft

1. Create a Gemini API key in Google AI Studio.
2. In this repository, open **Settings → Secrets and variables → Actions → New repository secret**.
3. Name it `GEMINI_API_KEY` and paste the key as its value.
4. Open **Actions → Daily story draft → Run workflow** to test manually.
5. The scheduled workflow runs daily at 13:30 UTC (19:00 India Standard Time).
6. Download the generated JSON story from the workflow run's Artifacts section.

If the key is missing or the API quota is exhausted, the workflow stops. There is no paid fallback.

## Required GitHub secret

- `GEMINI_API_KEY`: store only as a GitHub Actions secret. Never put it in source code, commits, screenshots, or chat.
- `GROQ_API_KEY`: optional backup provider key, stored only as a GitHub Actions secret. If Gemini exhausts its retry policy, the script tries Groq. The backup only works if your Groq account has access to the configured model (`openai/gpt-oss-120b`) and available quota.

To enable Groq fallback, create a key at https://console.groq.com/keys and add a repository secret named `GROQ_API_KEY` under **Settings → Secrets and variables → Actions**. Do not paste the key into chat or commit it. The workflow never switches to a paid provider automatically; check your Groq plan and limits before use.

The Gemini API free tier has model-specific rate limits and terms. A free quota is not unlimited and may change. Check the current Google AI Studio terms before using generated content commercially.

## Roadmap

- [x] Scheduled cloud workflow
- [x] Structured English story and scene-plan generation
- [x] Basic script validation
- [ ] Original reusable SVG puppet characters and backgrounds
- [ ] English text-to-speech with verified commercial-use terms
- [ ] HyperFrames rendering on a GitHub-hosted runner
- [ ] Audio, subtitle, and video quality checks
- [ ] YouTube OAuth upload (private test first)
- [ ] Optional Instagram/Facebook publishing if account/API eligibility permits

## Important

The repository currently generates **story drafts only**, not finished videos. Do not enable automatic publishing until every stage is implemented and tested. Monetization is not guaranteed; use original scripts and visuals and comply with each platform's monetization policies.
