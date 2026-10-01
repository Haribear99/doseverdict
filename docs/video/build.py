"""시연 영상 합성기 — storyboard.json → TTS(edge-tts) → 장면별 영상 → 자막 번인 → out/doseverdict_demo.mp4

실행: py -3.14 docs/video/build.py [--only s01,s02] [--no-burn]
- 비트(beat) 하나 = 내레이션 한 덩어리 + 화면 하나. 비트 길이는 TTS 길이 + gap으로 정해져 음성과 화면이 어긋나지 않는다.
- 화면 종류: image(정지, 선택적 느린 확대) · scroll(긴 캡처를 위→아래로) · clip(녹화 구간을 비트 길이에 맞춰 배속)
- 숫자·원문은 캡처와 카드(실제 값)만 쓴다. 생성 이미지는 넣지 않는다.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TMP = OUT / "tmp"
FPS = 30
W, H = 1920, 1080
SR = 48000

INK = "1b2430"
BOX_T = 4  # 강조 박스 선 두께(px). 선은 박스 바깥쪽에 그려 안쪽 여백(pad)을 글자에서 떼어 둔다


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-3000:])
        raise SystemExit(1)


def duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


# ---------- TTS ----------
SAY_RULES = [
    (r"(\d)\s*~\s*(\d)", r"\1에서 \2"),
    (r"(\d)\s*mg\b", r"\1 밀리그램"),
    (r"(\d)\s*nM\b", r"\1 나노몰"),
    (r"(\d(?:\.\d+)?)\s*%", r"\1 퍼센트"),
    (r"\bRP2D\b", "알피투디"),
    (r"\bMTD\b", "엠티디"),
    (r"\bPK\b", "피케이"),
    (r"\bDLT\b", "디엘티"),
    (r"\bTCR\b", "티씨알"),
    (r"\bFDA\b", "에프디에이"),
    (r"\bNLI\b", "엔엘아이"),
    (r"\bAUROC\b", "에이유록"),
    (r"\bORR\b", "오알알"),
    (r"\bPFS\b", "피에프에스"),
    (r"3\+3", "삼 플러스 삼"),
    (r"\bBOIN\b", "보인"),
    (r"\bChEMBL\b", "켐블"),
    (r"\bRDKit\b", "알디킷"),
    (r"\bopenFDA\b", "오픈 에프디에이"),
    (r"\bIC50\b", "아이씨 오십"),
    (r"\bDV-505\b", "디브이 오공오"),
    (r"\bDiff\b", "디프"),
    (r"\bnull\b", "널"),
    (r"\bgrounded\b", "그라운디드"),
    (r"\bablation\b", "어블레이션"),
    (r"\bSMILES\b", "스마일스"),
    (r"\bKRAS G12C\b", "크라스 지 십이 씨"),
]


def to_say(text: str) -> str:
    # 파이썬 \b는 한글도 단어 문자로 봐서 "RP2D로"·"mg에서"를 놓친다 → 영숫자 경계로 바꿔 적용
    s = text.replace("DoseVerdict", "도즈버딕트")
    for pat, rep in SAY_RULES:
        pat = pat.replace(r"\b", r"(?<![A-Za-z0-9])", 1) if pat.startswith(r"\b") else pat
        pat = pat.replace(r"\b", r"(?![A-Za-z0-9])")
        s = re.sub(pat, rep, s)
    return s


async def _tts(say: str, voice: str, rate: str, out: Path) -> None:
    await edge_tts.Communicate(say, voice, rate=rate).save(str(out))


def tts(say: str, voice: str, rate: str) -> Path:
    key = hashlib.sha1(f"{voice}|{rate}|{say}".encode()).hexdigest()[:16]
    mp3 = TMP / "tts" / f"{key}.mp3"
    if not mp3.exists():
        mp3.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(3):
            try:
                asyncio.run(_tts(say, voice, rate, mp3))
                break
            except Exception:  # edge-tts 일시 오류는 재시도
                if attempt == 2:
                    raise
    # edge-tts는 앞 약 0.35초·뒤 약 1.1초 무음을 붙인다 → 잘라서 비트 간격(gap)으로만 쉼을 준다
    wav = mp3.with_suffix(".trim.wav")
    if not wav.exists():
        sr = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-af",
             f"{sr},areverse,{sr.replace('0.04', '0.08')},areverse", "-ar", str(SR), "-ac", "1", str(wav)])
    return wav


# ---------- 화면 ----------
def vf_image(v: dict, d: float) -> tuple[list[str], str]:
    src = HERE / v["src"]
    z0, z1 = v.get("zoom", [1.0, 1.0])
    ox, oy = v.get("focus", [0.5, 0.5])  # 확대 중심(비율)
    inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(src)]
    # 카드는 1920x1080 좌표 그대로 → pad만 적용(확대가 있으면 좌표가 어긋나므로 박스와 함께 쓰지 않는다)
    v["_boxes"] = [dict(b, x=b["x"] - b.get("pad", 12), y=b["y"] - b.get("pad", 12),
                        w=b["w"] + 2 * b.get("pad", 12), h=b["h"] + 2 * b.get("pad", 12)) for b in v.get("boxes", [])]
    if z0 == z1 == 1.0:
        vf = f"scale={W}:{H}:flags=lanczos,setsar=1"
    else:
        z = f"({z0}+({z1}-{z0})*min(1,t/{d:.3f}))"
        vf = (f"scale=w='trunc({W}*{z}/2)*2':h=-2:eval=frame:flags=lanczos,"
              f"crop={W}:{H}:x='(in_w-{W})*{ox}':y='(in_h-{H})*{oy}',setsar=1")
    return inp, vf


def vf_scroll(v: dict, d: float) -> tuple[list[str], str]:
    src = HERE / v["src"]
    y0, y1 = v["y0"], v["y1"]  # 1920 폭 기준 좌표
    hold = v.get("hold", 0.15)  # 앞뒤 정지 비율
    p = f"min(1,max(0,(t/{d:.3f}-{hold})/(1-2*{hold})))"
    ease = f"(3*{p}*{p}-2*{p}*{p}*{p})"
    inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(src)]
    vf = f"scale={W}:-2:flags=lanczos,crop={W}:{H}:0:'{y0}+({y1}-{y0})*{ease}',setsar=1"
    return inp, vf


def vf_clip(v: dict, d: float) -> tuple[list[str], str]:
    src = HERE / v["src"]
    crop = v.get("crop")  # [x, y, w] CSS px, 16:9
    pre = f"crop={crop[2]}:{int(crop[2]*9/16)}:{crop[0]}:{crop[1]}," if crop else ""
    if "freeze" in v:  # 녹화의 한 프레임을 비트 내내 정지(과속 배속 구간 대체). 나머지 길이는 render_segment의 tpad가 채운다
        inp = ["-ss", f"{v['freeze']:.3f}", "-i", str(src)]
        vf = (f"{pre}trim=end_frame=1,setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=#fbfaf7,setsar=1")
        return inp, vf
    s, e = v["start"], v["end"]
    k = d / (e - s)
    inp = ["-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", str(src)]
    vf = (f"{pre}setpts=(PTS-STARTPTS)*{k:.5f},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=#fbfaf7,setsar=1")
    return inp, vf


def load_marks(src: str) -> dict:
    m = HERE / (str(Path(src).with_suffix("")) + ".marks.json")
    return json.loads(m.read_text(encoding="utf-8")) if m.exists() else {}


def vf_view(v: dict, d: float) -> tuple[list[str], str]:
    """캡처(CSS px 좌표, 2배 해상도 PNG)의 한 창을 1920x1080으로 확대. to=[x,y]면 같은 배율로 패닝."""
    src = HERE / v["src"]
    from PIL import Image
    iw, ih = Image.open(src).size
    k = iw / W  # PNG 픽셀 / CSS px (dsf)
    x0, y0, cw = v["crop"]
    ch = cw * 9 / 16
    x1, y1 = v.get("to", [x0, y0])
    # 창이 이미지 밖으로 나가면 ffmpeg crop이 몰래 안쪽으로 밀어 박스가 어긋난다 → 미리 고정
    mx, my = iw / k - cw, ih / k - ch
    x0, x1 = min(max(0, x0), mx), min(max(0, x1), mx)
    y0, y1 = min(max(0, y0), my), min(max(0, y1), my)
    hold = v.get("hold", 0.15)
    p = f"min(1,max(0,(t/{d:.3f}-{hold})/(1-2*{hold})))"
    e = f"(3*{p}*{p}-2*{p}*{p}*{p})"
    inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(src)]
    vf = (f"crop={int(cw*k)}:{int(ch*k)}:'{x0*k}+({(x1-x0)*k})*{e}':'{y0*k}+({(y1-y0)*k})*{e}',"
          f"scale={W}:{H}:flags=lanczos,setsar=1")
    # 강조 박스는 최종 창 기준으로 좌표 변환(패닝이 있으면 패닝이 끝난 뒤부터)
    marks = load_marks(v["src"])
    s = W / cw
    bx = []
    for b in v.get("boxes", []):
        if "mark" in b:
            mx, my, mw, mh = marks[b["mark"]]
            if "w" in b:
                mw = b["w"]
            if "h" in b:
                mh = b["h"]
        else:
            mx, my, mw, mh = b["x"], b["y"], b["w"], b["h"]
        pad = b.get("pad", 8)
        nb = dict(b, x=int((mx - pad - x1) * s), y=int((my - pad - y1) * s), w=int((mw + 2 * pad) * s), h=int((mh + 2 * pad) * s))
        if v.get("to") and nb.get("from", 0) < 1 - hold:
            nb["from"] = 1 - hold
        bx.append(nb)
    v["_boxes"] = bx
    return inp, vf


def boxes_vf(v: dict, d: float) -> str:
    out = []
    for b in v.get("_boxes", v.get("boxes", [])):
        t0, t1 = b.get("from", 0.0) * d, b.get("to", 1.0) * d
        en = f"enable='gte(t,{t0:.3f})*lt(t,{t1:.3f})'"  # 반열린 구간 → 이어지는 박스가 경계 프레임에서 겹치지 않는다
        if b.get("spot"):  # 강조 영역 밖을 종이색으로 덮어 시선을 모은다
            x, y, w, h = max(0, b["x"]), max(0, b["y"]), b["w"], b["h"]
            for rx, ry, rw, rh in [(0, 0, W, y), (0, y + h, W, H - y - h), (0, y, x, h), (x + w, y, W - x - w, h)]:
                if rw > 0 and rh > 0:
                    out.append(f"drawbox=x={rx}:y={ry}:w={rw}:h={rh}:color=#fbfaf7@0.84:t=fill:{en}")
        # drawbox는 선을 사각형 안쪽으로 그린다 → 두께만큼 키워 선이 pad 바깥에 놓이게 한다
        out.append(f"drawbox=x={b['x'] - BOX_T}:y={b['y'] - BOX_T}:w={b['w'] + 2 * BOX_T}:h={b['h'] + 2 * BOX_T}:"
                   f"color=#{b.get('color', INK)}@0.95:t={BOX_T}:{en}")
    return ("," + ",".join(out)) if out else ""


def render_segment(v: dict, d: float, frames: int, out: Path) -> None:
    kind = v["type"]
    if kind == "seq":  # 한 비트 안에서 화면을 비율대로 나눠 잇는다
        parts, acc, f_done = [], 0.0, 0
        for i, sub in enumerate(v["items"]):
            acc += sub.get("frac", 1 / len(v["items"]))
            f_end = frames if i == len(v["items"]) - 1 else round(frames * acc)
            n = f_end - f_done
            po = out.with_name(f"{out.stem}_p{i}.mp4")
            render_segment(sub, n / FPS, n, po)
            parts.append(po); f_done = f_end
        lst = out.with_suffix(".txt")
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        return
    inp, vf = {"image": vf_image, "scroll": vf_scroll, "clip": vf_clip, "view": vf_view}[kind](v, d)
    vf += boxes_vf(v, d)
    fade = v.get("fade_in", 0)
    if fade:
        vf += f",fade=t=in:st=0:d={fade}:color=#fbfaf7"
    vf += f",format=yuv420p,trim=end_frame={frames},tpad=stop_mode=clone:stop={frames}"
    run(["ffmpeg", "-y", "-v", "error", *inp, "-vf", vf, "-frames:v", str(frames), "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(out)])


# ---------- 자막 ----------
def chunks(text: str, limit: int = 30) -> list[str]:
    parts = re.split(r"(?<=[.?!。])\s+|(?<=[,，])\s+", text.strip())
    res: list[str] = []
    for p in parts:
        while len(p) > limit:
            cut = p.rfind(" ", 0, limit)
            cut = cut if cut > limit * 0.4 else limit
            res.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            res.append(p)
    return res


def ass_time(t: float) -> str:
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Pretendard SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H1A30241B,&H1A30241B,0,0,0,0,100,100,0,0,3,14,0,2,80,80,46,1
Style: WM,Pretendard Medium,24,&H00303030,&H00FFFFFF,&H00E8EFF2,&H00E8EFF2,0,0,0,0,100,100,0,0,3,9,0,7,40,40,34,1
Style: Q,Pretendard Bold,64,&H00FFFFFF,&H00FFFFFF,&H0030241B,&H0030241B,0,0,0,0,100,100,0,0,3,22,0,1,110,40,170,1
Style: Tag,Pretendard Medium,26,&H00FFFFFF,&H00FFFFFF,&H005F3A1F,&H005F3A1F,0,0,0,0,100,100,1,0,3,10,0,9,40,40,34,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=str(HERE / "storyboard.json"))
    ap.add_argument("--only", default="")
    ap.add_argument("--no-burn", action="store_true")
    a = ap.parse_args()

    board = json.loads(Path(a.board).read_text(encoding="utf-8"))
    voice, rate = board.get("voice", "ko-KR-InJoonNeural"), board.get("rate", "+0%")
    only = set(filter(None, a.only.split(",")))
    (TMP / "seg").mkdir(parents=True, exist_ok=True)
    (TMP / "aud").mkdir(parents=True, exist_ok=True)

    t = 0.0
    seg_list, aud_list, events, timeline = [], [], [], []
    for sc in board["scenes"]:
        sc_start = t
        for bi, b in enumerate(sc["beats"]):
            bid = f"{sc['id']}_{bi:02d}"
            text = b.get("text", "")
            gap = b.get("gap", 0.7)
            if text:
                mp3 = tts(b.get("say") or to_say(text), voice, b.get("rate", rate))
                speech = duration(mp3)
            else:
                mp3, speech = None, 0.0
            d_raw = max(b.get("min", 0.0), speech + gap)
            f0, f1 = round(t * FPS), round((t + d_raw) * FPS)
            frames = f1 - f0
            d = frames / FPS
            seg = TMP / "seg" / f"{bid}.mp4"
            aud = TMP / "aud" / f"{bid}.wav"
            lead = b.get("lead", 0.0)  # 화면이 먼저 나오고 말이 늦게 시작
            if not only or sc["id"] in only or not seg.exists():
                render_segment(b["visual"], d, frames, seg)
            if mp3:
                run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-af",
                     f"adelay={int(lead*1000)}:all=1,apad,atrim=0:{d:.4f}", "-ar", str(SR), "-ac", "1", str(aud)])
            else:
                run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
                     "-t", f"{d:.4f}", str(aud)])
            seg_list.append(seg); aud_list.append(aud)
            # 자막: 말하는 구간을 글자 수 비율로 나눈다
            if text and not b.get("no_sub"):
                cs = chunks(b.get("sub", text))
                total = sum(len(c) for c in cs)
                ct = t + lead
                for c in cs:
                    cd = speech * len(c) / total
                    events.append(f"Dialogue: 0,{ass_time(ct)},{ass_time(ct + cd)},Sub,,0,0,0,,{c}")
                    ct += cd
            timeline.append({"beat": bid, "start": round(t, 2), "dur": round(d, 2), "text": text[:40]})
            t += d
        if sc.get("tag"):
            events.append(f"Dialogue: 1,{ass_time(sc_start)},{ass_time(t)},Tag,,0,0,0,,{sc['tag']}")
        if sc.get("wm"):
            events.append(f"Dialogue: 1,{ass_time(sc_start)},{ass_time(t)},WM,,0,0,0,,{sc['wm']}")
        if sc.get("q"):
            events.append(f"Dialogue: 2,{ass_time(sc_start + 0.1)},{ass_time(sc_start + sc.get('q_dur', 1.6))},Q,,0,0,0,,{{\\fad(120,200)}}{sc['q']}")

    (OUT / "subs.ass").write_text(ASS_HEAD + "\n".join(events) + "\n", encoding="utf-8")
    (OUT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")
    (TMP / "vlist.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in seg_list), encoding="utf-8")
    (TMP / "alist.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in aud_list), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(TMP / "vlist.txt"), "-c", "copy", str(TMP / "video.mp4")])
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(TMP / "alist.txt"),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", str(TMP / "audio.wav")])

    final = OUT / "doseverdict_demo.mp4"
    vf = "null"
    if not a.no_burn:
        # subtitles 필터는 경로의 콜론·역슬래시를 이스케이프해야 해서 out 폴더에서 상대 경로로 돌린다
        vf = "subtitles=subs.ass:fontsdir=../fonts"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "tmp/video.mp4", "-i", "tmp/audio.wav", "-vf", vf,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", final.name],
                   cwd=OUT, check=True)
    print(f"{final} {t:.1f}s ({int(t // 60)}:{t % 60:04.1f}), beats={len(seg_list)}")


if __name__ == "__main__":
    main()
