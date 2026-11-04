#!/usr/bin/env python3
"""Generate index.html for the "Join my affiliate team" edit (HyperFrames).

Edit list + word timings live in src/edit.json (output-timeline seconds).
Markup/animation live in src/index.template.txt. Run:  python3 build.py
"""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
EDIT = json.loads((HERE / "src" / "edit.json").read_text())
TOTAL = 44.4  # edited speech ends ~41.9 s, then a CTA hold
LAST_VIDEO_END = 42.62  # let the final clip's picture run past the voice cut, then hold a still
POSTER = (31.4837, 35.5337)  # creator's own poster, baked into the footage
AFTER_POSTER = 35.56  # poster last frame is 35.55 (frame 2133); card shows from frame 2134

# ---------------------------------------------------------------- words
FIX = {"komision": "komisen", "RM1000": "RM1,000", "sample": "sampel", "stress,": "stres,"}
words = []
for i, w in enumerate(EDIT["words"]):
    t = w["t"]
    if i == 11 and t == "So":  # whisper put the C-segment "So" inside the hook clip
        continue
    if i == 27 and t == "start":
        t = "stuck"  # matches what is said ("selalu stuck dekat 1,000")
    words.append(dict(t=FIX.get(t, t), s=w["s"], e=w["e"]))
# "Yang" (start of B) fell into the removed pause; restore it on the cut
words.append(dict(t="Yang", s=26.33, e=26.36))
words.sort(key=lambda w: w["s"])

# sentence ends from Whisper's segments (source seconds) -> force a caption break after them
SENT_END_SRC = [2.10, 4.44, 6.28, 9.08, 10.52, 12.42, 16.00, 18.74, 20.50, 22.66, 26.04, 27.82, 29.58, 32.18,
                34.30, 37.54, 39.92, 42.22]


def to_src(t):
    for sg in EDIT["segments"]:
        if sg["at"] <= t < sg["at"] + (sg["end"] - sg["src"]) + 1e-6:
            return sg["src"] + (t - sg["at"])
    return None


for w in words:
    src = to_src(w["e"])
    w["brk"] = src is not None and any(abs(src - e) < 0.05 for e in SENT_END_SRC)
# hook ends on "sebulan" (its sentence end sits inside the hook clip)
for w in words:
    if w["t"] in ("sebulan", "atas", "RM20", "RM500"):
        w["brk"] = True

BRAND_WORD = "Seeds"
HL = {"5", "angka", "sebulan", "stuck", "RM1,000", "RM800,", "RM500", "RM10,", "RM20", "apa?", "circle",
      "leader", "susah", "join", "MCN", "Ocean", BRAND_WORD, "senang", "down", "stres,", "bersemangat",
      "Circle-circle", "semangat", "bawah", "atas", "blueprint", "dapat"}
NEG = {"stuck", "RM10,", "RM20", "apa?", "susah", "down", "stres,", "bersemangat", "bawah"}


def paginate(ws, max_chars=19, max_gap=0.35):
    pages, cur = [], []
    for w in ws:
        txt = " ".join(x["t"] for x in cur + [w])
        brk = cur and (len(txt) > max_chars or w["s"] - cur[-1]["e"] > max_gap
                       or cur[-1].get("brk") or cur[-1]["t"][-1] in ".?" or (cur[-1]["t"][-1] == "," and len(cur) >= 2))
        if brk:
            pages.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pages.append(cur)
    return pages


# no caption card while the poster is on screen
visible = []
for w in words:
    if POSTER[0] - 0.05 <= w["s"] < POSTER[1] - 0.5:
        continue  # spoken over the poster: no card there
    if POSTER[1] - 0.5 <= w["s"] < POSTER[1]:
        w = dict(w, s=POSTER[1] + 0.1)  # words just before the card returns start with it
    visible.append(w)
pages = paginate(visible)

LEAD = 0.06
cap_html, cap_js = [], []
for i, pg in enumerate(pages):
    start = max(0, pg[0]["s"] - LEAD)
    nxt = pages[i + 1][0]["s"] - LEAD if i + 1 < len(pages) else 41.95
    # don't let a page hang across the poster
    if start < POSTER[0] <= nxt:
        nxt = POSTER[0]
    nxt = min(nxt, start + max(1.2, pg[-1]["e"] - start + 0.5))
    spans = []
    for k, w in enumerate(pg):
        cls = "w"
        if w["t"].strip(".,?") in HL or w["t"] in HL:
            cls += " neg" if w["t"] in NEG else " hl"
        text = re.sub(r"[.,]$", "", w["t"])
        if w["t"] == BRAND_WORD:
            spans.append(f'<span id="c{i}w{k}" class="{cls}" data-var-text="mcn_short">6</span>')
        else:
            spans.append(f'<span id="c{i}w{k}" class="{cls}">{text}</span>')
        cap_js.append([f"#c{i}w{k}", round(w["s"] - LEAD, 3), round(max(w["e"], w["s"] + 0.18), 3)])
    cap_html.append(
        f'        <div id="cap{i}" class="clip cap" data-start="{round(start, 3)}" '
        f'data-duration="{round(nxt - start, 3)}" data-track-index="20">{"".join(spans)}</div>'
    )

