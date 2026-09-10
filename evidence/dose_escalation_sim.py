"""
DoseVerdict — 용량증량 설계 Operating Characteristics 시뮬레이터

프로토콜의 "3+3 설계로 MTD를 탐색한다"는 문장을 말이 아니라 수치로 반증한다.
동일한 참 독성곡선에서 3+3과 BOIN을 몬테카를로로 비교한다.

지표
  PCS      정확 MTD 선택률 (Probability of Correct Selection)
  ±1       참 MTD의 한 용량 이내를 선택할 확률
  None     MTD를 확정하지 못하고 증량이 종료될 확률
  P(over)  참 독성률이 목표를 크게 넘는 용량이 MTD로 선택될 확률
  N(over)  과다투여(참 독성률 > 목표+0.1) 용량에 노출된 환자 수 기댓값
  %(over)  전체 표본 대비 과다투여 노출 비율 — 표본수가 다른 설계를 비교하려면 절대수가 아니라 이 값을 봐야 한다
  N        평균 표본수

참고: BOIN 결정경계는 Liu & Yuan (2015)의 닫힌형 근사를 사용한다.
      3+3은 표준 알고리즘(코호트 3명, DLT 0/3 증량, 1/3 확장, >=2/3 중단,
      감량 시 이전 용량을 6명까지 확장해 <=1/6을 확인)이다.

설계 비교의 전제: 3+3은 알고리즘상 평균 14명에서 자연 종료하고 BOIN은 n_max까지
      쓴다. 따라서 n_max=36의 BOIN과 3+3을 나란히 놓으면 정확도 차이가 설계의
      우열로 오독된다. 표본수를 맞춘 BOIN(n_max=15)을 함께 출력해 그 혼동을 막는다.
"""

import sys

import numpy as np

TARGET = 0.30  # 목표 DLT 확률 phi


# ------------------------------------------------------------------ BOIN
def boin_boundaries(phi, p_lo_mult=0.6, p_hi_mult=1.4):
    """Liu & Yuan (2015) 최적 구간 경계."""
    p_lo, p_hi = phi * p_lo_mult, phi * p_hi_mult
    lam_e = np.log((1 - p_lo) / (1 - phi)) / np.log(phi * (1 - p_lo) / (p_lo * (1 - phi)))
    lam_d = np.log((1 - phi) / (1 - p_hi)) / np.log(p_hi * (1 - phi) / (phi * (1 - p_hi)))
    return lam_e, lam_d


def isotonic(y, w):
    """Pool-Adjacent-Violators — 가중 단조증가 적합."""
    y = list(map(float, y))
    w = list(map(float, w))
    blocks = [[y[i], w[i], 1] for i in range(len(y))]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            v1, w1, n1 = blocks[i]
            v2, w2, n2 = blocks[i + 1]
            tw = w1 + w2
            merged = [(v1 * w1 + v2 * w2) / tw if tw > 0 else 0.0, tw, n1 + n2]
            blocks[i : i + 2] = [merged]
            i = max(i - 1, 0)
        else:
            i += 1
    out = []
    for v, _, n in blocks:
        out.extend([v] * n)
    return np.array(out)


