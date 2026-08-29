# OTTAM Autonomous Production

Production-grade, resumable, zero-touch YouTube video factory.

## Goals
- Scheduled topic discovery through publication
- No manual command sequencing
- FFmpeg rendering instead of DaVinci/FCPXML in normal production
- Kokoro TTS on Modal
- Resumable per-stage state
- Deterministic recovery first, AI-assisted repair second
- Quarantine unrecoverable episodes without blocking publishing cadence
- YouTube upload/scheduling via API

## Initial pipeline
`DISCOVER_TOPIC -> RESEARCH -> FACT_CHECK -> WRITE_SCRIPT -> SCRIPT_QA -> TTS -> ALIGN -> STORYBOARD -> VISUALS -> VISUAL_QA -> ASSEMBLE -> VIDEO_QA -> THUMBNAIL -> METADATA -> PUBLISH`

## Development status
Foundation scaffold only. External providers remain disabled until their credentials/contracts are configured.
