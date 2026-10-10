# Reference reels: quick case study

Three reels from the creator ("Doctor Sonnanga"), all 720x1280, 30 fps, loudness about −14 LUFS.

| Reel | Length | Edit intensity | Verdict |
|---|---|---|---|
| Deep fry (`fry`) | 25.6 s | **High.** A visual change every ~1.5 s | Best of the three. This is the template to copy. |
| Skincare (`skin`) | 37.7 s | **Medium.** Branded look, split-screen lists | Good, but the captions are too thin and small |
| Reservation (`res`) | 2:27 | **Minimal.** Cold open plus one long take | Right choice for a serious topic, but has no subtitles |

---

## Shared formula (the creator's "rules")
1. **Script shape:** hook question (0–3 s) → twist ("but did you know…") → short explanation → 1–2 actionable tips → **catchphrase sign-off**: *"So health first da… doctor sonnanga la!"*
2. **Spoken Tamil + English captions.** The captions are a *translation*, not verbatim, one phrase at a time, so non-Tamil viewers can follow.
3. **Caption style:**
   - Clean geometric sans (Poppins/Montserrat-like), semi-bold.
   - 2 lines max, centred in the lower third (about 70–78% of frame height).
   - Fry reel: pale yellow with a dark outline. Skin reel: white with a soft shadow.
4. **Keyword emphasis:** one important word per line is set in a **script font** in an accent colour ("*confusing*", "*cleanse*", "*sunscreen*"), or pops up as a separate title ("*oxidation*", "*Free Radicals*") in the top area.
5. **Jump cuts with punch-ins:** retakes and pauses are removed, and the framing alternates between wide and ~110–115% scale on each new sentence. This hides the cuts and resets attention.
6. **Literal visuals for every noun:**
   - Bajji/samosa → cut-out food PNG stickers pop in.
   - "Cancer" → full-screen 3D bacteria stock clip.
   - "Reheat oil" → street-vendor frying B-roll.
   - "Brain damage" → glowing brain render.
   - "Free radicals" → virus graphics composited over the top half.
7. **No background music** in fry or skin. Voice carries everything, with light SFX accents on graphic entrances (transients at about 1.4 s and 3.6 s in fry, plus real sizzle sound under the oil B-roll at about 10.5–12 s).
8. **Sign-off branding:** the catchphrase is captioned. In the skin reel it ends on a white script logo stamp: "*Doctor sonnanga!*"

## Per-reel notes

**Fry (the strongest edit)**
- 14 visual changes in 25 s: B-roll, stickers, punch-ins and keyword titles.
- Hook at 0–3 s, B-roll pattern-interrupt at 3.5 s, payoff advice from 15 s, sign-off at 22.6 s.
- *Issue:* the long caption lines ("This will lead to brain damage…") run almost edge to edge, outside the safe zone. Wrap them into shorter lines.

**Skin**
- Strong colour identity: a magenta wall, with the accent colour matched to the caption keyword.
- For the 3-item lists (cleanse / moisturise / protect; anti-aging / pigmentation / acne), the frame switches to a **white background**:
  - Stock photo on top.
  - Speaker shrunk into a **rounded-corner card** below.
  - List word in magenta script.
- *Issues:*
  - Captions are thin and small; the script words are hard to read on magenta.
  - The grade is very contrasty and crushes the skin tones.
  - Long gaps (19–29 s) with no visual change.

**Reservation**
- **Cold open:** the emotional line from 2:01 ("they'll end up on the road… doing sex work") is repeated at the start in **black & white**, followed by a **dip to black with a beat of silence** at 3.3 s. Then the full talk plays in colour.
- One long take with a few invisible jump cuts. There's a **punch-in at 2:04.6** for the "share / repost" CTA.
- *Issue:* **no captions at all** on a 2.5-minute Tamil talk, which loses retention and non-Tamil reach. Add English subtitles and a few punch-ins on key lines (e.g. 64 s "I'm a doctor with no job", 109 s "99.9 %").

## Are they good?
- **Yes. Fry and skin are competent, modern "doctor explainer" edits.** Fast hooks, translated captions, literal B-roll and a consistent sign-off.
- They're beatable on polish:
  - bolder, safer captions;
  - a 1080x1920 export (the source is 720p);
  - SFX on every graphic hit;
  - a quiet music bed ducked under the voice;
  - no dead stretches longer than ~3 s.

## How to do it in DaVinci Resolve (free)
| Effect | How to do it in Resolve |
|---|---|
| Jump cuts | Blade (B) out the pauses and retakes. Ripple delete (Shift+Backspace). |
| Punch-in | On alternate clips: Inspector → Zoom 1.12, then nudge Position so the face stays centred. Hard cut, no animation. |
| Captions | Subtitle track or **Text+**: Poppins SemiBold, ~60 px at 1080 width, 2 lines, outline/shadow. Keep inside x 60–960, y 1150–1450. |
| Script keyword | A separate Text+ with a script font (e.g. Great Vibes) in the accent colour, placed in or above the line. |
| Sticker pop | PNG on V2. Keyframe Zoom 0 → 1.1 → 1.0 over ~6 frames. Add a "pop" SFX. |
| Full-screen B-roll | Place it on V2 over the talking head for 1–2 s while the voice continues (J/L cut). Add a whoosh at the cut. |
| Split-screen list | V1: white Solid Color. V2: stock photo cropped to the top half. V3: talking head scaled ~0.75 with a rounded rectangle mask (Fusion → Rectangle, Corner Radius). |
| B&W cold open | Copy the strongest line to the start. Color page: Saturation 0. Then 10–15 frames of black with silence. |
| Sign-off stamp | Script Text+ rotated ~−10°, Zoom pop-in. |
| SFX sources | Blackmagic's free **Fairlight Sound Library** (Fairlight → Sound Library), Pixabay SFX, Mixkit. |
| Loudness | Fairlight: target −14 LUFS (Deliver → Audio → Normalize). Same as the references. |
