"""Generate SFX / music with ElevenLabs.

The API key is read from the ELEVENLABS_API_KEY environment variable, falling back to
a .env file (path in VIDEO_USE_ENV, default ./.env). It is never printed.
"""
import json
import os
import pathlib
import sys

import requests


def key() -> str:
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    env_file = pathlib.Path(os.environ.get("VIDEO_USE_ENV", ".env"))
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")
    sys.exit("ELEVENLABS_API_KEY not set (env var or VIDEO_USE_ENV file)")


def sfx(text, dur, out, infl=0.45):
    r = requests.post(
        "https://api.elevenlabs.io/v1/sound-generation",
        headers={"xi-api-key": key()},
        json={"text": text, "duration_seconds": dur, "prompt_influence": infl},
        timeout=120,
    )
    r.raise_for_status()
    pathlib.Path(out).write_bytes(r.content)
    print("ok", out, len(r.content))


def music(prompt, ms, out):
    r = requests.post(
        "https://api.elevenlabs.io/v1/music",
        headers={"xi-api-key": key()},
        json={"prompt": prompt, "music_length_ms": ms, "force_instrumental": True},
        timeout=600,
    )
    if r.status_code != 200:
        print("music error", r.status_code, r.text[:300])
        return
    pathlib.Path(out).write_bytes(r.content)
    print("ok", out, len(r.content))


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf8"))
    for s in spec.get("sfx", []):
        sfx(s["text"], s["dur"], s["out"], s.get("infl", 0.45))
    for m in spec.get("music", []):
        music(m["prompt"], m["ms"], m["out"])
