"""
Open Targets Platform GraphQL 도구 — 타겟 근거·safety liability 조회 (CC0). 공식 rate limit 미공개 → 요청 간 0.3초 대기.
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.tools import ToolResult, run_tool

ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"
UA = {"User-Agent": "DoseVerdict/0.1 (academic competition prototype)", "Content-Type": "application/json"}

_Q_SEARCH = """
query Search($q: String!) { search(queryString: $q, entityNames: ["target"], page: {index: 0, size: 3}) {
  hits { id name entity object { ... on Target { approvedSymbol approvedName } } } } }"""
_Q_TARGET = """
query T($id: String!) { target(ensemblId: $id) {
  id approvedSymbol approvedName biotype
  safetyLiabilities { event eventId effects { direction dosing } datasource literature }
  tractability { modality label value }
  drugAndClinicalCandidates { count rows { id maxClinicalStage drug { id name } diseases { disease { name } } } } } }"""


def _gql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    import urllib.error
    import time
    for attempt in range(3):   # 5xx·연결·타임아웃은 2초·4초 백오프로 재시도, 4xx(스키마 오류)는 즉시 보존
        req = urllib.request.Request(ENDPOINT, data=json.dumps({"query": query, "variables": variables}).encode(), headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:  # GraphQL 스키마 오류는 400 본문에 메시지가 있다 → 관측값으로 보존
            if e.code < 500 or attempt == 2:
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from e
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 * 2 ** attempt)
    if data.get("errors"):
        raise RuntimeError(str(data["errors"])[:300])
    return data["data"]


def target_evidence(symbol: str) -> ToolResult:
    """유전자 심볼(예: KRAS) → Ensembl ID 해석 → safety liabilities·tractability·승인/임상 약물."""
    def _run(symbol: str) -> dict[str, Any]:
        hits = _gql(_Q_SEARCH, {"q": symbol})["search"]["hits"]
        if not hits:
            return {"symbol": symbol, "found": False}
        exact = [h for h in hits if (h["object"] or {}).get("approvedSymbol", "").upper() == symbol.upper()]
        h = (exact or hits)[0]
        time.sleep(0.3)
        t = _gql(_Q_TARGET, {"id": h["id"]})["target"]
        return {
            "symbol": t["approvedSymbol"], "ensembl_id": t["id"], "name": t["approvedName"], "found": True,
            "safety_liabilities": [{"event": s["event"], "effects": s.get("effects"), "source": s.get("datasource")} for s in (t.get("safetyLiabilities") or [])][:20],
            "tractability_sm": [x for x in (t.get("tractability") or []) if x.get("modality") == "SM" and x.get("value")][:6],
            "known_drugs": [{"drug": (r.get("drug") or {}).get("name"), "max_stage": r.get("maxClinicalStage"),
                             "diseases": [((x.get("disease") or {}).get("name")) for x in (r.get("diseases") or [])][:5]}
                            for r in ((t.get("drugAndClinicalCandidates") or {}).get("rows") or [])][:15],
            "known_drugs_count": (t.get("drugAndClinicalCandidates") or {}).get("count"),
        }

    r = run_tool("opentargets.target_evidence", _run, symbol=symbol)
    r.source = {"url": ENDPOINT, "license": "CC0 1.0", "retrieved_at": datetime.now(timezone.utc).isoformat()}
    return r
