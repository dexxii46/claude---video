#!/usr/bin/env python3
"""Generate index.html for the Armaf Odyssey Mega edit ("editorial luxe" design).

Audio edit: src/edit.json (source -> output). Caption words: src/words_raw.json, transcribed from the
edited voice track, so they are already in output time. Markup/animation: src/index.template.txt.
Run:  python3 build.py
"""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
EDIT = json.loads((HERE / "src" / "edit.json").read_text())
RAW = json.loads((HERE / "src" / "words_raw.json").read_text())
TOTAL = 32.6          # must stay under 35 s
SPEECH_END = EDIT["edited"]  # 30.6
HOOK_VISUAL_SRC = 22.3  # cap/logo spin; that stretch's own audio (the comparison line) was cut

# ---------------------------------------------------------------- video: hook uses a different shot, then picture follows the voice
aud = EDIT["audio"]
hook_len = aud[2]["at"]
video_segs = [dict(src=HOOK_VISUAL_SRC, at=0.0, dur=hook_len)]
for i, a in enumerate(aud[2:]):
    end = 60.7 if i == len(aud[2:]) - 1 else a["end"]  # last shot runs to the end of the take
    video_segs.append(dict(src=a["src"], at=a["at"], dur=round(end - a["src"], 4)))
hold_start = round(video_segs[-1]["at"] + video_segs[-1]["dur"], 4)
videos = "\n".join(
    f'        <video id="seg{i}" class="clip footage" src="assets/source.mp4" muted playsinline data-start="{v["at"]}" '
    f'data-duration="{v["dur"]}" data-media-start="{v["src"]}" data-track-index="0"></video>'
    for i, v in enumerate(video_segs))

# ---------------------------------------------------------------- caption words
FIX = {"Odissi": "Odyssey", "RM100ml": "100ML", "perimah": "premium", "sembuh": "sembur", "powder": "powdery"}
cuts = [a["at"] for a in aud]
words = []
for x in RAW:
    t = x["w"].strip()
    if t.startswith("-") and words:
        words[-1]["t"] += t
        words[-1]["e"] = x["e"]
        continue
    if t.lower().strip(",") == "eh":
        continue
    t = FIX.get(t.strip(",."), t)
    s, e = x["s"], x["e"]
    for c in cuts:  # a word never starts before the clip it is spoken in
        if s < c < e and c - s < 0.6:
            s = c
    words.append(dict(t=t, s=round(s, 3), e=round(e, 3)))

HL = {"rm200", "odyssey", "mega", "armaf", "100ml", "premium", "leather", "casing", "apple", "fresh,", "fresh",
      "masculine", "powdery", "harian", "kuning", "murah", "siang", "malam"}
BREAK_AFTER = {"terbaru", "armaf", "100ml", "premium", "ni", "apple", "powdery", "ok", "beli", "lah"}


def paginate(ws, max_chars=30):
    pages, cur = [], []
    for i, w in enumerate(ws):
        txt = " ".join(x["t"] for x in cur + [w])
        crosses_cut = any(cur and cur[-1]["s"] < c - 0.02 and c <= w["s"] + 0.05 for c in cuts[1:])
        if cur and (crosses_cut or len(txt) > max_chars or w["s"] - cur[-1]["e"] > 0.4
                    or (cur[-1]["t"].lower().strip(",.") in BREAK_AFTER and len(" ".join(x["t"] for x in cur)) > 6)):
            pages.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pages.append(cur)
    return pages


pages = paginate(words)
cap_html, cap_js = [], []
for i, pg in enumerate(pages):
    start = max(0.0, pg[0]["s"] - 0.04)
    nxt = pages[i + 1][0]["s"] - 0.04 if i + 1 < len(pages) else SPEECH_END + 0.1
    spans = []
    for k, w in enumerate(pg):
        cls = "w hl" if w["t"].lower().strip(",.") in HL else "w"
        spans.append(f'<span id="c{i}w{k}" class="{cls}">{re.sub(r"[.,]$", "", w["t"])}</span>')
        cap_js.append([f"#c{i}w{k}", round(w["s"] - 0.04, 3), round(max(w["e"], w["s"] + 0.2), 3)])
    cap_html.append(f'        <div id="cap{i}" class="clip cap" data-start="{round(start, 3)}" '
                    f'data-duration="{round(nxt - start, 3)}" data-track-index="20">{" ".join(spans)}</div>')

# ---------------------------------------------------------------- audio


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


SFX_GAIN = 0.35  # effects always sit well under the voice
SFX = [
    (0.0, "air", 0.35), (1.38, "coins", 0.4), (2.43, "page", 0.5), (5.6, "sparkle", 0.3), (8.44, "tick", 0.5),
    (11.0, "glow", 0.3), (12.32, "select", 0.4), (15.93, "wind", 0.4), (19.08, "bubble", 0.45), (20.14, "bubble", 0.45),
    (21.86, "chime", 0.35), (22.93, "page", 0.5), (24.68, "tick", 0.5), (25.5, "paper", 0.4), (26.86, "msg", 0.4),
    (27.44, "coins", 0.35), (29.6, "tick", 0.45), (30.04, "tick", 0.45), (30.65, "positive", 0.35),
]
audio = [
    f'    <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="1"></audio>',
    f'    <audio id="bgm-a" src="assets/bgm.wav" data-start="0" data-duration="{SPEECH_END}" data-volume="0.12" data-fade-in="0.3" data-track-index="2"></audio>',
    f'    <audio id="bgm-b" src="assets/bgm.wav" data-start="{SPEECH_END}" data-duration="{round(TOTAL - SPEECH_END, 3)}" data-media-start="{SPEECH_END}" data-volume="0.26" data-fade-out="1.0" data-track-index="2"></audio>',
]
lane_ends = []
for i, (t, name, vol) in enumerate(SFX):
    d = min(dur(HERE / "assets" / "sfx" / f"{name}.wav"), TOTAL - t)
    lane = next((k for k, e in enumerate(lane_ends) if e <= t), None)
    if lane is None:
        lane_ends.append(0)
        lane = len(lane_ends) - 1
    lane_ends[lane] = t + d
    audio.append(f'    <audio id="sfx{i}" src="assets/sfx/{name}.wav" data-start="{t}" data-duration="{round(d, 3)}" '
                 f'data-volume="{round(vol * SFX_GAIN, 3)}" data-track-index="{10 + lane}"></audio>')

tpl = (HERE / "src" / "index.template.txt").read_text()
html = (tpl.replace("__TOTAL__", str(TOTAL)).replace("__VIDEOS__", videos)
        .replace("__HOLDSTART__", str(hold_start)).replace("__HOLDDUR__", str(round(TOTAL - hold_start, 4)))
        .replace("__AUDIO__", "\n".join(audio)).replace("__CAPTIONS__", "\n".join(cap_html))
        .replace("__CAPWORDS__", json.dumps(cap_js)))
left = re.findall(r"__[A-Z]+__", html)
assert not left, left
(HERE / "index.html").write_text(html)
print(f"wrote index.html {TOTAL}s pages={len(pages)} hold@{hold_start}")
for i, pg in enumerate(pages):
    print(i, round(pg[0]["s"], 2), " ".join(w["t"] for w in pg))
