"""
제안서 삽입용 그림 생성 (한글 HWPX 삽입용 PNG)

그림1  핵심 가치 — 문제 / 계산 / 출력
그림2  용량증량 설계 시뮬레이션 결과 (실측값)
그림3  에이전트 워크플로와 자기수정 루프
그림4  본선 시연 트레이스 — 한 문장이 통과하는 전 과정

박스 높이는 줄 수에서 자동 계산한다(텍스트 넘침 방지).
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.patches as mp
import matplotlib.pyplot as plt

OUT = "figures"

for cand in ("Malgun Gothic", "NanumGothic", "Gulim", "Batang"):
    if any(f.name == cand for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

# validate_palette.js 통과 — CVD ΔE 30.0 / normal ΔE 34.8
BLUE, AMBER = "#3B6FD6", "#E08A1E"
INK, INK2, MUTED, LINE = "#1c1c1e", "#55555c", "#8a8a92", "#d4d4d8"
SURF = "#ffffff"
TINT_B, TINT_A, TINT_G = "#eaf0fc", "#fdf3e3", "#f4f4f5"


class Fig:
    """축 단위(0~1)와 포인트 단위를 연결하는 얇은 래퍼."""

    def __init__(self, w_in, h_in):
        self.fig, self.ax = plt.subplots(figsize=(w_in, h_in), dpi=200)
        self.ax.set_xlim(0, 1); self.ax.set_ylim(0, 1); self.ax.axis("off")
        self.fig.patch.set_facecolor(SURF)
        self.h_in = h_in

    def pt(self, size):
        """폰트 크기(pt) → 축 세로 단위."""
        return size / (self.h_in * 72.0)

    def box_h(self, n_lines, tsize=10.5, bsize=9.0, pad_top=0.9, pad_bot=1.75):
        """줄 수에서 박스 높이를 계산한다.

        마지막 줄은 va="top" 기준이라 글자 높이만큼 아래로 더 내려간다.
        pad_bot에 그 몫(약 1.0)과 여백(약 0.75)을 함께 넣는다.
        """
        return (self.pt(tsize) * (1.35 + pad_top)
                + self.pt(bsize) * 1.62 * n_lines
                + self.pt(bsize) * pad_bot)

    def box(self, x, y_top, w, title, lines, fill=SURF, edge=LINE, tcol=INK,
            tsize=10.5, bsize=9.0, lw=1.3, h=None):
        """y_top을 기준으로 아래로 그린다. 실제 높이를 반환."""
        hh = h if h is not None else self.box_h(len(lines), tsize, bsize)
        self.ax.add_patch(mp.FancyBboxPatch(
            (x, y_top - hh), w, hh,
            boxstyle="round,pad=0,rounding_size=0.010",
            linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2))
        ty = y_top - self.pt(tsize) * 1.35
        self.ax.text(x + 0.014, ty, title, fontsize=tsize, fontweight="bold",
                     color=tcol, va="top", ha="left", zorder=3)
        yy = ty - self.pt(tsize) * 0.9 - self.pt(bsize) * 1.30
        for ln in lines:
            self.ax.text(x + 0.014, yy, ln, fontsize=bsize, color=INK2,
                         va="top", ha="left", zorder=3)
            yy -= self.pt(bsize) * 1.62
        return hh

    def arrow(self, x1, y1, x2, y2, color=MUTED, lw=1.5, ls="-", rad=None):
        cs = f"arc3,rad={rad}" if rad else "arc3,rad=0"
        self.ax.add_patch(mp.FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
            linewidth=lw, color=color, linestyle=ls, zorder=1,
            connectionstyle=cs, shrinkA=0, shrinkB=0))

    def save(self, name):
        self.fig.savefig(f"{OUT}/{name}", bbox_inches="tight",
                         facecolor=SURF, pad_inches=0.12)
        plt.close(self.fig)


# ====================================================== 그림 1
def fig1():
    f = Fig(12.0, 5.6); ax = f.ax
    ax.text(0.5, 0.975, "프로토콜을 읽는 AI는 이미 많다. DoseVerdict는 프로토콜을 계산한다.",
            fontsize=15, fontweight="bold", color=INK, ha="center", va="top")

    top = 0.875
    h1 = f.box(0.012, top, 0.300,
               "문제 — 승인된 약에서 일어난 일",
               ["소토라십(LUMAKRAS) FDA 승인 라벨",
                "",
                "· 180~960 mg 구간에서 정상상태",
                "  노출량(AUC, Cmax)이 유사 (라벨 12.3)",
                "  → 5.3배 증량이 노출을 늘리지 못함",
                "",
                "· \"노출-반응 관계는 알려지지 않음\"",
                "  (라벨 12.2 원문)",
                "",
                "· 그럼에도 최대용량이 승인 용량이 됨",
                "· FDA는 승인과 동시에 960 vs 240 mg",
                "  비교를 시판후 요구사항으로 부과"],
               fill=TINT_A, edge=AMBER, tcol="#8a5510", tsize=10.5)

    f.box(0.348, top, 0.310, "DoseVerdict — 계산으로 반박",
          ["네 가지 계산",
           "   ChEMBL 효력값 분포 (IC50 / Ki)",
           "   openFDA 라벨 PK (노출 · 경고)",
           "   RDKit 구조 → 반응성 계열 분류",
           "   용량증량 설계 몬테카를로",
           "",
           "세 관점이 서로 다른 근거만 본다",
           "   규제기관 / 시험기관 / 환자 부담",
           "",
           "근거가 결론을 지탱하지 못하면",
           "결론을 만들지 않는다",
           "   지표별 판정이 갈리면 → 보류 · 재계획"],
          fill=TINT_B, edge=BLUE, tcol="#1e4699", tsize=10.5, h=h1)

    f.box(0.694, top, 0.294, "출력 — 사람이 판단할 재료",
          ["· 위험도순 Gap Matrix",
           "· 문장 단위 수정안 (Diff)",
           "· 예상 규제기관 질의",
           "· 시험기관 실행가능성 보드",
           "· 환자 부담 요약",
           "· 근거 · 버전 · 검색일 감사 로그",
           "",
           "모든 수정은",
           "사람의 승인 후에만 반영된다"],
          fill=TINT_G, edge=LINE, tsize=10.5, h=h1)

    mid = top - h1 / 2
    f.arrow(0.316, mid, 0.344, mid, color=AMBER, lw=1.9)
    f.arrow(0.662, mid, 0.690, mid, color=BLUE, lw=1.9)

    by = top - h1 - 0.045
    ax.add_patch(mp.FancyBboxPatch(
        (0.012, by - 0.175), 0.976, 0.175,
        boxstyle="round,pad=0,rounding_size=0.010",
        linewidth=1.3, edgecolor=LINE, facecolor="#fafafa", zorder=2))
    ax.text(0.030, by - 0.030,
            "\"The MTD will be selected as the RP2D.\" 라는 한 문장에 대한 판정 차이",
            fontsize=11, fontweight="bold", color=INK, va="top")
    ax.text(0.030, by - 0.083,
            "일반적 규제 문서 에이전트     \"가이드라인상 이익-위험 비교 계획이 필요합니다\"",
            fontsize=9.8, color=MUTED, va="top")
    ax.text(0.030, by - 0.130,
            "DoseVerdict     \"이 조건에서 3+3은 증량 16명으로 참 MTD를 27.6%에서만 맞히고 "
            "17.1%에서는 확정조차 못 합니다\"",
            fontsize=9.8, fontweight="bold", color=BLUE, va="top")
    f.save("그림1_핵심가치.png")


# ====================================================== 그림 2
def fig2():
    f = Fig(13.0, 7.9); ax = f.ax
    ax.text(0.5, 0.982, "에이전트 워크플로 — 자율적 계획, 도구 호출, 그리고 자기수정 루프",
            fontsize=14.5, fontweight="bold", color=INK, ha="center", va="top")

    C1, C2, C3, C4 = 0.012, 0.245, 0.520, 0.795
    W1, W2, W3, W4 = 0.205, 0.245, 0.245, 0.193
    TS, BS = 10.0, 8.6

    f.box(C1, 0.910, W1, "입력",
          ["프로토콜 초안 synopsis", "시험약 구조 (SMILES)",
           "용량 · 노출표", "대상 국가 (한국 · 미국)"], fill=TINT_G, tsize=TS, bsize=BS)
    f.box(C1, 0.680, W1, "Protocol Compiler",
          ["비정형 문서 → Trial Schema", "Pydantic 형식 강제"], tsize=TS, bsize=BS)
    h_orc = f.box(C1, 0.480, W1, "Orchestrator",
                  ["필드 결측 · 상충 → 과제 DAG",
                   "도구 선택 = 추출 필드가 결정",
                   "재계획 트리거 6종",
                   "Gap당 최대 3회 · 예산 상한"],
                  fill=TINT_B, edge=BLUE, tcol="#1e4699", tsize=TS, bsize=BS)
    f.arrow(C1 + W1 / 2, 0.755, C1 + W1 / 2, 0.686, lw=1.3)
    f.arrow(C1 + W1 / 2, 0.556, C1 + W1 / 2, 0.486, lw=1.3)

    tools = [
        ("Pharmacology Evidence", ["RDKit · ChEMBL", "openFDA · Open Targets",
                                   "→ Target Coverage Ratio"], True),
        ("Trial Design Simulator", ["NumPy 몬테카를로", "3+3 / BOIN / mTPI-2",
                                    "→ 정확 MTD 선택률"], True),
        ("Regulatory Evidence", ["BM25 + 임베딩 하이브리드", "ICH · FDA · 식약처",
                                 "→ 조항 · 버전 · 적용국가"], False),
        ("Analog Trial", ["ClinicalTrials.gov API v2", "유사시험 설계 비교"], False),
    ]
    y = 0.905
    centers = []
    for name, lines, calc in tools:
        hh = f.box(C2, y, W2, name, lines,
                   fill=TINT_A if calc else SURF,
                   edge=AMBER if calc else LINE,
                   tcol="#8a5510" if calc else INK, tsize=TS, bsize=BS)
        centers.append(y - hh / 2)
        y -= hh + 0.038
    for cy in centers:
        f.arrow(C1 + W1 + 0.006, 0.480 - h_orc / 2, C2 - 0.004, cy, lw=1.0)

    h_arena = f.box(C3, 0.905, W3, "Adversarial Review Arena",
                    ["세 검토자가 서로 다른 근거만 본다", "",
                     "· 규제기관 Reviewer — 조항 · 규범 강도",
                     "· 시험기관 Reviewer — 방문 · 운영 부담",
                     "· 환자 부담 Reviewer — 투여기간 · 채혈량", "",
                     "서로의 결론을 보지 못한다",
                     "합의를 강제하지 않는다"],
                    fill=TINT_B, edge=BLUE, tcol="#1e4699", tsize=TS, bsize=BS)
    y_ver = 0.905 - h_arena - 0.055
    h_ver = f.box(C3, y_ver, W3, "Citation & Consistency Verifier",
                  ["전용 NLI 모델로 주장-근거 함의 판정",
                   "인용 버전 · 적용국가 검사",
                   "문서 내부 모순 검사"], tsize=TS, bsize=BS)
    for cy in centers:
        f.arrow(C2 + W2 + 0.004, cy, C3 - 0.004, 0.905 - h_arena / 2, lw=1.0)
    f.arrow(C3 + W3 / 2, 0.905 - h_arena - 0.004, C3 + W3 / 2, y_ver + 0.006,
            color=BLUE, lw=1.6)

    h_jud = f.box(C4, 0.905, W4, "판정",
                  ["근거 충분 → 통과", "근거 부족 → 기권",
                   "상충 → 상충 상태로 전달", "검증 실패 → 재계획"], tsize=TS, bsize=BS)
    y_gate = 0.905 - h_jud - 0.075
    f.box(C4, y_gate, W4, "Human Approval Gate",
          ["사람만 최종 승인한다", "승인 / 부분승인 / 보류", "감사 로그 기록"],
          fill=TINT_G, edge=INK2, tsize=TS, bsize=BS)
    f.arrow(C3 + W3 + 0.004, 0.905 - h_arena / 2, C4 - 0.004, 0.905 - h_jud / 2, lw=1.3)
    f.arrow(C4 + W4 / 2, 0.905 - h_jud - 0.004, C4 + W4 / 2, y_gate + 0.006, lw=1.3)

    # 자기수정 루프 — 모든 박스 아래로 우회해 Orchestrator로 복귀
    y_bot = min(y - 0.038, y_gate - f.box_h(3, TS, BS))  # 가장 낮은 박스 하단
    y_route = y_bot - 0.055
    x_from, x_to = C4 + W4 / 2, C1 + W1 / 2
    dash = dict(color=AMBER, linewidth=2.1, linestyle=(0, (6, 3)),
                zorder=4, solid_capstyle="butt")
    ax.plot([x_from, x_from], [y_gate - f.box_h(3, TS, BS) - 0.004, y_route], **dash)
    ax.plot([x_from, x_to], [y_route, y_route], **dash)
    ax.add_patch(mp.FancyArrowPatch(
        (x_to, y_route), (x_to, 0.480 - h_orc - 0.006),
        arrowstyle="-|>", mutation_scale=16, linewidth=2.1, color=AMBER,
        linestyle=(0, (6, 3)), shrinkA=0, shrinkB=0, zorder=4))
    ax.text(0.5, y_route - 0.048,
            "자기수정 루프 — 근거 부족 · 상충 · 검증 실패를 스스로 감지하면 "
            "결론을 폐기하고 Orchestrator로 되돌려 재계획한다",
            fontsize=10.5, fontweight="bold", color="#8a5510",
            ha="center", va="top")
    f.save("그림3_워크플로.png")


# ====================================================== 그림 3
def fig3():
    f = Fig(13.0, 7.2); ax = f.ax
    ax.text(0.5, 0.983, "본선 시연 시나리오 — 프로토콜 한 문장이 시스템을 통과하는 전 과정",
            fontsize=14.5, fontweight="bold", color=INK, ha="center", va="top")
    ax.text(0.5, 0.944, "아래 값은 전부 2026-08-07에 공식 API로 실제 조회 · 계산한 결과다",
            fontsize=9.8, color=MUTED, ha="center", va="top", style="italic")

    ax.add_patch(mp.FancyBboxPatch(
        (0.13, 0.822), 0.74, 0.088,
        boxstyle="round,pad=0,rounding_size=0.010",
        linewidth=1.7, edgecolor=AMBER, facecolor=TINT_A, zorder=2))
    ax.text(0.5, 0.895, "입력 문장   \"The MTD will be selected as the RP2D.\"",
            fontsize=12.5, fontweight="bold", color="#8a5510", ha="center", va="top")
    ax.text(0.5, 0.855, "최대내약용량을 그대로 권장 2상 용량으로 삼는다",
            fontsize=9.3, color=INK2, ha="center", va="top")

    cols = [
        ("ChEMBL", ["KRAS 표적 활성 11건", "중앙값 68 nM / 최소 7 nM"]),
        ("openFDA 라벨", ["\"180~960 mg 노출 유사\"", "\"노출-반응 관계 미상\""]),
        ("RDKit", ["cLogP 4.48 / 구조알림 3건", "→ 간독성 모니터링 필요"]),
        ("설계 시뮬레이터", ["3+3 정확MTD 29.5% / 표본 14.1명", "BOIN 53.6% / 34.8명 (40,000회)"]),
    ]
    x0, w, gap = 0.020, 0.234, 0.014
    for i, (name, lines) in enumerate(cols):
        x = x0 + i * (w + gap)
        hh = f.box(x, 0.762, w, name, lines, edge=BLUE, tcol="#1e4699",
                   tsize=10, bsize=8.8)
        f.arrow(0.5, 0.818, x + w / 2, 0.768, lw=1.0)
    y_after = 0.762 - hh

    revs = [("규제 Reviewer", "High", "이익-위험 용량 비교 계획 부재", AMBER),
            ("시험기관 PI · CRC", "Medium", "감량 · 중단 관리 부담 증가", MUTED),
            ("환자 부담 Reviewer", "High", "이익 근거 없는 고용량 장기 투여", AMBER)]
    ax.text(0.5, y_after - 0.038,
            "적대검토 — 세 관점이 서로 다른 결론을 낸다 (합의 강제 없음)",
            fontsize=10, fontweight="bold", color=INK2, ha="center", va="top")
    ry = y_after - 0.075
    rw = 0.318
    for i, (nm, lv, rs, c) in enumerate(revs):
        x = 0.020 + i * (rw + 0.013)
        ax.add_patch(mp.FancyBboxPatch(
            (x, ry - 0.098), rw, 0.098,
            boxstyle="round,pad=0,rounding_size=0.010",
            linewidth=1.3, edgecolor=c, facecolor=SURF, zorder=2))
        ax.text(x + 0.014, ry - 0.022, nm, fontsize=9.8, fontweight="bold",
                color=INK, va="top")
        ax.text(x + rw - 0.014, ry - 0.022, lv, fontsize=9.8, fontweight="bold",
                color=c, va="top", ha="right")
        ax.text(x + 0.014, ry - 0.062, rs, fontsize=8.8, color=INK2, va="top")

    y2 = ry - 0.098 - 0.045
    f.box(0.020, y2, 0.470, "인용 검증기가 주장을 기각하는 장면",
          ["초안 생성 문장",
           "   \"식약처도 동일한 용량 비교를 의무화하고 있다\"",
           "→ 뒷받침할 한국 규정 조항을 찾지 못함",
           "→ 문장 기각, \"국가별 요구 차이 확인 필요\"로 대체"],
          fill=TINT_G, edge=INK2, tsize=10, bsize=8.7)
    h_diff = f.box(0.512, y2, 0.468, "최종 수정안 (Diff)",
                   ["(삭제) The MTD will be selected as the RP2D.",
                    "(추가) 두 개 이상의 후보 용량을 무작위 배정해",
                    "         안전성 · 내약성 · PK · PD · 초기 항종양 활성을",
                    "         비교한 뒤 RP2D를 선정한다."],
                   edge=BLUE, tcol="#1e4699", tsize=10, bsize=8.7)
    f.arrow(0.255, ry - 0.100, 0.255, y2 + 0.006, lw=1.2)
    f.arrow(0.746, ry - 0.100, 0.746, y2 + 0.006, lw=1.2)

    y3 = y2 - h_diff - 0.048
    ax.add_patch(mp.FancyBboxPatch(
        (0.22, y3 - 0.105), 0.56, 0.105,
        boxstyle="round,pad=0,rounding_size=0.010",
        linewidth=1.7, edgecolor=INK2, facecolor="#fafafa", zorder=2))
    ax.text(0.5, y3 - 0.026, "Human Approval Gate — 사람만 최종 승인한다",
            fontsize=11.5, fontweight="bold", color=INK, ha="center", va="top")
    ax.text(0.5, y3 - 0.068,
            "승인 / 부분승인 / 보류  ·  근거 · 도구 호출 · 모델 버전 · 검색일 · 승인자가 감사 로그에 기록",
            fontsize=8.8, color=INK2, ha="center", va="top")
    f.arrow(0.5, y2 - h_diff - 0.004, 0.5, y3 + 0.006, color=INK2, lw=1.6)
    f.save("그림4_시연트레이스.png")


# ====================================================== 그림 4
def fig4():
    scen = ["S1\n저용량이 MTD", "S2\n중간이 MTD", "S3\n고용량이 MTD",
            "S4\n전반적 안전", "평균"]
    p33 = [37.2, 26.2, 22.1, 32.4, 29.5]
    boin = [65.7, 48.4, 41.6, 58.6, 53.6]

    fig, ax = plt.subplots(figsize=(9.4, 4.4), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    xs = list(range(len(scen))); bw = 0.36

    b1 = ax.bar([x - bw / 2 - 0.010 for x in xs], p33, bw, label="3+3 설계",
                color=AMBER, edgecolor=SURF, linewidth=2)
    b2 = ax.bar([x + bw / 2 + 0.010 for x in xs], boin, bw, label="BOIN 설계",
                color=BLUE, edgecolor=SURF, linewidth=2)
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 1.5,
                    f"{r.get_height():.1f}", ha="center", va="bottom",
                    fontsize=9.5, fontweight="bold", color=INK)

    ax.set_ylabel("정확 MTD 선택률 (%)", fontsize=10.5, color=INK2)
    ax.set_title("용량증량 설계 Operating Characteristics\n"
                 "목표 DLT율 30%, 용량군 6개, 4시나리오 x 10,000회 = 40,000회",
                 fontsize=12, fontweight="bold", color=INK, pad=12)
    ax.set_xticks(xs); ax.set_xticklabels(scen, fontsize=9.5, color=INK2)
    ax.set_ylim(0, 76)
    ax.legend(frameon=False, fontsize=10, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=2)
    ax.grid(axis="y", color=LINE, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(axis="y", colors=MUTED, labelsize=9, length=0)
    ax.tick_params(axis="x", colors=INK2, length=0)
    fig.text(0.5, -0.10,
             "정확도만 표시. 평균 표본수 3+3 14.1명 vs BOIN 34.8명, 과다투여 노출 1.4명 vs 4.9명 — 본문 표 참조   ·   "
             "재현 코드: evidence/dose_escalation_sim.py",
             fontsize=8.5, color=MUTED, ha="center")

    fig.savefig(f"{OUT}/그림2_설계시뮬레이션.png", bbox_inches="tight",
                facecolor=SURF, pad_inches=0.16)
    plt.close(fig)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2(); fig3(); fig4()
    for fn in sorted(os.listdir(OUT)):
        print(f"  생성: {OUT}/{fn}  ({os.path.getsize(os.path.join(OUT, fn)):,} bytes)")
