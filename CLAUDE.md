# AI Video Studio — Rulebook

This folder is a video production studio. Every video goes through the same pipeline:
**CUT → MOTION → QA → EXPORT**. Follow it in order and don't skip the approval gates.

## Folder map

| Folder | Purpose |
|---|---|
| `footage/` | Raw clips. The user drops files here. **Never modify or delete anything in here.** |
| `brand/` | Brand kit: `BRAND.md`, `fonts/`, `logo/`. |
| `cuts/` | video-use outputs: `rough_cut.mp4` + edit decision list (`edl.json`). |
| `motion-hf/` | HyperFrames project. This is the default compositor. |
| `motion-remotion/` | Remotion project. Only for specialist components. |
| `overlays/` | Transparent renders for compositing (WebM VP9 with alpha, or ProRes 4444 `.mov`). |
| `exports/` | Final deliverables. |
| `qa/` | Sampled frames + `notes.md` per render. |

Tool locations: video-use is at `<path-to>/video-use` (skill `video-use`). Its ElevenLabs key lives in that repo's `.env`. Never ask the user to paste API keys into chat. If the key is missing, tell them to edit that file themselves.

## Rule 0: Brand first
Before generating any motion graphic (captions, titles, lower-thirds, overlays), **read `brand/BRAND.md`** and use the fonts in `brand/fonts/` and logos in `brand/logo/`.
- Never invent a font or color when `brand/` defines one.
- If a needed field is still `TODO`, ask the user rather than guessing. For throwaway tests, use neutral placeholders and say so.

## Step 1: CUT (video-use)
1. Use the `video-use` skill on `footage/`. Inventory the takes, propose a cut strategy, and wait for the user's OK. That's video-use's own rule, so follow it.
2. The rough cut is just the cut: filler and dead-air removal, audio fades at cuts, and an optional grade if requested. **Do NOT burn subtitles or add animations in video-use.** Captions and motion belong to Step 2.
3. video-use writes to `footage/edit/`. Copy the results into `cuts/`:
   - `cuts/rough_cut.mp4`
   - `cuts/edl.json` (edit decision list), plus the transcript/`takes_packed.md` if useful for captions.
4. **🛑 STOP: show the user the rough cut and wait for approval** before Step 2.

## Step 2: MOTION (HyperFrames is the default)
- **HyperFrames (`motion-hf/`) is the compositor.** `cuts/rough_cut.mp4` is the base layer. Captions, titles, transitions, zooms/punch-ins and crops/reframes are all built here. Start with the `/hyperframes` skill. Good starting workflows are `/embedded-captions` and `/talking-head-recut`, plus `/hyperframes-keyframes` for zooms.
- **Use Remotion (`motion-remotion/`) ONLY for complex components**: data viz, intricate reusable React components, or anything HyperFrames genuinely can't do well. Render those as **transparent overlays** into `overlays/` (e.g. `npx remotion render <id> ../overlays/<name>.webm --codec=vp9 --pixel-format=yuva420p`, or `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le` for `.mov`). Verify alpha with ffprobe before using it.
- HyperFrames can also render transparent overlays itself (`npx hyperframes render --format webm` / `mov`). Prefer that over Remotion for simple overlays.
- Composite overlays from `overlays/` on top of the base inside HyperFrames as a `<video class="clip" muted>` on a higher track. Both WebM VP9 alpha and ProRes 4444 `.mov` composite correctly (verified in the Phase 4 smoke test).
- Before using any video as a HyperFrames base layer, re-encode it with a keyframe every second, or seeking will stutter:
  `ffmpeg -i in.mp4 -c:v libx264 -crf 16 -r 30 -g 30 -keyint_min 30 -movflags +faststart -c:a copy out.mp4`
- Run `npx hyperframes check <dir>` before every render. One `index.html` per project folder (a second root HTML file is a lint error).

## Step 3: QA (after EVERY render, no exceptions)
1. Extract ~1 frame per second:
   `ffmpeg -i <render> -vf fps=1 qa/<render-name>/f_%03d.png`
