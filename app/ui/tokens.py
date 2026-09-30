"""DoseVerdict 색 토큰 — 화면 색의 단일 원천(docs/DESIGN.md).

main.py의 CSS·graph_dot()과 app/eval/ledger.py(파레토 그림)는 여기서 읽는다. 파이썬 밖에서 같은 값을 들고 있는 곳은 셋이다:
.streamlit/config.toml(배지 :green-badge 등), docs/slides/deck.html(:root), docs/report.css. 값을 바꾸면 함께 바꾼다.
"""

INK = "#1b2430"
MUTED = "#5b6472"
PAPER = "#fbfaf7"
PANEL = "#ffffff"
SOFT = "#f2efe8"
LINE = "#dcd6ca"
ACCENT = "#1f3a5f"

# 판정 상태 4색 — 색은 상태를 뜻할 때만 쓴다(장식 금지)
VERIFIED, VERIFIED_BG = "#2f7d4f", "#dcebe2"
HELD, HELD_BG, HELD_TEXT = "#b7791f", "#f6e5c6", "#96610f"
REJECTED, REJECTED_BG = "#b4372f", "#f3d6d3"
ABSTAIN, ABSTAIN_BG = "#5a5f96", "#dfe0ef"

# 중증도는 상태색을 쓰지 않는다(high가 기각 빨강과 겹쳤다) — 무채색 위계, critical만 굵게(main.py CSS)
SEV = {"critical": INK, "high": INK, "medium": MUTED, "low": MUTED}
DEL_BG, INS_BG = "#f8e6e4", "#e8f2ec"

SANS = '"Pretendard Variable", Pretendard, -apple-system, "Segoe UI", "Malgun Gothic", sans-serif'
SERIF = 'Georgia, "Noto Serif KR", serif'


def css_vars() -> str:
    pairs = {"ink": INK, "muted": MUTED, "paper": PAPER, "panel": PANEL, "soft": SOFT, "line": LINE, "accent": ACCENT,
             "verified": VERIFIED, "verified-bg": VERIFIED_BG, "held": HELD, "held-bg": HELD_BG, "held-text": HELD_TEXT,
             "rejected": REJECTED, "rejected-bg": REJECTED_BG, "abstain": ABSTAIN, "abstain-bg": ABSTAIN_BG,
             "del-bg": DEL_BG, "ins-bg": INS_BG, **{f"sev-{k}": v for k, v in SEV.items()}}
    return " ".join(f"--dv-{k}: {v};" for k, v in pairs.items())
