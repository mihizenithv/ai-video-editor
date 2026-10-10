"""Build a DaVinci Resolve-importable FCPXML timeline from a video-use EDL.

V1 (spine)  : original footage, one clip per EDL range (cut points stay trimmable in Resolve)
V2+ (lanes) : graphics layers (HyperFrames renders, Remotion alpha overlays), placed at output time
Markers     : "Resolve tasks" (tracking / masking / roto) and any notes

Usage:
  python tools/edl_to_fcpxml.py cuts/edl.json -o exports/<name>.fcpxml \
      [--width 1080 --height 1920 --fps 30] \
      [--layer path.mov@START[:LANE]] ...        # extra overlay, START in output seconds
      [--marker START:"note"] ...                 # extra marker
      [--tasks exports/RESOLVE_TASKS.json]        # [{"start":s,"end":s,"note":"..."}]

Without an EDL (e.g. for a flat render), pass --base path.mp4 instead of the EDL path.
Import in Resolve: File > Import > Timeline... > pick the .fcpxml (free and Studio both work).
"""
import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape, quoteattr


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    num, den = (v["r_frame_rate"].split("/") if v else ("30", "1"))
    return {
        "duration": float(info["format"]["duration"]),
        "width": int(v["width"]) if v else 0,
        "height": int(v["height"]) if v else 0,
        "fps": Fraction(int(num), int(den)),
        "audio": has_audio,
    }


def file_url(path: Path) -> str:
    return "file:///" + quote(path.resolve().as_posix(), safe="/:")


