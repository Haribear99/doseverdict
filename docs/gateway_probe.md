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
