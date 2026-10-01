"""덱·기술서용 도표 — 값은 docs/numbers.md와 evidence/tcr_240mg.json에서 파싱한다(하드코딩 없음).

실행: py -3.14 docs/figs/make_figs.py  → docs/figs/*.png (300 dpi)
색: app/ui/tokens.py(강조 1색 accent, 나머지 ink·muted). 상태 4색은 쓰지 않는다(판정 상태 전용, docs/DESIGN.md).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.ui import tokens as T  # noqa: E402

OUT = Path(__file__).resolve().parent
FONTS = ROOT / "docs" / "video" / "fonts"
for f in FONTS.glob("Pretendard-*.otf"):
    font_manager.fontManager.addfont(str(f))
plt.rcParams.update({
    "font.family": "Pretendard", "font.size": 11, "axes.edgecolor": T.LINE, "axes.labelcolor": T.MUTED,
    "xtick.color": T.MUTED, "ytick.color": T.INK, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "figure.facecolor": T.PAPER, "axes.facecolor": T.PAPER, "savefig.facecolor": T.PAPER,
    "axes.unicode_minus": False,
})
NUM = (ROOT / "docs" / "numbers.md").read_text(encoding="utf-8")
CI = r"(-?[\d.]+) \[(-?[\d.+]+), (-?[\d.+]+)\]"


def ci(s: str) -> tuple[float, float, float]:
    m = re.search(CI, s)
    return float(m.group(1)), float(m.group(2)), float(m.group(3))


def save(fig, name):
    fig.savefig(OUT / name, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(name)


def fig_tcr240():
    d = json.loads((ROOT / "evidence" / "tcr_240mg.json").read_text(encoding="utf-8"))
    rows = d["rows"]
    fig, ax = plt.subplots(figsize=(7.6, 2.5))
    metrics = [("TCR_max", "C_max", "^"), ("TCR_avg", "C_avg", "o"), ("TCR_trough", "C_trough", "s")]
    for yi, r in enumerate(rows):
        y = len(rows) - 1 - yi
        xs = [r[k] for k, _, _ in metrics]
        ax.plot([min(xs), max(xs)], [y, y], color=T.LINE, lw=2, zorder=1)
        for k, lab, mk in metrics:
            v = r[k]
            below = v < 1
            ax.scatter(v, y, marker=mk, s=70, color=T.ACCENT if below else T.INK, zorder=3, edgecolor=T.PAPER, linewidth=1.5)
            ax.annotate(f"{lab} {v:.2f}" if v < 2 else f"{lab} {v:.1f}", (v, y), xytext=(0, 11), textcoords="offset points",
                        ha="center", fontsize=9.5, color=T.ACCENT if below else T.INK, fontweight=700 if below else 500)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["assumption"] for r in reversed(rows)], fontsize=11)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 100)
    ax.set_ylim(-0.6, len(rows) - 0.25)
    ax.set_xticks([0.1, 1, 10, 100])
    ax.set_xticklabels(["0.1", "1", "10", "100"])
    for x, lab in [(1, "1 미만 = 표적 미커버"), (10, "10 초과 = 포화 의심(잠정)")]:
        ax.axvline(x, color=T.MUTED, lw=0.8, ls=(0, (3, 3)), zorder=0)
        ax.text(x * 1.06, -0.55, lab, fontsize=8.5, color=T.MUTED, va="bottom")
    ax.set_xlabel("TCR = 유리 농도 / IC50 (로그 축) · 소토라십 240 mg · 라벨 PK · IC50 30 nM", fontsize=9)
    ax.tick_params(axis="y", length=0)
    save(fig, "tcr240.png")


def fig_retro():
    sec = NUM[NUM.index("## 1-4."):NUM.index("## 1-5.")]
    rows = []
    for line in sec.splitlines():
        m = re.match(r"\| (S1|S2|B1|B2|B3|B4) \| (.+?) \| (\d+) \| " + CI, line)
        if m:
            rows.append((m.group(1), m.group(2), int(m.group(3)), float(m.group(4)), float(m.group(5)), float(m.group(6))))
    assert len(rows) == 6, rows
    names = {"S1": "S1 에이전트 1차 점수(사전 등록)", "S2": "S2 에이전트 2차 점수", "B1": "B1 키워드 규칙", "B2": "B2 승인연도",
             "B3": "B3 승인 후 라벨 규칙(참고)", "B4": "B4 약 이름을 준 모델 기억(사후)"}
    fig, ax = plt.subplots(figsize=(7.6, 3.1))
    for i, (k, _, n, est, lo, hi) in enumerate(rows):
        y = len(rows) - 1 - i
        c = T.ACCENT if k == "S1" else T.MUTED
        ax.plot([lo, hi], [y, y], color=c, lw=2.2 if k == "S1" else 1.6, solid_capstyle="round")
        ax.scatter(est, y, s=60 if k == "S1" else 40, color=c, zorder=3, edgecolor=T.PAPER, linewidth=1.5)
        ax.text(hi + 0.012, y, f"{est:.3f} [{lo:.3f}, {hi:.3f}]" + (f" · n={n}" if n != 43 else ""), va="center",
                fontsize=9, color=T.INK if k == "S1" else T.MUTED, fontweight=700 if k == "S1" else 400)
    ax.axvline(0.5, color=T.INK, lw=0.9)
    ax.text(0.495, len(rows) - 0.35, "0.5 = 무작위", ha="right", fontsize=8.5, color=T.INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([names[r[0]] for r in reversed(rows)], fontsize=10)
    ax.set_xlim(0.2, 1.08)
    ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xlabel("AUROC [95% CI] · 승인 전 1상 초록 43건(양성 14) · FDA 용량최적화 PMR/PMC", fontsize=9)
    ax.tick_params(axis="y", length=0)
    save(fig, "retro_auroc.png")


def fig_oneshot():
    sec = NUM[NUM.index("## 1-5."):NUM.index("## 1-6.")]
    pre = next(l for l in sec.splitlines() if l.startswith("| oneshot(2회 평균)"))
    p1 = next(l for l in sec.splitlines() if "대칭 필터(원문 일치만)" in l)
    p2 = next(l for l in sec.splitlines() if "대칭 필터(일치 또는 NLI 의역)" in l)
    rows = [("사전 등록 · grounded 차이", ci(pre.split("|")[4]), True),
            ("사후 · 원문 일치 필터를 양쪽에", ci(p1.split("차이(원샷 − 에이전트)")[1]), False),
            ("사후 · 일치 또는 NLI 의역 필터를 양쪽에", ci(p2.split("차이(원샷 − 에이전트)")[1]), False)]
    fig, ax = plt.subplots(figsize=(7.6, 2.4))
    for i, (lab, (est, lo, hi), prereg) in enumerate(rows):
        y = len(rows) - 1 - i
        c = T.ACCENT if prereg else T.MUTED
        ax.plot([lo, hi], [y, y], color=c, lw=2.2 if prereg else 1.6, solid_capstyle="round")
        ax.scatter(est, y, s=60 if prereg else 40, color=c, zorder=3, edgecolor=T.PAPER, linewidth=1.5)
        ax.text(max(hi, 0) + 0.012, y, f"{est:+.3f} [{lo:+.3f}, {hi:+.3f}]", va="center", fontsize=9,
                color=T.INK if prereg else T.MUTED, fontweight=700 if prereg else 400)
    ax.axvline(0, color=T.INK, lw=0.9)
    ax.text(0.005, len(rows) - 0.4, "0 = 차이 없음", fontsize=8.5, color=T.INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=10)
    ax.set_xlim(-0.47, 0.25)
    ax.set_ylim(-0.6, len(rows) - 0.15)
    ax.set_xlabel("차이(원샷 − 에이전트) [95% CI] · 합성 원 20 · 왼쪽일수록 에이전트가 높음 · 사후 판정기는 에이전트 검증기와 같은 NLI", fontsize=8.5)
    ax.tick_params(axis="y", length=0)
    save(fig, "oneshot_diff.png")


if __name__ == "__main__":
    fig_tcr240()
    fig_retro()
    fig_oneshot()