# chapter tabs on the caption card
CHAPTERS = [(0, 3.45, "RAHSIA"), (3.45, 12.55, "REALITI"), (12.55, 19.8, "PUNCA"), (19.8, 26.3, "SOLUSI"),
            (26.3, POSTER[0], "CIRCLE"), (AFTER_POSTER, 41.95, "BLUEPRINT")]
tabs = "\n".join(
    f'        <div id="tab{i}" class="clip tab" data-start="{a}" data-duration="{round(b - a, 4)}" data-track-index="21">'
    f'<span class="tab-dot"></span>{name}</div>'
    for i, (a, b, name) in enumerate(CHAPTERS)
)
card_spans = [(0, POSTER[0]), (AFTER_POSTER, 41.95)]
cards = "\n".join(
    f'      <div id="card{i}" class="clip capcard" data-start="{a}" data-duration="{round(b - a, 4)}" data-track-index="19"><div id="card{i}-in" class="capcard-in"></div></div>'
    for i, (a, b) in enumerate(card_spans)
)

# ---------------------------------------------------------------- media
segs = EDIT["segments"]
videos = "\n".join(
    f'          <video id="seg{i}" class="clip footage" src="assets/source.mp4" muted playsinline '
    f'data-start="{s["at"]}" data-duration="{round((LAST_VIDEO_END if i == len(segs) - 1 else s["end"]) - s["src"], 4)}" data-media-start="{s["src"]}" '
    f'data-track-index="0"></video>'
    for i, s in enumerate(segs)
)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


SFX_GAIN = 0.5  # effects sit clearly under the voice
SFX = [
    (0.0, "zoom", 0.35), (0.62, "select", 0.4), (1.62, "coins", 0.5), (2.82, "positive", 0.35),
    (3.42, "swoosh", 0.4),
    (7.2, "card_in", 0.35), (7.43, "pop", 0.35), (8.73, "pop", 0.35), (9.37, "pop", 0.35),
    (11.07, "neg_tap", 0.45), (11.53, "neg_tap", 0.45), (11.83, "bubble", 0.5),
    (12.6, "swoosh", 0.35), (13.17, "neg_tap", 0.4), (14.35, "neg_tap", 0.4), (18.71, "neg_tap", 0.45),
    (19.8, "whoosh", 0.4), (20.71, "splash", 0.45), (21.45, "sparkle", 0.35),
    (23.69, "select", 0.45), (24.25, "select", 0.45), (25.45, "correct", 0.3),
    (26.4, "swoosh", 0.3), (27.2, "bubble", 0.4), (27.58, "bubble", 0.4), (28.5, "bubble", 0.4),
    (29.06, "chime", 0.35), (30.84, "level_done", 0.35),
    (31.46, "whoosh", 0.4), (31.5, "impact_movie", 0.25), (35.5, "swoosh", 0.35), (36.68, "achieve", 0.3),
    (37.2, "paper_move", 0.45), (38.38, "paper_slide", 0.5), (39.9, "coins", 0.4),
    (41.6, "card_in", 0.35), (42.0, "msg_pop", 0.5),
]
audio = [
    f'    <audio id="vo" src="assets/voice.wav" data-start="0" data-duration="43.5" data-volume="1" data-track-index="1"></audio>',
    f'    <audio id="bgm-a" src="assets/bgm.wav" data-start="0" data-duration="41.95" data-volume="0.13" data-fade-in="0.4" data-track-index="2"></audio>',
    f'    <audio id="bgm-b" src="assets/bgm.wav" data-start="41.95" data-duration="{round(TOTAL - 41.95, 3)}" data-media-start="41.95" data-volume="0.3" data-fade-out="0.9" data-track-index="2"></audio>',
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
html = (tpl.replace("__TOTAL__", str(TOTAL))
        .replace("__VIDEOS__", videos)
        .replace("__AUDIO__", "\n".join(audio))
        .replace("__CARDS__", cards)
        .replace("__TABS__", tabs)
        .replace("__CAPTIONS__", "\n".join(cap_html))
        .replace("__CAPWORDS__", json.dumps(cap_js)))
left = re.findall(r"__[A-Z]+__", html)
assert not left, left
(HERE / "index.html").write_text(html)
print(f"wrote index.html  {TOTAL}s  pages={len(pages)}")
for i, pg in enumerate(pages):
    print(i, round(pg[0]["s"], 2), " ".join(w["t"] for w in pg))
