"""
Trial Schema — Protocol Compiler의 출력이자 모든 에이전트 노드가 읽고 쓰는 단일 상태 객체.

deep-research-report.md 「핵심 데이터 스키마 샘플」과 제안서 2장(상태·과제 DAG·재계획)을 Pydantic으로 고정한다.
LLM이 채우는 필드는 전부 Optional — 결측은 "근거 미확보"로 남고, Orchestrator는 결측 패턴에서 과제를 만든다.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ----------------------------------------------------------------- 기본 열거형
class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Applicability(str, Enum):
    KR = "KR"
    US = "US"
    common = "common"
    conditional = "conditional"


class NormStrength(str, Enum):
    """규범 강도 — 인용 검증기가 술어('의무화' 등)와 대조한다."""
    binding = "binding"              # 법령·고시
    final_guidance = "final_guidance"  # FDA 최종 가이던스, ICH Step 4
    draft_guidance = "draft_guidance"
    civil_guide = "civil_guide"      # 식약처 민원인 안내서 (법적 구속력 없음)
    reference = "reference"          # CTTI 등


class HumanStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    partially_approved = "partially_approved"
    rejected = "rejected"
    on_hold = "on_hold"


# ----------------------------------------------------------------- 프로토콜 구조
class InvestigationalProduct(BaseModel):
    name: Optional[str] = None
    modality: Optional[str] = None
    target: Optional[str] = None
    smiles: Optional[str] = Field(None, description="구조가 공개된 경우만. 없으면 RDKit·ChEMBL 호출 생략")
    chembl_id: Optional[str] = None
    drug_class_hint: Optional[str] = Field(None, description="프로토콜이 언급한 계열(예: KRAS G12C inhibitor)")


class Study(BaseModel):
    study_id: Optional[str] = None
    title: Optional[str] = None
    indication: Optional[str] = None
    phase: Optional[str] = None
    countries: list[str] = Field(default_factory=list, description="대상 규제 관할. 예: ['KR','US']")
    investigational_product: InvestigationalProduct = Field(default_factory=InvestigationalProduct)


class DoseLevel(BaseModel):
    label: str
    dose: Optional[str] = None
    n_planned: Optional[int] = None
    exposure_auc: Optional[float] = Field(None, description="용량군별 노출값이 표에 있으면 기록(단위 exposure_unit)")
    exposure_cmax: Optional[float] = None
    exposure_unit: Optional[str] = None
    dlt_observed: Optional[int] = None
    n_evaluable: Optional[int] = None


class ExpansionCohort(BaseModel):
    cohort_id: str
    dose: Optional[str] = None
    objective: Optional[str] = None
    n_planned: Optional[int] = None


class DoseStrategy(BaseModel):
    starting_dose: Optional[str] = None
    dose_levels: list[DoseLevel] = Field(default_factory=list)
    escalation_method: Optional[str] = Field(None, description="예: '3+3', 'BOIN', 'mTPI-2', 'CRM'")
    target_dlt_rate: Optional[float] = None
    rp2d_rule_text: Optional[str] = Field(None, description="RP2D 선정 규칙 원문 (예: 'The MTD will be selected as the RP2D.')")
    dose_comparison_plan: Optional[str] = Field(None, description="용량 비교(무작위) 계획 원문. 없으면 None")
    expansion_cohorts: list[ExpansionCohort] = Field(default_factory=list)
    pk_sampling_plan: Optional[str] = None


class Eligibility(BaseModel):
    key_inclusion: list[str] = Field(default_factory=list)
    key_exclusion: list[str] = Field(default_factory=list)
    prior_therapy_washout: Optional[str] = Field(None, description="선행 치료 washout 규정 원문(예: anti-PD-(L)1)")


class Endpoint(BaseModel):
    name: str
    kind: Literal["primary", "secondary", "exploratory"]
    definition: Optional[str] = None
    analysis_population: Optional[str] = None


class VisitProcedure(BaseModel):
    visit: str
    day: Optional[str] = None
    procedures: list[str] = Field(default_factory=list)
    blood_volume_ml: Optional[float] = None


class SafetyMonitoring(BaseModel):
    lab_schedule_text: Optional[str] = Field(None, description="간기능 등 검사 주기 원문")
    dose_modification_text: Optional[str] = None


class Design(BaseModel):
    objectives_primary: list[str] = Field(default_factory=list)
    objectives_secondary: list[str] = Field(default_factory=list)
    dose_strategy: DoseStrategy = Field(default_factory=DoseStrategy)
    eligibility: Eligibility = Field(default_factory=Eligibility)
    endpoints: list[Endpoint] = Field(default_factory=list)
    visits_and_procedures: list[VisitProcedure] = Field(default_factory=list)
    safety_monitoring: SafetyMonitoring = Field(default_factory=SafetyMonitoring)


class ProtocolSpan(BaseModel):
    section: Optional[str] = None
    text: str = Field(..., description="프로토콜 원문 발췌(수정 없이)")


class TrialSchema(BaseModel):
    """Protocol Compiler 출력. `source_spans`는 필드 → 원문 위치 매핑(추적성)."""
    study: Study = Field(default_factory=Study)
    design: Design = Field(default_factory=Design)
    source_spans: dict[str, ProtocolSpan] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list, description="Compiler가 찾지 못한 필드 경로")


# ----------------------------------------------------------------- 근거·판정
class Evidence(BaseModel):
    evidence_id: str
    kind: Literal["regulatory_clause", "label_statement", "calculation", "database_record", "analog_trial", "literature"]
    authority: Optional[str] = None       # FDA / MFDS / ICH / openFDA / ChEMBL / ClinicalTrials.gov / 계산
    document_title: Optional[str] = None
    version_date: Optional[str] = None
    section: Optional[str] = None
    quote: Optional[str] = Field(None, description="원문 발췌 또는 계산 결과 요약")
    applicability: Optional[Applicability] = None
    norm_strength: Optional[NormStrength] = None
    url: Optional[str] = None
    retrieved_at: Optional[str] = None
    tool_call_id: Optional[str] = Field(None, description="감사로그의 도구 호출 ID")
    # 근거 우선순위: 직접 측정(라벨 보고값) > 문서 규범 > 파생 추정 지표
    priority_tier: Literal[1, 2, 3] = 2


class ReviewerPosition(BaseModel):
    reviewer: Literal["regulatory", "site", "patient"]
    severity: Severity
    position: str
    evidence_ids_seen: list[str] = Field(default_factory=list, description="이 Reviewer에게만 공급된 근거")


class Finding(BaseModel):
    finding_id: str
    category: Literal["dose_optimization", "safety_monitoring", "eligibility", "endpoint_ctq", "burden", "source_version", "feasibility"]
    severity: Severity
    protocol_span: ProtocolSpan
    claim: str
    protocol_fact: Optional[str] = Field(None, description="프로토콜이 무엇을 적었거나 빠뜨렸는가 — 원문 span과 대조")
    evidence_fact: Optional[str] = Field(None, description="인용 근거가 무엇을 말하는가 — 근거 quote와 NLI 대조")
    span_verified: Optional[bool] = Field(None, description="protocol_span.text가 프로토콜 원문에 실제로 존재하는가(결정론)")
    evidence_ids: list[str] = Field(default_factory=list)
    related_evidence_ids: list[str] = Field(default_factory=list, description="자동 검색(로컬 NLI)이 같은 규범으로 제안한 다른 문서의 조항 — 인용이 아니라 사람 검토용 후보")
    reviewer_positions: list[ReviewerPosition] = Field(default_factory=list)
    conflict_unresolved: bool = Field(False, description="Reviewer 간 상충이 남아 있으면 True — 합의를 강제하지 않는다")
    suggested_patch: Optional[str] = None
    required_additional_data: list[str] = Field(default_factory=list)
    verdict: Literal["defect", "abstain", "no_issue"] = "defect"
    abstain_reason: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    verifier_status: Literal["pending", "verified", "rejected", "held"] = "pending"
    verifier_note: Optional[str] = None
    human_status: HumanStatus = HumanStatus.pending


# ----------------------------------------------------------------- 오케스트레이션 상태
class ToolCall(BaseModel):
    tool_call_id: str
    tool: str
    args: dict[str, Any]
    ok: bool
    result_summary: Optional[str] = None
    error: Optional[str] = None
    started_at: str
    latency_s: Optional[float] = None


class Task(BaseModel):
    """Orchestrator가 결측·상충 패턴에서 생성하는 검토 과제(DAG 노드)."""
    task_id: str
    kind: str                          # 예: exposure_dose_relationship / structural_class_label_check / design_oc / regulatory_clause_search
    depends_on: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    rationale: str
    status: Literal["planned", "running", "done", "failed", "abstained", "skipped"] = "planned"
    replan_count: int = 0


class Budget(BaseModel):
    max_tokens: int = 150_000
    max_tool_calls: int = 60
    max_replans_per_gap: int = 3
    used_tokens: int = 0
    used_tool_calls: int = 0

    def exhausted(self) -> bool:
        return self.used_tokens >= self.max_tokens or self.used_tool_calls >= self.max_tool_calls


class AuditMeta(BaseModel):
    run_id: str
    created_at: str = Field(default_factory=lambda: datetime.now().astimezone().isoformat())
    models: dict[str, str] = Field(default_factory=dict)
    prompt_hashes: list[str] = Field(default_factory=list)
    corpus_manifest_id: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


class ReviewState(BaseModel):
    """LangGraph 상태 객체 — 모든 노드가 이 객체만 읽고 쓴다."""
    run_id: str
    raw_protocol_text: str = ""
    trial: TrialSchema = Field(default_factory=TrialSchema)
    tasks: list[Task] = Field(default_factory=list)
    evidence: dict[str, Evidence] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)
    tool_log: list[ToolCall] = Field(default_factory=list)
    replan_events: list[dict[str, Any]] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    audit: Optional[AuditMeta] = None
    scratch: dict[str, Any] = Field(default_factory=dict, description="노드 간 전달용 중간 결과(라벨 PK, 구조 프로파일 등). 감사로그에는 evidence로만 남긴다")
    review_questions: list[dict[str, Any]] = Field(default_factory=list)
    unavailable_axes: list[str] = Field(default_factory=list, description="도구를 호출하지 않은 축과 이유('근거 미확보')")
    terminal_status: Literal["running", "awaiting_human", "completed", "no_conclusion"] = "running"
