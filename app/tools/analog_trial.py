"""
Analog Trial 도구 — ClinicalTrials.gov API v2. 설계 구조 비교 전용(효능·안전성 정답으로 쓰지 않는다).
"""
from __future__ import annotations

import urllib.parse
from datetime import datetime, timezone
from typing import Any

from app.tools import ToolResult, asof_date, run_tool

BASE = "https://clinicaltrials.gov/api/v2/studies"


def _get(url: str, timeout: int = 40) -> dict[str, Any]:
    import pharmacology_evidence as pe   # 5xx·연결·타임아웃 재시도(2회, 백오프) 공용 구현
    return pe.fetch_json(url, timeout=timeout)


def _design_summary(study: dict[str, Any]) -> dict[str, Any]:
    ps = study.get("protocolSection", {})
    ident = ps.get("identificationModule", {})
    status = ps.get("statusModule", {})
    design = ps.get("designModule", {})
    arms = ps.get("armsInterventionsModule", {})
    elig = ps.get("eligibilityModule", {})
    return {
        "nct_id": ident.get("nctId"),
        "title": ident.get("briefTitle"),
        "overall_status": status.get("overallStatus"),
        "why_stopped": status.get("whyStopped"),
        "phases": design.get("phases"),
        "enrollment": (design.get("enrollmentInfo") or {}).get("count"),
        "enrollment_type": (design.get("enrollmentInfo") or {}).get("type"),
        "allocation": (design.get("designInfo") or {}).get("allocation"),
        "n_arms": len(arms.get("armGroups") or []),
        "arm_labels": [a.get("label") for a in (arms.get("armGroups") or [])][:8],
        "interventions": [i.get("name") for i in (arms.get("interventions") or [])][:8],
        "eligibility_excerpt": (elig.get("eligibilityCriteria") or "")[:600],
        "start_date": (status.get("startDateStruct") or {}).get("date"),
        "first_posted": (status.get("studyFirstPostDateStruct") or {}).get("date"),
    }


def search_analog_trials(query_term: str, phases: str = "PHASE1,PHASE2", page_size: int = 20) -> ToolResult:
    def _run(query_term: str, phases: str, page_size: int) -> dict[str, Any]:
        adv = f"AREA[Phase]({' OR '.join(phases.split(','))})"
        if asof_date():   # 후향 검증: 승인 시점 이후 시작된 시험(예: 승인 후 용량 비교 시험)은 보지 않는다
            adv += f" AND AREA[StartDate]RANGE[MIN, {asof_date()}]"
        q = urllib.parse.urlencode({
            "query.term": query_term,
            "filter.advanced": adv,
            "pageSize": page_size,
            "fields": "NCTId,BriefTitle,OverallStatus,WhyStopped,Phase,EnrollmentCount,EnrollmentType,DesignAllocation,ArmGroupLabel,InterventionName,EligibilityCriteria,StartDate,StudyFirstPostDate",
            "countTotal": "true",
        })
        data = _get(f"{BASE}?{q}")
        studies = [_design_summary(s) for s in data.get("studies", [])]
        if asof_date():   # 서버 필터 이중 확인 — 시작일 없는 등록도 제외
            studies = [s for s in studies if s.get("start_date") and s["start_date"] <= asof_date()]
        return {"query": query_term, "total_count": data.get("totalCount"), "n_returned": len(studies), "studies": studies,
                "usage_note": "설계 구조 비교 전용. 효능·안전성·규제 정답으로 사용 금지."}

    r = run_tool("ctgov.search_analog_trials", _run, query_term=query_term, phases=phases, page_size=page_size)
    r.source = {"url": BASE, "license": "public", "retrieved_at": datetime.now(timezone.utc).isoformat()}
    return r


def get_study(nct_id: str) -> ToolResult:
    def _run(nct_id: str) -> dict[str, Any]:
        return _design_summary(_get(f"{BASE}/{nct_id}"))

    r = run_tool("ctgov.get_study", _run, nct_id=nct_id)
    r.source = {"url": f"{BASE}/{nct_id}", "retrieved_at": datetime.now(timezone.utc).isoformat()}
    return r
