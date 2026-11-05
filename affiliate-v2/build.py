#!/usr/bin/env python3
"""Generate index.html for the Ocean 6 recruitment edit, take 2 ("lime brutalist" design).

Edit list + word timings: src/edit.json (output seconds). Markup/animation: src/index.template.txt.
Run:  python3 build.py
"""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
EDIT = json.loads((HERE / "src" / "edit.json").read_text())
TOTAL = 39.9          # must stay under 40 s
SUB_END = 38.25       # subtitles end with the last word; CTA owns the band after that
LAST_VIDEO_END = 42.62  # last clip's picture runs a little past the voice cut, then a still holds

# ---------------------------------------------------------------- words
FIX = {"komision": "komisen", "RM1000": "RM1,000", "sample": "sampel", "stress,": "stres,", "Seeds": "6"}
words = []
for i, w in enumerate(EDIT["words"]):
    t = w["t"]
    if (i == 11 and t == "So") or (i == 118 and t == "And"):
        continue  # whisper put these across a cut; the audio for them was removed
    if i == 23 and t == "start":
        t = "stuck"
    words.append(dict(t=FIX.get(t, t), s=w["s"], e=w["e"], src_e=w["src_e"]))
words.append(dict(t="Yang", s=24.59, e=24.62, src_e=0))  # start of the B clip, lost in the pause cut
words.sort(key=lambda w: w["s"])

SENT_END_SRC = [2.10, 4.44, 6.28, 9.08, 10.52, 12.42, 16.00, 18.74, 20.50, 22.66, 26.04, 27.82, 29.58,
                32.18, 34.28, 37.54, 39.92, 42.22]
for w in words:
    w["brk"] = any(abs(w["src_e"] - e) < 0.05 for e in SENT_END_SRC) or w["t"] in ("sebulan", "RM500", "RM20", "bawah")

HL = {"5", "angka", "sebulan", "affiliate", "stuck", "RM1,000", "RM800,", "RM500", "RM10,", "RM20", "apa?", "circle",
      "leader", "susah", "join", "MCN", "Ocean", "6", "senang", "down", "stres,", "bersemangat", "Circle-circle",
      "semangat", "bawah", "blueprint", "dapat"}


def paginate(ws, max_chars=20, max_gap=0.35):
    pages, cur = [], []
    for w in ws:
        txt = " ".join(x["t"] for x in cur + [w])
        if cur and (len(txt) > max_chars or w["s"] - cur[-1]["e"] > max_gap or cur[-1]["brk"]
                    or cur[-1]["t"][-1] in ".?" or (cur[-1]["t"][-1] == "," and len(cur) >= 2)):
            pages.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pages.append(cur)
    return pages


pages = paginate(words)
LEAD = 0.06
cap_html, cap_js = [], []
for i, pg in enumerate(pages):
    start = max(0.0, pg[0]["s"] - LEAD)
    nxt = pages[i + 1][0]["s"] - LEAD if i + 1 < len(pages) else SUB_END
    nxt = min(nxt, SUB_END)
    spans = []
    for k, w in enumerate(pg):
        cls = "w hl" if (w["t"] in HL or w["t"].strip(".,?") in HL) else "w"
        text = re.sub(r"[.,]$", "", w["t"])
        if w["t"] == "6":
            spans.append(f'<span id="c{i}w{k}" class="{cls}" data-var-text="mcn_num">6</span>')
        else:
            spans.append(f'<span id="c{i}w{k}" class="{cls}">{text}</span>')
        cap_js.append([f"#c{i}w{k}", round(w["s"] - LEAD, 3), round(max(w["e"], w["s"] + 0.18), 3)])
    cap_html.append(f'        <div id="cap{i}" class="clip cap" data-start="{round(start, 3)}" '
                    f'data-duration="{round(nxt - start, 3)}" data-track-index="20">{"".join(spans)}</div>')

# ---------------------------------------------------------------- media
segs = EDIT["segments"]
videos = "\n".join(
    f'        <video id="seg{i}" class="clip footage" src="assets/source.mp4" muted playsinline '
    f'data-start="{s["at"]}" data-duration="{round((LAST_VIDEO_END if i == len(segs) - 1 else s["end"]) - s["src"], 4)}" '
    f'data-media-start="{s["src"]}" data-track-index="0"></video>'
    for i, s in enumerate(segs)
)
hold_start = round(segs[-1]["at"] + LAST_VIDEO_END - segs[-1]["src"], 4)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


SFX_GAIN = 0.5  # effects stay under the voice
SFX = [
    (0.0, "zoom", 0.3), (2.0, "stamp", 0.6), (2.85, "stamp", 0.5), (2.9, "pencil", 0.3), (3.42, "swoosh", 0.4),
    (4.2, "tape", 0.35), (6.6, "paper", 0.4), (6.7, "click", 0.5), (8.0, "click", 0.5), (8.64, "click", 0.5),
    (10.34, "neg", 0.45), (10.8, "neg", 0.45), (11.1, "hit", 0.45),
    (11.9, "swoosh", 0.35), (12.44, "scribble", 0.4), (13.62, "scribble", 0.4), (15.78, "scribble", 0.4), (16.96, "stamp", 0.55),
    (18.9, "swoosh", 0.4), (19.7, "stamp", 0.6), (19.75, "pencil", 0.35), (20.02, "sparkle", 0.3),
    (20.7, "tape", 0.35), (21.94, "correct", 0.3), (22.5, "click", 0.5), (23.6, "click", 0.5),
    (24.62, "swoosh", 0.35), (25.45, "bubble", 0.45), (25.83, "bubble", 0.45), (26.75, "neg", 0.45),
    (27.3, "msg", 0.4), (29.09, "levelup", 0.35),
    (31.1, "paper", 0.4), (31.6, "pencil", 0.4), (33.09, "stamp", 0.5),
    (33.6, "tape", 0.35), (34.72, "pencil", 0.35), (35.4, "click", 0.5), (36.76, "coins", 0.4),
    (37.55, "swoosh", 0.4), (37.95, "msg", 0.5), (38.6, "stamp", 0.45),
]
audio = [
    f'    <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="1"></audio>',
    f'    <audio id="bgm-a" src="assets/bgm.wav" data-start="0" data-duration="{SUB_END}" data-volume="0.12" data-fade-in="0.3" data-track-index="2"></audio>',
    f'    <audio id="bgm-b" src="assets/bgm.wav" data-start="{SUB_END}" data-duration="{round(TOTAL - SUB_END, 3)}" data-media-start="{SUB_END}" data-volume="0.28" data-fade-out="0.9" data-track-index="2"></audio>',
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
html = (tpl.replace("__TOTAL__", str(TOTAL)).replace("__SUBEND__", str(SUB_END))
        .replace("__VIDEOS__", videos).replace("__HOLDSTART__", str(hold_start))
        .replace("__HOLDDUR__", str(round(TOTAL - hold_start, 4)))
        .replace("__AUDIO__", "\n".join(audio)).replace("__CAPTIONS__", "\n".join(cap_html))
        .replace("__CAPWORDS__", json.dumps(cap_js)))
left = re.findall(r"__[A-Z]+__", html)
assert not left, left
(HERE / "index.html").write_text(html)
print(f"wrote index.html {TOTAL}s pages={len(pages)} hold@{hold_start}")
for i, pg in enumerate(pages):
    print(i, round(pg[0]["s"], 2), " ".join(w["t"] for w in pg))