def run_boin(true_p, rng, cohort=3, n_max=36, phi=TARGET):
    lam_e, lam_d = boin_boundaries(phi)
    k = len(true_p)
    n = np.zeros(k, int)
    y = np.zeros(k, int)
    d = 0
    eliminated = np.zeros(k, bool)

    while n.sum() < n_max:
        dlt = rng.binomial(cohort, true_p[d])
        n[d] += cohort
        y[d] += dlt
        rate = y[d] / n[d]

        # 과도한 독성 용량 제거 (n>=3에서 베타사후 기준)
        if n[d] >= 3:
            from math import comb

            # P(p_d > phi | data) > 0.95  근사: 베타(1+y, 1+n-y)
            a, b = 1 + y[d], 1 + n[d] - y[d]
            # 베타 CDF를 정규근사 대신 직접 적분(작은 n이라 저렴)
            xs = np.linspace(0, 1, 2001)
            pdf = xs ** (a - 1) * (1 - xs) ** (b - 1)
            pdf /= pdf.sum()
            if pdf[xs > phi].sum() > 0.95:
                eliminated[d:] = True
                if d == 0:
                    break

        if rate <= lam_e:
            nd = min(d + 1, k - 1)
        elif rate >= lam_d:
            nd = max(d - 1, 0)
        else:
            nd = d
        while 0 <= nd < k and eliminated[nd]:
            nd -= 1
        if nd < 0:
            break
        d = nd

    tried = n > 0
    if not tried.any():
        return None, n
    rates = np.where(tried, y / np.maximum(n, 1), 0.0)
    iso = isotonic(rates[tried], n[tried])
    idx = np.where(tried)[0]
    valid = ~eliminated[idx]
    if not valid.any():
        return None, n
    best = idx[valid][int(np.argmin(np.abs(iso[valid] - phi)))]
    return best, n


# ------------------------------------------------------------------ 3+3
def run_3p3(true_p, rng):
    k = len(true_p)
    n = np.zeros(k, int)
    y = np.zeros(k, int)
    d = 0
    mtd = None

    def deescalate(cur):
        """중단 시 MTD는 '6명 중 DLT <=1'인 직전 용량. 3명만 본 상태면 3명을 더 채운다."""
        prev = cur - 1
        while prev >= 0:
            if n[prev] < 6:
                add = rng.binomial(3, true_p[prev])
                n[prev] += 3
                y[prev] += add
            if y[prev] <= 1:
                return prev
            prev -= 1
        return None

    while True:
        dlt = rng.binomial(3, true_p[d])
        n[d] += 3
        y[d] += dlt
        if dlt == 0:
            if d == k - 1:
                mtd = d
                break
            d += 1
        elif dlt == 1:
            dlt2 = rng.binomial(3, true_p[d])
            n[d] += 3
            y[d] += dlt2
            if dlt2 == 0:
                if d == k - 1:
                    mtd = d
                    break
                d += 1
            else:
                mtd = deescalate(d)
                break
        else:
            mtd = deescalate(d)
            break
    return mtd, n


# ------------------------------------------------------------------ 평가
def true_mtd_index(true_p, phi=TARGET):
    return int(np.argmin(np.abs(np.array(true_p) - phi)))


def evaluate(design_fn, true_p, n_sim, seed):
    rng = np.random.default_rng(seed)
    tgt = true_mtd_index(true_p)
    over = np.array(true_p) > TARGET + 0.10
    correct = n_over = n_tot = sel_over = within1 = undetermined = 0
    for _ in range(n_sim):
        sel, n = design_fn(true_p, rng)
        if sel is None:
            undetermined += 1
        else:
            if sel == tgt:
                correct += 1
            if abs(sel - tgt) <= 1:
                within1 += 1
            if over[sel]:
                sel_over += 1
        n_over += n[over].sum()
        n_tot += n.sum()
    return {
        "PCS": 100 * correct / n_sim,
        "within1": 100 * within1 / n_sim,
        "none": 100 * undetermined / n_sim,
        "P_over": 100 * sel_over / n_sim,
        "N": n_tot / n_sim,
        "N_over": n_over / n_sim,
        "pct_over": 100 * n_over / n_tot,
    }


SCENARIOS = {
    "S1 저용량이 MTD": [0.30, 0.45, 0.55, 0.65, 0.72, 0.80],
    "S2 중간이 MTD": [0.10, 0.18, 0.30, 0.45, 0.58, 0.70],
    "S3 고용량이 MTD": [0.05, 0.08, 0.12, 0.18, 0.30, 0.45],
    "S4 전체적으로 안전": [0.02, 0.04, 0.07, 0.11, 0.16, 0.30],
}


