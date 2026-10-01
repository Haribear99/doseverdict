"""영상 카드 HTML 생성 — cards/*.html (렌더는 render_cards.py).

숫자·원문은 docs/numbers.md, 덱 1·5장, LUMAKRAS 라벨 12.3(openFDA 조회 결과)에 있는 값만 쓴다.
색은 app/ui/tokens.py와 같은 값(cards/base.css). 상태색은 기권(보라)에만 쓴다.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent / "cards"
HEAD = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"><style>{css}</style></head><body>{body}</body></html>'
QUOTE_PRE = "Sotorasib exhibited non-linear, time-dependent, pharmacokinetics over the dose range of "
cards = {}

cards["h1"] = ("""
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center}
.n{font-size:330px;font-weight:800;letter-spacing:-.04em;line-height:1}
.n small{font-size:150px;font-weight:700;margin-left:18px;letter-spacing:-.02em}
.cap{margin-top:34px;font-size:44px;font-weight:700}
.sub{margin-top:14px;font-size:30px;color:var(--muted)}
.k{position:absolute;left:120px;top:96px}""", """
<div class="k kicker">DoseVerdict · 시연</div>
<div class="wrap"><div class="n">960<small>mg</small></div>
<div class="cap">소토라십(LUMAKRAS) 승인 용량</div>
<div class="sub">KRAS G12C 변이 비소세포폐암 · 1일 1회</div></div>""")


def h2(underline: bool):
    u = "u on" if underline else "u"
    return ("""
