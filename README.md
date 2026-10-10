# AI Video Editor

An agent-driven video production studio. Drop raw footage in, and a fixed pipeline cuts it, adds
motion graphics, checks the result frame by frame, and hands you an MP4 **plus** an editable
DaVinci Resolve timeline.

```
footage/ ──► CUT ──► MOTION ──► QA ──► EXPORT ──► RESOLVE HANDOFF
            video-use  HyperFrames  frame     H.264/AAC   .fcpxml + alpha
            (EDL)      / Remotion   sampling  1080x1920   overlays
```

## Why it exists

Short-form editing is repetitive: remove filler, add captions, add a title, check safe zones,
export, then fix things by hand in a real editor. This repo encodes that workflow as rules an AI
coding agent follows, with human approval gates, so every video goes through the same checks.

## What's in the repo

| Path | Purpose |
|---|---|
| `CLAUDE.md` | The studio rulebook the agent follows (pipeline, approval gates, safe zones, QA checklist). |
| `brand/` | Brand kit: `BRAND.md` (colors, fonts, caption style) and font files. The agent reads this before generating any graphic. |
| `motion-hf/` | HyperFrames (HTML-based video compositor) project, the default compositor for captions, titles and zooms. |
| `motion-remotion/` | [Remotion](https://www.remotion.dev) project for complex React components rendered as transparent overlays. |
| `tools/edl_to_fcpxml.py` | Converts a cut list (EDL) plus overlay renders into a DaVinci Resolve-importable `.fcpxml` timeline. |
| `tools/el_audio.py` | Generates sound effects and music beds with the ElevenLabs API. |
| `research/` | Reference-reel analysis used to choose pacing and style. |
| `qa/`, `footage/`, `cuts/`, `exports/`, `overlays/` | Working folders (contents are git-ignored). |

## Pipeline details

1. **Cut**: transcribe, remove filler and dead air, add audio fades at cut points. Output is a rough cut plus an `edl.json`. The agent stops here for approval.
2. **Motion**: HyperFrames composites captions, titles, zooms and overlays on top of the rough cut. Remotion is used only for components HyperFrames cannot do well.
3. **QA**: after every render, one frame per second is sampled and checked for readability, 9:16 safe zones, caption timing, clipped content and audio levels.
4. **Export**: `<project>_<platform>_v<N>.mp4`, H.264 + AAC, 30 fps, 1080x1920 for Reels/Shorts/TikTok.
5. **Handoff**: `edl_to_fcpxml.py` builds a timeline with every cut trimmable on V1, graphics on V2+, and markers for work that can't be automated (tracking, masking, roto).

## Quick start

Requirements: Node 20+, Python 3.10+, `ffmpeg` and `ffprobe` on PATH.

```bash
# Build a Resolve timeline from a cut list
python tools/edl_to_fcpxml.py cuts/edl.json -o exports/my_video.fcpxml \
    --width 1080 --height 1920 --fps 30 \
    --layer overlays/captions_hf.mov@0:2

# Preview / check / render the HyperFrames compositor
cd motion-hf
npm run dev
npm run check
npm run render

# Remotion components
cd motion-remotion
npm install
npm run dev
```

Optional audio generation:

```bash
export ELEVENLABS_API_KEY=...        # never commit this
python tools/el_audio.py audio_spec.json
```

`audio_spec.json` format:

```json
{
  "sfx":   [{"text": "soft whoosh", "dur": 1.2, "out": "overlays/whoosh.mp3"}],
  "music": [{"prompt": "calm lo-fi bed", "ms": 30000, "out": "overlays/bed.mp3"}]
}
```

## Design decisions

- **Rules as code-adjacent docs.** `CLAUDE.md` is the contract, so a different agent or a human follows the same pipeline.
- **HyperFrames by default, Remotion by exception.** Fewer moving parts for the common case.
- **Resolve handoff via FCPXML.** Resolve free has no external scripting API, so the timeline file is the integration point.
- **Never automate footage-aware effects.** Tracking, masking and roto are listed as Resolve tasks instead of faked.

## Limitations

- Depends on the external `video-use` skill for the cut step (not bundled).
- First HyperFrames render in a session is slow while the headless browser warms up.
- Raw footage and renders are intentionally not included in this repo.

## License

MIT

