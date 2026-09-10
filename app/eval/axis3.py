"""
평가 축 ③ — 승인 라벨을 정답으로 쓰는 약리 판정 재현 (계산 모듈 전용, LLM 없음).

입력: 라벨 12.3 PK 진술(비선형 PK, 노출-반응 미상, 단백결합, 반감기)만.
정답: FDA가 용량 최적화 PMR/PMC를 실제로 부과했는가(승인서한 원문, app/eval/data/pmr_ground_truth.jsonl).
출력: 위험 순위 → AUROC·PR-AUC·양성 재현율@k. 클래스 불균형(양성 7/29)이 크므로 절대 정확도 대신 순위 지표를 보고한다(제안서 4장).

점수 규칙(잠정, 본 프로젝트가 정한 것): 노출-반응 미상 +2, 비선형/포화 PK 진술 +2, 단백결합 ≥ 97% +0.5, 반감기 ≤ 8h(1일 1회면 트로프 급락) +0.5.
ablation: '계산 모듈 제거' = 라벨 PK 해석 없이 상수 점수 → AUROC 0.5.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def risk_score(label: dict) -> tuple[float, list[str]]:
    s, why = 0.0, []
    if label.get("exposure_response_unknown"):
        s += 2; why.append("E-R unknown")
    if label.get("nonlinear_pk_statement"):
        s += 2; why.append("nonlinear/saturable PK")
    pk = label.get("pk") or {}
    if (pk.get("protein_binding_pct") or 0) >= 97:
        s += 0.5; why.append("PB≥97%")
    if 0 < (pk.get("t_half_hr") or 0) <= 8:
        s += 0.5; why.append("t½≤8h")
    return s, why


def auroc(scores: list[float], y: list[int]) -> float:
    pos = [s for s, t in zip(scores, y) if t]; neg = [s for s, t in zip(scores, y) if not t]
    if not pos or not neg:
        return float("nan")
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def pr_auc(scores: list[float], y: list[int]) -> float:
    order = sorted(range(len(y)), key=lambda i: -scores[i])
    tp = fp = 0; P = sum(y); ap = 0.0; prev_recall = 0.0
    for i in order:
        if y[i]:
            tp += 1
        else:
            fp += 1
        recall = tp / P; precision = tp / (tp + fp)
        if y[i]:
            ap += precision * (recall - prev_recall); prev_recall = recall
    return ap


def main() -> None:
    labels = {r["generic_name"].lower(): r for r in (json.loads(l) for l in (DATA / "oncology_labels.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    truth = [json.loads(l) for l in (DATA / "pmr_ground_truth.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = []
    for t in truth:
        if t.get("exclude") or t["pmr_dose_optimization"] == "unknown":
            continue
        lb = labels.get(t["generic"].lower())
        if not lb:
            continue
        s, why = risk_score(lb)
        rows.append({"generic": t["generic"], "y": 1 if t["pmr_dose_optimization"] else 0, "score": s, "why": why, "approval": t["initial_approval_date"]})
    rows.sort(key=lambda r: (-r["score"], r["generic"]))
    y = [r["y"] for r in rows]; sc = [r["score"] for r in rows]
    n, P = len(rows), sum(y)
    au, ap = auroc(sc, y), pr_auc(sc, y)
    base_ap = P / n
    top = rows[:8]
    lines = [f"# 평가 축③ — 라벨 PK만으로 용량 최적화 PMR 부과 여부 순위 재현 (n={n}, 양성 {P})", "",
             f"AUROC {au:.3f} · PR-AUC {ap:.3f} (무작위 기준선 {base_ap:.3f}) · 상위 8 중 양성 {sum(r['y'] for r in top)}/8 · 계산 모듈 제거(상수 점수) AUROC 0.500", "",
             "| 순위 | 성분 | 승인 | 점수 | 근거 | PMR 정답 |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['generic']} | {r['approval'][:4]} | {r['score']:.1f} | {', '.join(r['why']) or '-'} | {'✅ 부과' if r['y'] else '—'} |")
    lines += ["", "한계: 점수 규칙은 본 프로젝트가 정한 잠정 기준이며 학습하지 않았다(정답을 본 뒤 조정하지 않음). 라벨 PK 정규식 추출 실패 성분은 제외됐고, "
              "gefitinib(2003 원문 미확보)·비종양 적응증(remibrutinib, tofacitinib)은 제외했다. 2010년 이전 승인약은 Project Optimus 이전이라 정답 자체의 시대 편향이 있다."]
    out = DATA / "results" / "AXIS3_REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4]))
    print(f"→ {out}")


if __name__ == "__main__":
    main()
