# 게이트웨이 프로브 결과 (2026-09-11 01:21)

## ① 모델별 최소 호출 (input: 'Reply only OK')

| model | status | output | in | out | reasoning | total | consumed(hdr) | quota_remaining(hdr) | tpm_left | rpm_left | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-luna | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 29999986 | 499986 | 299 | 2.542 |
| gpt-5.6-terra | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 29999972 | 499986 | 299 | 1.684 |
| gpt-5.6-sol | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 29999958 | 499986 | 299 | 1.953 |

## ② GPT-6 Astra 프로브 (허용 목록 밖 → 400/404 예상)

| model name | status | message |
| --- | --- | --- |
| gpt-6-astra | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6.0 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6.0-astra | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6-astra-2026-09-03 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |

## ③ Structured Outputs (text.format=json_schema, strict)

- **실패**: Expecting value: line 1 column 1 (char 0)

## ④ Function tool 호출

- status 200, function_calls=[('get_label_pk', '{"brand_name":"LUMAKRAS"}')], usage={'input_tokens': 67, 'output_tokens': 23, 'total_tokens': 90, 'reasoning_tokens': 0, 'cached_tokens': 0}

## ⑤ 스트리밍

- events=21, text='1, 2, 3, 4, 5', usage=ResponseUsage(input_tokens=17, input_tokens_details=InputTokensDetails(cache_write_tokens=0, cached_tokens=0), output_tokens=17, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=34), latency=1.63s

## ⑥ reasoning effort별 토큰 소비 (gpt-5.6-luna, 동일 프롬프트)

| effort | status | in | out | reasoning | total | consumed(hdr) | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | 200 | 37 | 7 | 0 | 44 | 44 | 1.307 |
| low | 200 | 37 | 60 | 50 | 97 | 97 | 2.137 |
| medium | 200 | 37 | 59 | 49 | 96 | 96 | 1.995 |

## 합계

```json
{
  "calls": 13,
  "by_model": {
    "gpt-5.6-luna": {
      "calls": 4,
      "input": 120,
      "output": 131,
      "total": 251
    },
    "gpt-5.6-terra": {
      "calls": 3,
      "input": 160,
      "output": 92,
      "total": 252
    },
    "gpt-5.6-sol": {
      "calls": 1,
      "input": 9,
      "output": 5,
      "total": 14
    },
    "gpt-6-astra": {
      "calls": 1,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6.0": {
      "calls": 1,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6": {
      "calls": 1,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6.0-astra": {
      "calls": 1,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6-astra-2026-09-03": {
      "calls": 1,
      "input": 0,
      "output": 0,
      "total": 0
    }
  },
  "last_quota": "29999449"
}
```

---

## ⑦ GPT-6 Astra 가용성 판정 (2026-09-11 01:21, Phase 0b)

| 확인 | 결과 |
|---|---|
| `GET /models` (0토큰) | 게이트웨이가 Azure 모델 카탈로그 417개를 반환. **`gpt-6-astra`, `gpt-6-astra-2026-09-03`, `gpt-6-astra-2026-09-03-private`가 카탈로그에 존재** |
| Responses 호출 5개 이름 | 전부 **404 `DeploymentNotFound`** — 리전 카탈로그에는 있으나 이 리소스에 배포(deployment)가 없음. 데이콘 공지 "gpt-6.0 지원 미정"과 일치 |
| 대조 gpt-5.6 3종 | 200 OK. `x-team-tokens-consumed` = `usage.total_tokens` (14/14) — **모델별 가중치 없음** |
| reasoning 토큰 | output_tokens에 포함되어 그대로 쿼터 차감(Luna none 44 / low 97 / medium 96) |
| Structured Outputs | effort none + max_output_tokens 300에서 정상(`{"drug":"Sotorasib","dose_mg":960,"verdict":"covered"}`). 기본 effort에 상한 64면 reasoning이 상한을 소진해 빈 출력 |
| Function tool / 스트리밍 | 정상 (tool call 인자 정확, SSE 21 이벤트) |

**판정**: Astra는 현재 사용 불가. 티어링(Sol/Terra/Luna) 유지. 토큰 과금이 모델 무관 1:1이므로 **품질이 필요한 노드는 주저 없이 Sol**을 쓴다.
**재시도**: `.venv/Scripts/python.exe -m app.llm.smoke_test` ②절. 배포되면 `.env`의 `DV_MODEL_PLANNER`·`DV_MODEL_REVIEWER`만 `gpt-6-astra`로 바꾼다. 본선 게시판 공지를 주 2회 확인.
**설계 메모**: 모델이 `verdict: covered`를 스스로 냈다. DoseVerdict는 판정을 LLM에 맡기지 않고 도구 계산(TCR 3지표)으로만 정하므로, Compiler 스키마에서 판정 필드를 제거하고 도구 결과로 채운다.
**토큰 사용**: Phase 0b 합계 약 900 토큰(잔여 29,999,000 이상).

---

## ⑧ 재실측 (2026-09-23 13:45) — 추가 3,000만 토큰 지급 후


### ① 모델별 최소 호출 (input: 'Reply only OK')

| model | status | output | in | out | reasoning | total | consumed(hdr) | quota_remaining(hdr) | tpm_left | rpm_left | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-luna | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 59999986 | 499986 | 299 | 3.298 |
| gpt-5.6-terra | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 59999972 | 499986 | 299 | 1.265 |
| gpt-5.6-sol | 200 | 'OK' | 9 | 5 | 0 | 14 | 14 | 59999958 | 499986 | 299 | 1.69 |

### ② GPT-6 Astra 프로브 (허용 목록 밖 → 400/404 예상)

