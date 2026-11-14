# Mythology Shorts Automation

Cloud-first prototype for original English-language Indian mythology Shorts.

## Current implementation

The repository currently contains:
- Gemini-based story and scene-plan generation.
- Structured scene validation.
- A Python-generated, vertical 2D vector cut-out composition for HyperFrames.
- Local Kokoro text-to-speech through the HyperFrames CLI.
- A scheduled GitHub Actions workflow that renders a draft MP4 and uploads it as an artifact.

The composition is a **procedural vector-animation prototype**, not yet a finished equivalent of the Instagram reference. It uses reusable geometric character parts, scene-specific vector backgrounds, simple expressions, props, camera moves and timeline animation. It does not yet provide a professionally hand-authored rig library, true word-level subtitle timing, a curated music/SFX mix, or visual QA against reference frames.

## Visual reference direction

The target is the provided Reel's flat geometric 2D cut-out style:
- Warm golden/cream palette and radial sunburst staging.
- Rounded character silhouettes, large expressive eyes and simple mouth shapes.
- Separate character limbs and props animated with eased joint/transform motion.
- Palace/courtyard staging, foreground props and concise top/bottom text.
- Warm, clear, measured mythological narration.

The English narrator is currently Kokoro am_michael at a slower pace. This is a free local male English voice, **not the same speaker or accent as the Telugu narrator in the reference**. The current Kokoro voice inventory does not provide a Telugu-accented English voice.

## Daily workflow

The scheduled workflow runs at 13:30 UTC (19:00 India Standard Time). It:
1. Generates and validates a story using GEMINI_API_KEY.
2. Creates English narration locally using HyperFrames' bundled Kokoro TTS.
3. Builds the HyperFrames composition.
4. Lints and renders a 1080 × 1920 MP4.
5. Checks duration, dimensions and audio stream.
6. Uploads the MP4 and source files as a GitHub Actions artifact.

To test manually, open **Actions → Daily mythology video draft → Run workflow**.

## Required secret

- GEMINI_API_KEY: create a key in Google AI Studio and store it under **Settings → Secrets and variables → Actions**. Never commit or share the key.

The workflow intentionally does not pass a Groq key or configure a paid fallback. If Gemini's free quota is exhausted, the run stops rather than switching providers or incurring charges. Gemini free-tier access and limits are model/account dependent and can change; verify the current AI Studio quota before relying on daily generation.

## Free cloud execution

The repository is public and uses the standard ubuntu-latest GitHub-hosted runner. Standard runners are free for public repositories under GitHub's current Actions policy. The runner has CPU resources, not a dedicated GPU. Kokoro TTS and HyperFrames rendering run locally on the runner.

## Current limitations — do not treat as production-ready

- Procedural SVG art cannot yet match every handcrafted detail in the reference.
- Character rigs and expression/action vocabulary are still limited.
- Scene selection is keyword-driven and needs stronger semantic mapping.
- Narration voice is a male English Kokoro voice, not an exact voice clone.
- Word-level subtitle synchronisation, licensed background music and scene-specific sound effects remain to be implemented.
- Current CI tests validate generated composition structure; a real rendered MP4 still needs visual review.

No automatic publishing is enabled. Monetisation is not guaranteed; use original scripts/assets and comply with platform policies.
