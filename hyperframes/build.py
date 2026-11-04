#!/usr/bin/env python3
"""Generate index.html for the HyperFrames version of the Black Ice edit.

Timings are authored in 30fps frames (same beat grid as the Remotion version)
and converted to seconds here. Run:  python3 build.py
"""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
WORDS_TS = (HERE.parent / "src" / "words.ts").read_text()


def ts_const(name):
    m = re.search(rf"export const {name} = (.*?)(?: as const)?;\n", WORDS_TS, re.S)
    return json.loads(m.group(1))


WORDS = ts_const("WORDS")
SEGMENTS = ts_const("SEGMENTS")
TOTAL = int(re.search(r"export const TOTAL = (\d+);", WORDS_TS).group(1))


def sec(f):
    return round(f / 30, 4)


def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout)


SFX_GAIN = 0.55
SFX = [
    (0, "deep_whoosh", 0.35), (6, "hit", 0.45), (19, "swipe", 0.5), (40, "hit", 0.42),
    (59, "swipe", 0.5), (71, "hit", 0.48), (95, "swipe", 0.5), (102, "impact", 0.6),
    (116, "whoosh", 0.45), (124, "sparkle", 0.4), (164, "shutter", 0.35), (176, "swoosh", 0.35),
    (228, "bubble", 0.5), (262, "coins", 0.45), (300, "swoosh", 0.3), (309, "click", 0.6),
    (316, "success", 0.3), (338, "swoosh", 0.3), (399, "pop", 0.35), (430, "pop", 0.35),
    (447, "pop", 0.35), (474, "swoosh", 0.3),
]

total_s = sec(TOTAL)

videos = "\n".join(
    f'          <video id="seg{i}" class="clip footage" src="assets/source.mp4" muted playsinline '
    f'data-start="{sec(s["at"])}" data-duration="{sec(s["to"] - s["from"])}" '
    f'data-media-start="{sec(s["from"])}" data-track-index="0"></video>'
    for i, s in enumerate(SEGMENTS)
)

audio = [
    f'    <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="{total_s}" data-volume="1" data-track-index="1"></audio>',
    # BGM ~17dB under the voice, lifts for the last beat after the final word
    f'    <audio id="bgm-a" src="assets/bgm.wav" data-start="0" data-duration="20.0" data-volume="0.14" data-fade-in="0.13" data-track-index="2"></audio>',
    f'    <audio id="bgm-b" src="assets/bgm.wav" data-start="20.0" data-duration="{round(total_s - 20.0, 4)}" data-media-start="20.0" data-volume="0.32" data-track-index="2"></audio>',
]
lane_ends = []  # greedy lanes so overlapping SFX sit on separate tracks
for i, (f, name, vol) in enumerate(SFX):
    d = min(dur(HERE / "assets" / "sfx" / f"{name}.wav"), total_s - sec(f))
    lane = next((k for k, e in enumerate(lane_ends) if e <= sec(f)), None)
    if lane is None:
        lane_ends.append(0)
        lane = len(lane_ends) - 1
    lane_ends[lane] = sec(f) + d
    audio.append(
        f'    <audio id="sfx{i}" src="assets/sfx/{name}.wav" data-start="{sec(f)}" '
        f'data-duration="{round(d, 4)}" data-volume="{round(vol * SFX_GAIN, 4)}" data-track-index="{10 + lane}"></audio>'
    )

# ---- captions: one timed group per page, words as children ----
PAGES = [[14, 17], [18, 20], [21, 23], [24, 25], [26, 28], [29, 30], [31, 34], [35, 37],
         [38, 39], [40, 43], [44, 46], [47, 50], [51, 53], [54, 55]]
YEL, ICE, RED, WHITE = "#ffd21f", "#9be8ff", "#ff2d46", "#ffffff"
HL = {"kuning": YEL, "promotion": YEL, "kau-kau,": YEL, "check": ICE, "out": ICE, "maskulin,": ICE,
      "outdoor,": ICE, "indoor": ICE, "baucer": YEL, "habis.": RED, "cepat-cepat": YEL}
LEAD = 2
caps = []
for i, (a, b) in enumerate(PAGES):
    start = (WORDS[a]["s"] - LEAD) / 30
    end = (WORDS[PAGES[i + 1][0]]["s"] - LEAD) / 30 if i + 1 < len(PAGES) else total_s
    words = "".join(
        f'<span id="w{k}" class="w" data-hl="{HL.get(WORDS[k]["t"].lower(), WHITE)}">'
        f'{re.sub(r"[.,]", "", WORDS[k]["t"])}</span>'
        for k in range(a, b + 1)
    )
    caps.append(
        f'        <div id="cap{i}" class="clip cap" data-start="{round(start, 4)}" '
        f'data-duration="{round(end - start, 4)}" data-track-index="8">{words}</div>'
    )

# ---- ice dust: deterministic (seeded) positions along the frame edges only ----
seed = 1234567
def rnd():
    global seed
    seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    return seed / 0x7FFFFFFF
motes = []
for i in range(34):
    x = 10 + rnd() * 170 if i % 2 == 0 else 900 + rnd() * 170
    size = 3 + rnd() * 7
    motes.append(
        f'        <div class="mote" style="left:{x:.1f}px;top:0;width:{size:.1f}px;height:{size:.1f}px;'
        f'opacity:{0.45 + rnd() * 0.4:.2f}" data-y="{rnd() * 1920:.0f}" data-sp="{1.2 + rnd() * 2.4:.2f}"></div>'
    )

title_chars = "".join(
    '<span class="t-ch t-sp"></span>' if c == " " else f'<span class="t-ch">{c}</span>' for c in "BLACK ICE"
)
basket = ('<svg width="66" height="66" viewBox="0 0 64 64" fill="none">'
          '<path d="M18 26 L28 10 M46 26 L36 10" stroke="#05080c" stroke-width="5" stroke-linecap="round"/>'
          '<path d="M8 26 H56 L50 54 H14 Z" fill="#05080c"/>'
          '<path d="M24 34 V46 M32 34 V46 M40 34 V46" stroke="#ffd21f" stroke-width="4" stroke-linecap="round"/></svg>')
def tick(n):
    return (f'<svg width="38" height="38" viewBox="0 0 24 24" fill="none"><path id="tick{n}" class="tick" '
            'd="M5 12.5 L10 17.5 L19 7" stroke="#05080c" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

tpl = (HERE / "src" / "index.template.txt").read_text()
html = (
    tpl.replace("__TOTAL__", str(total_s))
    .replace("__VIDEOS__", videos)
    .replace("__AUDIO__", "\n".join(audio))
    .replace("__WORDS__", json.dumps(WORDS, ensure_ascii=False))
    .replace("__PAGES__", json.dumps(PAGES))
    .replace("__CAPTIONS__", "\n".join(caps))
    .replace("__DUST__", "\n".join(motes))
    .replace("__TITLE_CHARS__", title_chars)
    .replace("__BASKET_SVG__", basket)
    .replace("__TICK1__", tick(1)).replace("__TICK2__", tick(2)).replace("__TICK3__", tick(3))
    .replace("__CTA_DUR__", str(round(total_s - 15.9, 4)))
)
assert "__" not in re.sub(r"window\.__\w+", "", html), re.findall(r"__\w+__", html)
(HERE / "index.html").write_text(html)
print("wrote index.html", total_s, "s")
