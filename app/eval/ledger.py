"""
토큰 원장 — 리소스(크레딧) 활용 효율성 증빙 산출물(토큰 0, 감사로그·평가 결과만 읽는다).

- 서빙 원장: 설정별 케이스당 노드 토큰(입력·출력·reasoning·캐시), 호출 수. 원천 = app/eval/data/audit_usage.jsonl의 usage.total_tokens
  (게이트웨이 쿼터는 total_tokens 1:1 차감, 캐시 적중도 전액 차감 — docs/gateway_probe.md ⑩-b. 캐시 절감을 주장하지 않는다)
- 성과 정규화: 케이스당 토큰 / 검증 통과 finding 수, grounded 적중 1건당 토큰 (app/eval/data/results/<config>.json)
- Pareto 그림: 케이스당 토큰 vs grounded_recall (점추정 — n=20 CI 겹침은 표에 함께 적는다)

실행: py -m app.eval.ledger --configs lean,full,no_arena,no_calc,no_verifier   (matplotlib이 있는 Python 3.14 — .venv에는 없다)
출력: docs/token_ledger.md, figures/pareto_tokens_grounded.png
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "app" / "eval" / "data" / "results"
NODES = ("compile", "plan", "arena", "findings", "rewrite")


def _node(purpose: str) -> str:
    return purpose.rsplit(":", 1)[-1].split("_", 1)[0]


def audit_by_config(configs: list[str]) -> dict[str, dict]:
    """eval-<config>-AX1-xxx:<node> 호출을 모은다. 같은 run_id가 여러 번 실행됐으면 마지막 실행(마지막 compile 이후)만 센다."""
    calls: dict[str, list[dict]] = defaultdict(list)
    from app.eval.audit_export import iter_audit
    for r in iter_audit():
        if not (r.get("purpose") or "").startswith("eval-"):
            continue
        run_id = r["purpose"].split(":", 1)[0]
        calls[run_id].append(r)
    out: dict[str, dict] = {}
    for cfg in configs:
        prefix = f"eval-{cfg}-AX"   # AX1(원·확장)·AXD(다약물)
        per_node = defaultdict(lambda: defaultdict(int))
        n_runs = 0
        for run_id, rs in calls.items():
            if not run_id.startswith(prefix):
                continue
            rs = sorted(rs, key=lambda r: r["ts"])
            starts = [i for i, r in enumerate(rs) if r["purpose"].endswith(":compile")]
            rs = rs[starts[-1]:] if starts else rs
            n_runs += 1
            for r in rs:
                u = r.get("usage") or {}
                d = per_node[_node(r["purpose"])]
                d["calls"] += 1
                for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens", "total_tokens"):
                    d[k] += int(u.get(k) or 0)
        out[cfg] = {"n_runs": n_runs, "per_node": {k: dict(v) for k, v in per_node.items()}}
    return out


def outcomes(cfg: str) -> dict | None:
    p = RES / f"{cfg}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["rows"]
    n = len(rows)
    verified = sum((r.get("verified_rate") or 0) * r.get("n_findings", 0) for r in rows)
    grounded = sum(r.get("n_grounded", 0) for r in rows)
    tok = sum(r["tokens"] for r in rows)
    return {"n": n, "tokens_per_case": tok / n, "grounded_recall": d["aggregate"]["grounded_recall"], "recall": d["aggregate"]["recall"],
            "verified_rate": d["aggregate"]["verified_rate"], "tokens_per_verified_finding": tok / max(verified, 1),
            "tokens_per_grounded_hit": tok / max(grounded, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="lean,full,no_arena,no_calc,no_verifier")
    a = ap.parse_args()
    cfgs = [c.strip() for c in a.configs.split(",") if c.strip()]
    led = audit_by_config(cfgs)
    lines = ["# 토큰 원장 (리소스 효율 증빙)", "",
             "원천: 감사로그 공개 집계본 `app/eval/data/audit_usage.jsonl`(`python -m app.eval.audit_export`)의 `usage.total_tokens`(게이트웨이 쿼터와 1:1, 캐시 적중도 전액 차감 — `docs/gateway_probe.md` ⑩-b), "
             "성과: `app/eval/data/results/<config>.json`. 생성: `py -m app.eval.ledger`.", "",
             "## 1. 서빙 원장 — 설정별 케이스당 노드 토큰", "",
             "| 설정 | 감사로그 케이스 | " + " | ".join(NODES) + " | 합계/케이스 | reasoning 비중 |", "|---|---|" + "---|" * (len(NODES) + 2)]
    for cfg in cfgs:
        L = led[cfg]
        n = max(L["n_runs"], 1)
        pn = L["per_node"]
        tot = sum(v.get("total_tokens", 0) for v in pn.values())
        rea = sum(v.get("reasoning_tokens", 0) for v in pn.values())
        cells = [f"{pn.get(k, {}).get('total_tokens', 0) / n:,.0f}" for k in NODES]
        lines.append(f"| {cfg} | {L['n_runs']} | " + " | ".join(cells) + f" | {tot / n:,.0f} | {rea / max(tot, 1):.1%} |")
    lines += ["", "## 2. 성과 정규화 — 같은 토큰으로 무엇을 얻었나", "",
              "| 설정 | n | 토큰/케이스 | span recall | grounded recall | 검증 통과율 | 토큰/검증 finding | 토큰/grounded 적중 |", "|---|---|---|---|---|---|---|---|"]
    pts = []
    for cfg in cfgs:
        o = outcomes(cfg)
        if not o:
            continue
        pts.append((cfg, o["tokens_per_case"], o["grounded_recall"]))
        lines.append(f"| {cfg} | {o['n']} | {o['tokens_per_case']:,.0f} | {o['recall']:.3f} | {o['grounded_recall']:.3f} | {o['verified_rate']:.3f} | "
                     f"{o['tokens_per_verified_finding']:,.0f} | {o['tokens_per_grounded_hit']:,.0f} |")
    lines += ["", "주의: n=20 설정 간 grounded 차이는 대부분 부트스트랩 CI가 겹친다 — 유의 여부는 `python -m app.eval.compare`의 쌍대 비교로만 주장한다. 토큰 차이는 호출 구조로 정해지므로 확정적이다.", "`*ext`는 확장 40케이스(AX1-021~060), `*mdrug`는 다약물 30케이스(AXD-)로 원 20케이스와 분포가 달라 설정 간 비교는 같은 세트 안에서만 한다.",
              "프롬프트 캐시는 적중해도 팀 쿼터 차감이 줄지 않아(⑩-b) 절감 수단으로 계산하지 않았다. Batch·Flex는 게이트웨이 지원을 확인하지 않았다."]
    (ROOT / "docs" / "token_ledger.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if pts:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from app.ui import tokens as T   # 색은 docs/DESIGN.md 토큰 — 원 세트만 강조색, 다른 세트는 회색
        plt.rcParams.update({"font.family": ["Malgun Gothic", "DejaVu Sans"], "axes.edgecolor": T.MUTED, "axes.labelcolor": T.INK,
                             "xtick.color": T.MUTED, "ytick.color": T.MUTED, "text.color": T.INK})
        fig, ax = plt.subplots(figsize=(7, 4.6))
        # 겹치는 점 라벨만 개별 오프셋(포인트) — 나머지는 오른쪽 위
        offset = {"lean_v3b": (6, 5), "lean_combo": (6, -13), "lean_v3": (-46, 4), "lean_mdrug3": (8, -14)}
        for name, x, y in pts:
            # 세트마다 모양을 달리한다 — 원(원 20) · 속 빈 사각형(확장 40) · 속 빈 세모(다약물 30). 세트 간 직접 비교하지 않는다
            kind = "ext" if name.endswith("ext") else ("mdrug" if "mdrug" in name else "orig")
            marker, edge = {"orig": ("o", None), "ext": ("s", T.MUTED), "mdrug": ("^", T.MUTED)}[kind]
            ax.scatter(x / 1000, y, s=52, marker=marker, facecolors="none" if edge else T.ACCENT, edgecolors=edge or T.ACCENT, linewidths=1.1)
            ax.annotate(name, (x / 1000, y), textcoords="offset points", xytext=offset.get(name, (6, -13 if edge else 4)), fontsize=10.5, color=T.MUTED if edge else T.INK)
        ax.set_xlabel("tokens per case (thousand, gateway quota)")
        ax.set_ylabel("grounded recall (point estimate)")
        ax.set_title("Cost vs grounded citation (o n=20, □ *ext n=40, △ *mdrug n=30)", loc="left", fontsize=12, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color=T.LINE, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=10.5)
        ax.xaxis.label.set_size(11); ax.yaxis.label.set_size(11)
        fig.tight_layout()
        fig.savefig(ROOT / "figures" / "pareto_tokens_grounded.png", dpi=160)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