2. Look at the frames yourself and check:
   - **Readability**: text contrast, size, nothing too small or too fast to read.
   - **Safe zones (9:16 Reels, 1080x1920)**: keep text and captions inside x 60–960 and y 250–1500. That clears the top status bar, the right-side action buttons and the bottom caption/username area. Captions sit around y ≈ 1150–1450.
   - **Timing**: captions match the spoken words (compare against the transcript timestamps). Titles land on the beat or the line they belong to.
   - **Nothing cut off**: no clipped text, logos, or faces at the frame edges, and no black bars or gaps.
   - **Audio**: no pops at cuts, levels consistent (check with `ffmpeg -af volumedetect` if in doubt).
3. Write findings to `qa/<render-name>/notes.md`. **Fix every issue and re-render before telling the user it's done.**

## Step 4: EXPORT
- Final files go to `exports/`, named `<project>_<platform>_v<N>.mp4`.
- Defaults: **Reels/Shorts/TikTok 1080x1920** (9:16), **YouTube 1920x1080** (16:9). Use H.264 + AAC, 30 fps unless the source is different.
- After export, run the QA step on the export file too.

## Step 5: HANDOFF TO DAVINCI RESOLVE (always, alongside the MP4)
The user does final edits in **DaVinci Resolve (free edition)**. Resolve free cannot be scripted from outside, so the handoff is a timeline file:
1. Render every graphics layer separately with alpha, as **ProRes 4444 `.mov`** (Resolve handles it better than WebM alpha):
   - HyperFrames graphics-only layer (captions, titles; no base video): `npx hyperframes render <dir> --format mov -o ../overlays/<name>_hf.mov`
   - Remotion components: `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le`
2. Write `exports/RESOLVE_TASKS.json` (`[{"start":s,"end":s,"note":"..."}]`, output-timeline seconds) for every Resolve task.
3. Build the timeline:
   `python tools/edl_to_fcpxml.py cuts/edl.json -o exports/<project>.fcpxml --width 1080 --height 1920 --fps 30 --layer overlays/<name>_hf.mov@0:2 --layer overlays/<x>.mov@<start>:3 --tasks exports/RESOLVE_TASKS.json`
   - V1 = original footage with every cut as a trimmable edit, V2+ = alpha graphics layers, markers = Resolve tasks.
   - The `.fcpxml` links media by absolute path, so don't move `footage/` or `overlays/` after building it.
   - Also hand over `master.srt` if there are captions (Resolve: File > Import > Subtitle).
4. Tell the user: **Resolve → File → Import → Timeline… → pick the `.fcpxml`**. If an overlay shows black instead of transparent: right-click the clip in the Media Pool → Clip Attributes → Alpha mode: Premultiplied.

## Resolve tasks (not done in code)
Footage-aware effects aren't attempted in code: **object tracking, masking, rotoscoping, sky replacement, motion-tracked text, face/object blur that follows movement.**
For these, add an entry to `exports/RESOLVE_TASKS.md` with the timecode range, what's needed, and which file. Tell the user they're DaVinci Resolve tasks.

## Known limitations
- HyperFrames composites alpha video fine (WebM VP9 and ProRes 4444 both verified), so no Resolve fallback is needed for overlays.
- Remotion WebM alpha shows as `pix_fmt=yuv420p` + `alpha_mode=1` in ffprobe. That's normal. To check real alpha, decode with `-c:v libvpx-vp9` and inspect the A channel.
- The first HyperFrames render of a session can take a few minutes (browser warm-up). Later renders take about 15s per 5s of video.
- Resolve free: no external scripting API, so the timeline is handed off via FCPXML (Step 5), never driven live.

## Environment notes (Windows)
- If `HOME` is redirected on your machine, use absolute paths rather than `~`.
- Use `python`, not `python3` (`python3` is the Microsoft Store stub).
- ffmpeg/ffprobe 8.1 are on PATH. Node 24.