class Timeline:
    def __init__(self, width, height, fps):
        self.fps = Fraction(fps).limit_denominator(1001)
        self.frame = 1 / self.fps
        self.width, self.height = width, height
        self.formats = {}  # (w,h,fps) -> id
        self.assets = {}   # path -> (id, probe)
        self.fmt_id(width, height, self.fps)

    def t(self, seconds) -> str:
        """Seconds -> frame-aligned rational time string."""
        frames = round(Fraction(seconds) / self.frame) if not isinstance(seconds, Fraction) else round(seconds / self.frame)
        r = frames * self.frame
        return f"{r.numerator}/{r.denominator}s" if r.denominator != 1 else f"{r.numerator}s"

    def frames(self, seconds):
        return round(Fraction(seconds).limit_denominator(100000) / self.frame)

    def fmt_id(self, w, h, fps):
        key = (w, h, fps)
        if key not in self.formats:
            self.formats[key] = f"r{len(self.formats) + 1}"
        return self.formats[key]

    def asset(self, path: Path):
        path = path.resolve()
        if path not in self.assets:
            if not path.exists():
                sys.exit(f"missing media: {path}")
            p = probe(path)
            fid = self.fmt_id(p["width"], p["height"], p["fps"])
            self.assets[path] = (f"a{len(self.assets) + 1}", p, fid)
        return self.assets[path]

    def resources_xml(self):
        out = []
        for (w, h, fps), fid in self.formats.items():
            fd = 1 / fps
            out.append(f'    <format id="{fid}" frameDuration="{fd.numerator}/{fd.denominator}s" width="{w}" height="{h}"/>')
        for path, (aid, p, fid) in self.assets.items():
            out.append(
                f'    <asset id="{aid}" name={quoteattr(path.name)} start="0s" duration="{self.t(p["duration"])}" '
                f'hasVideo="1" hasAudio="{1 if p["audio"] else 0}" format="{fid}">\n'
                f'      <media-rep kind="original-media" src={quoteattr(file_url(path))}/>\n'
                f'    </asset>')
        return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", nargs="?", help="video-use edl.json")
    ap.add_argument("--base", help="single flat video for V1 instead of an EDL")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--fps", default="30")
    ap.add_argument("--layer", action="append", default=[], help="path@start[:lane]")
    ap.add_argument("--marker", action="append", default=[], help='start:"note"')
    ap.add_argument("--tasks", help="JSON list of {start,end,note} Resolve tasks")
    a = ap.parse_args()

    tl = Timeline(a.width, a.height, Fraction(a.fps))

    # ---- V1 spine
    spine = []  # (asset_id, src_in, out_offset, dur, name)
    if a.edl:
        edl_path = Path(a.edl).resolve()
        edl = json.loads(edl_path.read_text(encoding="utf-8"))
        cursor = 0
        for r in edl["ranges"]:
            src = Path(edl["sources"][r["source"]])
            if not src.is_absolute():
                src = edl_path.parent / src
            aid, p, _ = tl.asset(src)
            dur_f = tl.frames(r["end"]) - tl.frames(r["start"])
            spine.append((aid, tl.frames(r["start"]), cursor, dur_f, r.get("beat") or r["source"]))
            cursor += dur_f
        layers = [(Path(o["file"]) if Path(o["file"]).is_absolute() else edl_path.parent.parent / o["file"],
                   o["start_in_output"], 2) for o in edl.get("overlays", [])]
    elif a.base:
        aid, p, _ = tl.asset(Path(a.base))
        spine.append((aid, 0, 0, tl.frames(p["duration"]), Path(a.base).stem))
        layers = []
    else:
        sys.exit("pass an edl.json or --base")

    for spec in a.layer:
        path, _, rest = spec.rpartition("@")
        start, _, lane = rest.partition(":")
        layers.append((Path(path), float(start), int(lane or 1)))

    markers = []
    for m in a.marker:
        s, _, note = m.partition(":")
        markers.append((float(s), 0.0, note.strip('"')))
    if a.tasks:
        for task in json.loads(Path(a.tasks).read_text(encoding="utf-8")):
            markers.append((task["start"], task.get("end", task["start"]) - task["start"],
                            "RESOLVE TASK: " + task["note"]))

    total = sum(s[3] for s in spine)

    def owner(out_frame):
        for i, (_, src_in, off, dur, _) in enumerate(spine):
            if off <= out_frame < off + dur:
                return i
        return len(spine) - 1

    children = {i: [] for i in range(len(spine))}
    for path, start, lane in layers:
        aid, p, _ = tl.asset(path)
        sf = tl.frames(start)
        i = owner(sf)
        _, src_in, off, _, _ = spine[i]
        local = (src_in + (sf - off)) * tl.frame  # connected-clip offset lives in parent's source time
        children[i].append(
            f'          <asset-clip ref="{aid}" lane="{lane}" offset="{tl.t(local)}" start="0s" '
            f'duration="{tl.t(p["duration"])}" name={quoteattr(path.name)}/>')
    for start, dur, note in markers:
        sf = tl.frames(start)
        i = owner(sf)
        _, src_in, off, _, _ = spine[i]
        local = (src_in + (sf - off)) * tl.frame
        d = max(tl.frames(dur), 1) * tl.frame
        children[i].append(f'          <marker start="{tl.t(local)}" duration="{tl.t(d)}" value={quoteattr(note)}/>')

    clips = []
    for i, (aid, src_in, off, dur, name) in enumerate(spine):
        attrs = (f'ref="{aid}" offset="{tl.t(off * tl.frame)}" start="{tl.t(src_in * tl.frame)}" '
                 f'duration="{tl.t(dur * tl.frame)}" name={quoteattr(name)}')
        if children[i]:
            clips.append(f"        <asset-clip {attrs}>\n" + "\n".join(children[i]) + "\n        </asset-clip>")
        else:
            clips.append(f"        <asset-clip {attrs}/>")

    name = a.name or Path(a.output).stem
    seq_fmt = tl.formats[(a.width, a.height, tl.fps)]
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.10">
  <resources>
{tl.resources_xml()}
  </resources>
  <library>
    <event name={quoteattr(name)}>
      <project name={quoteattr(name)}>
        <sequence format="{seq_fmt}" duration="{tl.t(total * tl.frame)}" tcStart="0s" tcFormat="NDF">
          <spine>
{chr(10).join(clips)}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
"""
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(xml, encoding="utf-8")
    print(f"wrote {a.output}: {len(spine)} V1 clip(s), {len(layers)} layer(s), {len(markers)} marker(s), "
          f"{float(total * tl.frame):.2f}s @ {a.width}x{a.height} {float(tl.fps):g}fps")


if __name__ == "__main__":
    main()