| model name | status | message |
| --- | --- | --- |
| gpt-6-astra | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6.0 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6.0-astra | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6-astra-2026-09-03 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |

### ③ Structured Outputs (text.format=json_schema, strict)

- status 200, parsed={'drug': 'Sotorasib', 'dose_mg': 960, 'verdict': 'covered'}, usage={'input_tokens': 84, 'output_tokens': 26, 'total_tokens': 110, 'reasoning_tokens': 0, 'cached_tokens': 0}

### ④ Function tool 호출

- status 200, function_calls=[('get_label_pk', '{"brand_name":"LUMAKRAS"}')], usage={'input_tokens': 67, 'output_tokens': 33, 'total_tokens': 100, 'reasoning_tokens': 8, 'cached_tokens': 0}

### ⑤ 스트리밍

- events=21, text='1, 2, 3, 4, 5', usage=ResponseUsage(input_tokens=17, input_tokens_details=InputTokensDetails(cache_write_tokens=0, cached_tokens=0), output_tokens=17, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=34), latency=1.48s

### ⑥ reasoning effort별 토큰 소비 (gpt-5.6-luna, 동일 프롬프트)

| effort | status | in | out | reasoning | total | consumed(hdr) | latency_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | 200 | 37 | 7 | 0 | 44 | 44 | 21.837 |
| low | 200 | 37 | 58 | 48 | 95 | 95 | 2.411 |
| medium | 200 | 37 | 71 | 61 | 108 | 108 | 2.343 |

### 합계

```json
{
  "calls": 28,
  "by_model": {
    "gpt-5.6-luna": {
      "calls": 8,
      "input": 240,
      "output": 272,
      "total": 512
    },
    "gpt-5.6-terra": {
      "calls": 8,
      "input": 488,
      "output": 301,
      "total": 789
    },
    "gpt-5.6-sol": {
      "calls": 2,
      "input": 18,
      "output": 10,
      "total": 28
    },
    "gpt-6-astra": {
      "calls": 2,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6.0": {
      "calls": 2,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6": {
      "calls": 2,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6.0-astra": {
      "calls": 2,
      "input": 0,
      "output": 0,
      "total": 0
    },
    "gpt-6-astra-2026-09-03": {
      "calls": 2,
      "input": 0,
      "output": 0,
      "total": 0
    }
  },
  "last_quota": "59999753"
}
```

### ⑧ 판정

| 확인 | 결과 |
|---|---|
| Astra 5개 이름 | 여전히 **404 `DeploymentNotFound`**(09-11과 같음) → 사용 불가, 티어링 유지 |
| 쿼터 헤더 | `x-team-remaining-quota-tokens` = **59,999,986**. 호출마다 14씩 줄어듦(실시간 갱신 확인). 09-11 29,999,449 → 한도가 6,000만으로 재설정된 상태 |
| strict json_schema | `strict: true`에서 정상 파싱 → 앱 전 노드를 strict로 바꿀 수 있음 |
| 캐싱 | 응답 usage에 `cache_write_tokens`·`cached_tokens` 필드가 있음(이번엔 짧은 프롬프트라 0). 1,024토큰 이상 공통 접두부에서 적중하는지 별도 측정 필요 |
| 과금 | `consumed(hdr)` = `usage.total_tokens`(모델별 가중치 없음, 09-11과 같음) |

---

## ⑨ GPT-6 세대 Sol/Luna 프로브 (2026-09-23 14:21)

| model name | status | message |
| --- | --- | --- |
| gpt-6-sol | 200 | **응답 성공** output='OK' model=gpt-6-sol |
| gpt-6-luna | 200 | **응답 성공** output='OK' model=gpt-6-luna |
| gpt-6-sol-2026-09-22 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |
| gpt-6-luna-2026-09-22 | 404 | {"type": "invalid_request_error", "code": "DeploymentNotFound", "message": "The API deployment for this resource does not exist. If you created the deployment w |

## ⑩ 프롬프트 캐시와 쿼터 차감 (gpt-5.6-luna, 공통 접두부 약 2779 토큰 추정)

| call | in | cached | out | total | consumed(hdr) | quota_remaining(hdr) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2785 | 0 | 5 | 2790 | 2790 | 59997210 |
| 2 | 2785 | 0 | 5 | 2790 | 2790 | 59994420 |
| 3 | 2785 | 0 | 5 | 2790 | 2790 | 59991630 |

### ⑩-b 캐시 추가 확인 (gpt-6-luna, 같은 접두부 2회, `prompt_cache_key` 지정)

| call | in | cached | total | consumed(hdr) |
|---|---|---|---|---|
| 1 | 2783 | 0 | 2788 | 2788 |
| 2 | 2783 | **2780** | 2788 | **2788** |

gpt-6-sol: `reasoning.effort` none·low 모두 허용, strict json_schema 정상(`{"a":7}`, 43토큰).

### ⑨·⑩ 판정

| 확인 | 결과 |
|---|---|
| GPT-6 세대 | **`gpt-6-sol`, `gpt-6-luna` 호출 가능(200)**. 날짜 접미 이름은 404. 공지(09-07)에는 없는 모델 |
| 캐시 적중 | gpt-5.6-luna는 3회 모두 cached 0. gpt-6-luna는 2회차에 2,780/2,783 적중 |
| 쿼터 차감 | 캐시 적중 여부와 무관하게 `x-team-tokens-consumed` = `usage.total_tokens` → **캐시는 팀 토큰을 줄이지 않는다**(지연만 감소). 토큰 절감은 입력 축소·호출 수 감소·reasoning 토큰 감소로만 가능 |