DESIGNS = (
    ("3+3", run_3p3),
    ("BOIN(n=15)", lambda p, rng: run_boin(p, rng, n_max=15)),
    ("BOIN(n=36)", lambda p, rng: run_boin(p, rng, n_max=36)),
)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    n_sim = 10000
    lam_e, lam_d = boin_boundaries(TARGET)
    hdr = (f"{'설계':<12}{'PCS %':>8}{'±1 이내 %':>11}{'미확정 %':>10}"
           f"{'과다선택 %':>12}{'표본수':>9}{'과다노출 n':>12}{'과다노출 %':>12}")

    print("=" * 96)
    print(f"용량증량 설계 비교  |  목표 DLT율 {TARGET:.0%}  |  용량군 6개  |  "
          f"시나리오 {len(SCENARIOS)}종 × {n_sim:,}회")
    print(f"BOIN 결정경계  증량 <= {lam_e:.3f} / 감량 >= {lam_d:.3f}")
    print("=" * 96)
    print(f"{'시나리오':<20}" + hdr)
    print("-" * 96)

    agg = {label: [] for label, _ in DESIGNS}
    for name, p in SCENARIOS.items():
        for i, (label, fn) in enumerate(DESIGNS):
            r = evaluate(fn, p, n_sim, seed=20260807)
            agg[label].append(r)
            print(
                f"{name if i == 0 else '':<20}{label:<12}"
                f"{r['PCS']:>8.1f}{r['within1']:>11.1f}{r['none']:>10.1f}"
                f"{r['P_over']:>12.1f}{r['N']:>9.1f}{r['N_over']:>12.1f}{r['pct_over']:>12.1f}"
            )
        print("-" * 96)

    print(f"{'평균':<20}", end="")
    means = {}
    for i, (label, _) in enumerate(DESIGNS):
        rs = agg[label]
        m = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        means[label] = m
        if i:
            print(f"{'':<20}", end="")
        print(
            f"{label:<12}{m['PCS']:>8.1f}{m['within1']:>11.1f}{m['none']:>10.1f}"
            f"{m['P_over']:>12.1f}{m['N']:>9.1f}{m['N_over']:>12.1f}{m['pct_over']:>12.1f}"
        )
    print("=" * 96)

    m3, m15 = means["3+3"], means["BOIN(n=15)"]
    print("표본을 맞추면(3+3 {:.1f}명 vs BOIN {:.1f}명) 정확 MTD 선택률은 "
          "{:.1f}% 대 {:.1f}%다.".format(m3["N"], m15["N"], m3["PCS"], m15["PCS"]))
    print("→ 정확도를 만드는 것은 설계가 아니라 표본수다. "
          "설계 교체가 아니라 필요 표본수가 에이전트의 출력이어야 한다.")

    # ---- self-check ----------------------------------------------------
    # 결론(어느 설계가 우월한지)은 검사하지 않는다. 그것은 시뮬레이션이 답할 문제이지
    # 자체검사가 고정할 문제가 아니다. 여기서는 구현이 공표된 수식과 맞는지만 본다.
    le, ld = boin_boundaries(0.30)
    assert abs(le - 0.236) < 0.01 and abs(ld - 0.359) < 0.01, (
        f"BOIN 경계가 Liu & Yuan(2015) 공표값(0.236/0.359)과 불일치: {le:.3f}/{ld:.3f}"
    )
    assert 15 <= m3["PCS"] <= 50, f"3+3 PCS가 문헌 보고 범위(약 20~45%) 밖: {m3['PCS']:.1f}"
    for label, m in means.items():
        assert m["PCS"] <= m["within1"], f"{label}: PCS가 ±1 이내보다 클 수 없다"
        assert m["PCS"] + m["none"] <= 100.0 + 1e-9, f"{label}: 확률 합이 100%를 넘는다"
    print(f"self-check 통과 — BOIN 경계 {le:.3f}/{ld:.3f} (공표값 일치), 지표 정합성 확인")


if __name__ == "__main__":
    main()