.top{position:absolute;left:120px;top:96px;font-size:44px;font-weight:700}
.top span{font-size:26px;color:var(--muted);font-weight:500;margin-left:14px}
.n{position:absolute;left:120px;top:200px;font-size:250px;font-weight:800;letter-spacing:-.04em;line-height:1}
.n small{font-size:110px;font-weight:700;margin-left:14px}
.q{position:absolute;left:120px;right:200px;top:520px;font-family:Georgia,'Noto Serif KR',serif;font-size:40px;line-height:1.6}
.u{padding-bottom:3px}
.u.on{border-bottom:5px solid var(--accent);font-weight:700}
.src{bottom:120px}""", f"""
<div class="top">960 mg<span>승인 용량</span></div>
<div class="n">180~960<small>mg</small></div>
<div class="q">“{QUOTE_PRE}<span class="{u}">180 mg to 960 mg</span> (0.19 to 1 time the approved recommended dosage) once daily with <span class="{u}">similar systemic exposure</span> (i.e., AUC 0-24h and C max) across doses at steady state.”</div>
<div class="src">LUMAKRAS 미국 라벨 12.3 원문 · effective 2025-01-22 · openFDA 조회 · 밑줄은 인용자</div>""")


cards["h2a"] = h2(False)
cards["h2b"] = h2(True)

cards["h3"] = ("""
.l{position:absolute;left:120px;top:0;bottom:0;width:680px;display:flex;flex-direction:column;justify-content:center;gap:48px}
.r{position:absolute;left:880px;top:0;bottom:0;right:120px;display:flex;align-items:center;border-left:2px solid var(--line);padding-left:90px}
.row .v{font-size:110px;font-weight:800;letter-spacing:-.03em;line-height:1}
.row .v small{font-size:54px;margin-left:8px}
.row .t{font-size:30px;color:var(--muted);margin-top:12px}
.big{font-size:220px;font-weight:800;letter-spacing:-.04em;line-height:1.05}""", """
<div class="l"><div class="row"><div class="v">960<small>mg</small></div><div class="t">승인 용량</div></div>
<div class="row"><div class="v">180~960<small>mg</small></div><div class="t">라벨: 정상상태 노출이 비슷한 범위</div></div></div>
<div class="r"><div class="big">왜<br>960?</div></div>""")

cards["h4"] = ("""
.l{position:absolute;left:120px;top:250px}
.l .v{font-size:240px;font-weight:800;letter-spacing:-.04em;line-height:1}
.l .v small{font-size:100px;margin-left:10px}
.l .t{font-size:36px;margin-top:18px;font-weight:700}
.l .t2{font-size:28px;color:var(--muted);margin-top:8px}
.tl{position:absolute;left:900px;right:120px;top:270px}
.m{position:relative;padding:0 0 70px 54px;border-left:3px solid var(--line)}
.m:last-child{padding-bottom:0}
.m:before{content:"";position:absolute;left:-13px;top:6px;width:20px;height:20px;border-radius:50%;background:var(--paper);border:3px solid var(--muted)}
.m.key:before{background:var(--accent);border-color:var(--accent)}
.d{font-size:28px;color:var(--muted);font-weight:600}
.x{font-size:38px;font-weight:700;margin-top:6px;line-height:1.35}
.after{position:absolute;left:900px;right:120px;top:800px;font-size:34px;font-weight:700;color:var(--accent);border-top:3px solid var(--accent);padding-top:20px}""", """
<div class="l"><div class="v">209<small>명</small></div><div class="t">960 대 240 mg 무작위 비교에 배정</div><div class="t2">FDA 시판 후 요구사항</div></div>
<div class="tl">
<div class="m"><div class="d">2021-05</div><div class="x">가속승인 · 960 mg<br>시판 후 요구: 960 대 240 mg 비교</div></div>
<div class="m key"><div class="d">2023-12</div><div class="x">이행 확인 · 960 mg 라벨 용량 유지</div></div>
</div>
<div class="after">용량에 대한 답은 승인 뒤에 나왔다</div>""")

cards["a1"] = ("""
.k{position:absolute;left:120px;top:96px}
.f{position:absolute;left:120px;right:120px;top:270px}
.f .s{font-size:30px;color:var(--muted);font-weight:600}
.f .x{font-size:84px;font-weight:800;letter-spacing:-.03em;margin-top:14px}
.qq{position:absolute;left:120px;right:120px;top:580px;border-top:3px solid var(--ink);padding-top:34px}
.qq .s{font-size:30px;color:var(--muted);font-weight:600}
.qq .x{font-size:60px;font-weight:800;line-height:1.3;margin-top:14px;letter-spacing:-.02em}
.qq .x b{color:var(--accent)}""", """
<div class="k kicker">소토라십 1상</div>
<div class="f"><div class="s">1상 공개 초록</div><div class="x">용량제한독성(DLT) 관찰 안 됨</div></div>
<div class="qq"><div class="s">그래도 남는 질문</div><div class="x">무작위 용량 비교 없이, 그 용량을<br><b>2상 권장 용량(RP2D)</b>으로 넘긴 근거는?</div></div>""")

cards["c1"] = ("""
.k{position:absolute;left:120px;top:96px}
h1{position:absolute;left:120px;top:150px;font-size:56px;font-weight:800;letter-spacing:-.02em}
.call{position:absolute;left:120px;top:320px;right:120px;font-size:38px;line-height:1.5;border-left:6px solid var(--accent);padding-left:28px}
.call b{color:var(--accent)}
.row{position:absolute;left:120px;right:120px;top:560px;display:flex;gap:26px;align-items:stretch}
.b{flex:1;border:2px solid var(--line);padding:36px 22px;font-size:32px;font-weight:600;text-align:center;color:var(--muted);background:var(--panel);display:flex;align-items:center;justify-content:center;line-height:1.3}
.b.on{border:5px solid var(--accent);color:var(--ink);font-weight:800}
.foot{position:absolute;left:120px;right:120px;bottom:130px;font-size:25px;color:var(--muted)}""", """
<div class="k kicker">개입 시점</div>
<h1>판정이 아니라, RP2D 전에 자료를 요청한다</h1>
<div class="call">DoseVerdict가 묻는 시점: <b>RP2D 확정 · 프로토콜 개정</b><br>내는 것: 960·240 판정이 아니라 <b>용량군별 반복투여 PK 요청</b></div>
<div class="row"><div class="b">1상 증량</div><div class="b on">RP2D 확정<br>프로토콜 개정</div><div class="b">확장 코호트</div><div class="b">승인</div><div class="b">시판 후 비교</div></div>
<div class="foot">질문 시점을 보여 주는 일반 흐름이다. 실제 소토라십 개발에 도구를 적용했거나 960/240 결론을 냈다는 뜻이 아니다.</div>""")

cards["d5"] = ("""
.k{position:absolute;left:120px;top:96px}
h1{position:absolute;left:120px;top:150px;font-size:66px;font-weight:800}
ol{position:absolute;left:120px;right:160px;top:340px;list-style:none;counter-reset:i}
li{counter-increment:i;font-size:44px;font-weight:700;line-height:1.4;padding:32px 0 32px 110px;position:relative;border-top:2px solid var(--line)}
li:before{content:counter(i);position:absolute;left:0;top:24px;font-size:72px;font-weight:800;color:var(--accent)}
li span{display:block;font-size:30px;color:var(--muted);font-weight:500;margin-top:10px}""", """
<div class="k kicker">먼저 밝혀 둘 것</div><h1>먼저 밝혀 둡니다</h1>
<ol><li>DoseVerdict는 960과 240 중 무엇이 맞는지 판정하지 않습니다<span>근거가 모자라면 결론 대신 자료를 요청합니다</span></li>
<li>실제 승인 전 1상 초록 43건 후향 검증: 신호 확인 안 됨(null)<span>끝에서 그대로 보여 드립니다</span></li></ol>""")


def chapter(num, title, sub):
    return ("""
