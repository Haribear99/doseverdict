"""storyboard.json + out/timeline.json → docs/시연영상_스크립트.md의 장면표 부분을 다시 쓴다.

실행: py -3.14 docs/video/export_script.py  (build.py 다음에)
문서의 "## 화면 수치 대조표" 이하는 그대로 둔다.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE.parent / "시연영상_스크립트.md"


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def screen(v: dict) -> str:
    k = v["type"]
    if k == "seq":
        return " → ".join(screen(x) for x in v["items"])
    src = v["src"]
    name = Path(src).stem
    if src.startswith("cards/"):
        return f"카드 `{name}`"
    if src.startswith("clips/"):
        return f"라이브 녹화 {v['start']:.0f}–{v['end']:.0f}초"
    if name.startswith("deck"):
        return f"덱 {name[4:]}장"
    demo, _, tab = name.partition("_")
    tab = {"find": "Findings", "tools": "도구 호출", "audit": "Audit", "retro": "후향 검증", "tl": "타임라인"}.get(tab, tab)
    return f"`?{demo.replace('d', 'demo=')}&cached=1` {tab}"


def main() -> None:
    board = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
    tl = {e["beat"]: e for e in json.loads((HERE / "out" / "timeline.json").read_text(encoding="utf-8"))}
    total = max(e["start"] + e["dur"] for e in tl.values())
    rows = []
    for sc in board["scenes"]:
        for i, b in enumerate(sc["beats"]):
            e = tl[f"{sc['id']}_{i:02d}"]
            rows.append(f"| {mmss(e['start'])} | {screen(b['visual'])} | {b.get('text') or '(무음)'} | {sc.get('tag', '') if i == 0 else ''} |")
    head = f"""# 시연 영상 스크립트 ({mmss(total)}, YouTube 일부 공개) — 2026-10-01 최종(제작본)

## 제작 방식

- 영상은 `docs/video/`의 스크립트로 만든다. 사람이 녹화하지 않는다. 다시 만들 때는 `docs/video/README.md` 순서대로 실행한다.
- 내레이션은 edge-tts `{board['voice']}`(한국어 신경망 음성)이고, 자막은 내레이션과 같은 문장을 번인한다. 화면 오른쪽 위에는 배점 항목을, 왼쪽 위에는 화면 출처(저장 결과·라이브·사후 분석)를 표시한다.
- 수치를 읽는 장면은 배포 Space의 저장 결과(`?demo=N&cached=1`) 캡처, 발표 덱, 카드(`docs/video/make_cards.py`, 값은 numbers.md·덱·라벨 원문)만 쓴다. 라이브 장면(`?demo=1&autorun=1`, Human Gate 승인까지 실제 클릭)에서는 수치를 읽지 않는다.
- GPT image 시안은 훅·챕터 카드의 구도 참고로만 썼다. 생성 이미지는 영상에 들어가지 않는다.
- 대본은 /panel(시안 3·심사 6·종합)로 만들고 red-judge 1회(조건부 → 13건 반영)를 거쳤다.

## 스크립트

| 시작 | 화면 | 내레이션(=자막) | 배점 |
|---|---|---|---|
"""
    old = DOC.read_text(encoding="utf-8")
    tail = old[old.index("## 화면 수치 대조표"):]
    DOC.write_text(head + "\n".join(rows) + "\n\n" + tail, encoding="utf-8", newline="\n")
    print(DOC, len(rows), mmss(total))


if __name__ == "__main__":
    main()