.n{position:absolute;left:120px;top:330px;font-family:Georgia,'Noto Serif KR',serif;font-size:300px;line-height:1;color:var(--accent)}
.t{position:absolute;left:560px;top:370px;border-left:2px solid var(--line);padding-left:60px}
.t h1{font-size:96px;font-weight:800;letter-spacing:-.03em;line-height:1.15}
.t p{font-size:36px;color:var(--muted);margin-top:24px}""",
            f"""<div class="n">{num}</div><div class="t"><h1>{title}</h1><p>{sub}</p></div>""")


cards["ch1"] = chapter("01", "작동", "합성 예시 프로토콜 · 실제 개발사 프로토콜 아님")
cards["ch2"] = chapter("02", "안 된 것", "사전 등록 판정 null · 기각된 시도까지 전부")

cards["c2"] = ("""
.box{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:1320px;border:3px solid var(--ink);padding:70px 80px;background:var(--panel)}
.box .k{margin-bottom:26px}
.box h1{font-size:64px;font-weight:800;letter-spacing:-.02em}
.box p{font-size:36px;line-height:1.6;margin-top:26px;color:var(--muted)}
.box b{color:var(--ink)}""", """
<div class="box"><div class="kicker k">지금부터 보는 입력</div><h1>합성 예시 프로토콜 DV-DEMO-001</h1>
<p>팀이 작성한 가상 시놉시스 · 소토라십 공개 라벨 값을 입력으로 사용<br><b>실제 소토라십 프로토콜이 아닙니다</b></p></div>""")

cards["t1"] = ("""
.band{position:absolute;left:0;right:0;top:0;background:var(--ink);color:#fff;font-size:27px;font-weight:600;padding:22px 120px}
h1{position:absolute;left:120px;top:130px;font-size:54px;font-weight:800;letter-spacing:-.02em}
h1 span{font-size:30px;color:var(--muted);font-weight:500;margin-left:16px}
table{position:absolute;left:120px;top:250px;border-collapse:collapse;width:1680px}
th{font-size:28px;color:var(--muted);font-weight:600;text-align:right;padding:16px 24px;border-bottom:2px solid var(--ink)}
th:first-child,td:first-child{text-align:left}
td{font-size:56px;font-weight:700;text-align:right;padding:24px 24px;border-bottom:1px solid var(--line)}
td:first-child{font-size:34px;font-weight:700}
td small{display:block;font-size:22px;color:var(--muted);font-weight:500}
td.j{font-size:32px;font-weight:600}
.hl{background:#efe9dc}
.sum{position:absolute;left:120px;right:120px;top:650px;font-size:40px;font-weight:700;padding:26px 30px;background:var(--abstain-bg);border-left:8px solid var(--abstain);color:#3d4170}
.foot{position:absolute;left:120px;right:120px;top:800px;font-size:24px;line-height:1.6;color:var(--muted)}""", """
<div class="band">예시 프로토콜과 별개 · 실제 소토라십 240 mg · 라벨 PK · 별도 근거 계산(evidence/tcr_240mg.json) · 앱 실행 결과 아님</div>
<h1>240 mg이면 표적을 덮는가<span>TCR = 유리 농도 / IC50</span></h1>
<table><tr><th>PK 가정</th><th>C_max</th><th>C_avg</th><th>C_trough</th><th>지표별 판정</th></tr>
<tr><td>(가) 선형 CL/F</td><td>8.6</td><td>2.5</td><td class="hl">0.31</td><td class="j">지표에 따라 갈림</td></tr>
<tr><td>(나) 노출 유사<small>라벨 12.3</small></td><td>34.5</td><td>10.0</td><td>1.24</td><td class="j">셋 다 덮음</td></tr></table>
<div class="sum">종합: 기권 — 가정과 지표에 따라 답이 갈린다. 용량군별 반복투여 PK를 요청한다.</div>
<div class="foot">IC50 30 nM(ChEMBL 세포 기반 중앙값) · (나) C_avg 정확값 9.99(포화 의심 기준 &gt;10 미해당) · TCR &lt;1 미커버, &gt;10 포화 의심은 본 프로젝트 잠정 기준(문헌값 아님) · 공유결합 저해제라 C_trough 판정은 스크리닝 근사</div>""")

cards["r1"] = ("""
.k{position:absolute;left:120px;top:96px}
h1{position:absolute;left:120px;top:150px;font-size:58px;font-weight:800;letter-spacing:-.02em}
.cols{position:absolute;left:120px;right:120px;top:330px;display:flex;gap:60px}
.c{flex:1;border-top:4px solid var(--ink);padding-top:30px}
.c .s{font-size:28px;color:var(--muted);font-weight:600}
.c .x{font-size:44px;font-weight:700;line-height:1.4;margin-top:14px}
.c .y{font-size:28px;color:var(--muted);margin-top:14px;line-height:1.5}
.end{position:absolute;left:120px;right:120px;top:760px;font-size:42px;font-weight:700;color:var(--accent);border-left:6px solid var(--accent);padding-left:26px}""", """
<div class="k kicker">승인 뒤</div><h1>시판 후 비교 뒤에도 닫히지 않은 질문</h1>
<div class="cols"><div class="c"><div class="s">209명 무작위 비교 · Hochmair 2024</div><div class="x">240 mg의 반응률(ORR)이<br>수치상 낮았다</div><div class="y">이 출처에서는 ORR 값만 인용한다</div></div>
<div class="c"><div class="s">표준 대 감량 용량 메타분석 · Aung 2026, JCO OP</div><div class="x">표준 용량의 ORR·PFS 개선은<br>유의하지 않았다</div><div class="y">유의성 판정은 이 메타분석에만 귀속한다</div></div></div>
<div class="end">DoseVerdict는 결과가 아니라 근거 사슬의 빈칸을 짚는다</div>""")

cards["d8"] = ("""
.k{position:absolute;left:120px;top:96px}
.kp{position:absolute;left:120px;right:120px;top:170px;display:flex;gap:80px}
.kp div.c{flex:1;border-top:4px solid var(--ink);padding-top:24px}
.kp .v{font-size:150px;font-weight:800;letter-spacing:-.03em;line-height:1}
.kp .t{font-size:34px;font-weight:700;margin-top:16px}
.kp .s{font-size:28px;color:var(--muted);margin-top:8px}
ul{position:absolute;left:120px;right:120px;top:520px;list-style:none}
li{font-size:34px;padding:16px 0;border-bottom:1px solid var(--line)}
.end{position:absolute;left:120px;right:120px;top:785px;font-size:30px;font-weight:600;background:var(--soft);padding:22px 28px;line-height:1.5}""", """
<div class="k kicker">비용</div>
<div class="kp"><div class="c"><div class="v">4.0만</div><div class="t">검토 1회당 토큰</div><div class="s">39,759 · 39,643</div></div>
<div class="c"><div class="v">약 8배</div><div class="t">같은 모델 원샷 대비</div><div class="s">39,701 대 5,023</div></div></div>
<ul><li>토큰의 70~80%가 입력 → 줄이는 레버는 입력 길이</li><li>캐시는 쿼터를 줄이지 않아 절감에서 제외</li><li>LLM 호출 전 예산 가드 · 노드별 토큰 원장</li></ul>
<div class="end">기대할 몫은 탐지율이 아니다 — <span id="e1">입력 재현성(고정 조회 규약·순환성)</span> · <span id="e2">원문에 묶인 인용(사후)</span><br><span id="e3">지적 문장 일관성은 원샷과 차이 확인 안 됨(에이전트 0.687 대 원샷 0.746), 방향은 에이전트가 낮음(사전 등록)</span></div>""")

FCSS = """
.k{position:absolute;left:120px;top:96px}
h1{position:absolute;left:120px;top:150px;font-size:58px;font-weight:800;letter-spacing:-.02em}
h1 span{font-size:30px;color:var(--muted);font-weight:600;margin-left:18px}
ul{position:absolute;left:120px;right:120px;top:300px;list-style:none}
li{font-size:38px;font-weight:600;line-height:1.4;padding:26px 0 26px 0;border-top:2px solid var(--line)}
li small{display:block;font-size:27px;color:var(--muted);font-weight:500;margin-top:6px}
.f{position:absolute;left:120px;right:120px;bottom:120px;font-size:25px;color:var(--muted)}"""


def flist(kicker, title, sub, items, foot):
    lis = "".join(f"<li>{a}<small>{b}</small></li>" for a, b in items)
    return (FCSS, f"""<div class="k kicker">{kicker}</div><h1>{title}<span>{sub}</span></h1><ul>{lis}</ul><div class="f">{foot}</div>""")


cards["f1"] = flist("한계", "아직 말할 수 없는 것", "앞 장면 요약", [
    ("전문가 라벨이 없는 합성 Silver Set", "외부 자문 미확보 · 지적의 타당성은 평가하지 않음"),
    ("실제 1상 초록 43건 후향 검증 null", "AUROC 0.440 · 모델이 가린 약을 재식별해 기억과 분리되지 않음"),
    ("결함 없는 판에서 실행당 6.42건 지적", "줄이려던 두 시도는 결함까지 놓쳐 기각"),
    ("반복 일관성(사전 등록): 지적 문장 집합 차이 확인 안 됨(에이전트 0.687 대 원샷 0.746)", "방향은 에이전트가 낮음")],
    "기술서 13.1 · 발표자료 10쪽·부록 B1~B3")
cards["f2"] = flist("다음 단계", "판정 기준을 먼저 등록한다", "모두 계획 · 아직 실행하지 않음", [
    ("외부 전문가 2인 이상 맹검 라벨 → Gold Set", "평가자 간 κ ≥ 0.61일 때만 정답 세트로 쓴다(계획상 기준)"),
    ("재식별 탐침에서 약을 알아보지 못한 비공개 프로토콜로 재검증", "1차 지표: 전문가 라벨 대비 지적 정확성 · 규제 요구 기록이 쌓이면 AUROC CI 하한 > 0.5"),
    ("원샷 + 인용 판정기 + 도구 기권 구성과 비교", "비열등이면 다단계 구조를 기본값에서 내린다")],
    "단계별 자원·반증 조건: 기술서 13.2·13.4 · 발표자료 11쪽")
cards["f3"] = flist("의의", "확인된 범위까지만", "", [
    ("240 mg: PK 가정에 따라 판정이 갈려 기권", "결론 대신 용량군별 반복투여 PK 요청"),
    ("아다그라십·DV-505: 지표에 따라 갈려 기권", "로를라티닙은 갈리지 않아 기권하지 않음"),
    ("후향 43건: 입력이 비면 전형값으로 채우지 않음", "F00 43/43 기권(입력을 차단한 조건) · 승인은 사람이 한다")],
    "원샷 대비 우위·실제 약 판별력·도구 판정의 정확도는 의의로 주장하지 않는다")

cards["run"] = ("""
.k{position:absolute;left:120px;top:96px}
h1{position:absolute;left:120px;top:150px;font-size:58px;font-weight:800;letter-spacing:-.02em}
table{position:absolute;left:120px;top:270px;width:1680px;border-collapse:collapse}
td{font-size:32px;padding:20px 18px;border-bottom:1px solid var(--line);vertical-align:top}
td:first-child{width:80px;font-weight:800;color:var(--accent);font-size:36px}
td:nth-child(2){width:420px;font-weight:700}
td code{font-family:Consolas,monospace;font-size:28px;background:var(--soft);padding:2px 8px}
.f{position:absolute;left:120px;right:120px;bottom:120px;font-size:26px;color:var(--muted)}""", """
<div class="k kicker">실행 방법</div><h1>로그인 없이 바로 열린다</h1>
<table><tr><td>①</td><td>웹 UI</td><td>예시 프로토콜 선택 → 검토 실행</td></tr>
<tr><td>②</td><td>원클릭 라이브</td><td><code>?demo=1&amp;autorun=1</code></td></tr>
<tr><td>②′</td><td>저장 결과 즉시 보기</td><td><code>?demo=1&amp;cached=1</code> · LLM 호출 없음</td></tr>
<tr><td>③</td><td>직접 입력 · CLI</td><td>직접 붙여넣기 · 파일 업로드 · <code>python -m app.cli review …</code></td></tr>
<tr><td>④</td><td>로컬 Docker</td><td><code>docker build</code> → <code>docker run</code> · API 키 환경변수 필요</td></tr></table>
<div class="f">haribear99-doseverdict.hf.space · github.com/Haribear99/doseverdict</div>""")

cards["end"] = ("""
.k{position:absolute;left:120px;top:96px}
.m{position:absolute;left:120px;top:250px;font-size:72px;font-weight:800;line-height:1.3;letter-spacing:-.02em}
.u{position:absolute;left:120px;top:600px;font-size:48px;font-weight:700;color:var(--accent)}
.u2{position:absolute;left:120px;top:675px;font-size:32px;color:var(--muted)}
.f{position:absolute;left:120px;right:120px;bottom:120px;font-size:25px;color:var(--muted);border-top:1px solid var(--line);padding-top:20px}""", """
<div class="k kicker">DoseVerdict · MTD는 RP2D가 아니다</div>
<div class="m">정답을 맞히는 기계가 아니라,<br>근거가 얇을 때 멈추고<br>출처를 남기는 검토자</div>
<div class="u">haribear99-doseverdict.hf.space</div>
<div class="u2">?demo=1&amp;cached=1 저장 결과 · ?demo=1&amp;autorun=1 라이브 실행</div>
<div class="f">평가는 전문가 라벨이 없는 합성 Silver Set 기준 · 부정적 결과 전체는 상세기술서와 발표자료 10쪽·부록 B1~B3 · 제4회 JUMP AI Agentic Drug Challenge 본선</div>""")

for k, (css, body) in cards.items():
    (HERE / f"{k}.html").write_text(HEAD.format(css=css, body=body), encoding="utf-8")
print(" ".join(cards))
