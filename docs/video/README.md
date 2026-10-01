# 시연 영상 제작 파이프라인

본선 제출용 시연 영상(`out/doseverdict_demo.mp4`)을 사람이 녹화하지 않고 만든다. 모든 명령은 프로젝트 루트에서 `py -3.14`로 실행한다.

필요한 것: ffmpeg, `pip install playwright edge-tts pillow`, `python -m playwright install chromium`, `fonts/`의 Pretendard(OFL, [릴리스 zip](https://github.com/orioncactus/pretendard/releases)의 `public/static`에서 Regular·Medium·SemiBold·Bold·ExtraBold).

| 순서 | 명령 | 결과 |
|---|---|---|
| 1 | `docs/video/capture.py` | `shots/*.png`와 강조 좌표 `*.marks.json`. 배포 Space의 저장 결과 화면과 덱 장면을 2배 해상도로 캡처한다 |
| 2 | `docs/video/capture.py --specs docs/video/shots_live.json` | `clips/live_gate.webm`. 라이브 실행부터 Human Gate 승인 클릭, Audit까지 녹화한다(LLM 호출 약 3.6만 토큰) |
| 3 | `docs/video/make_cards.py` → `docs/video/render_cards.py` | `cards/png/*.png`(훅·챕터·표 카드) |
| 4 | `docs/video/build.py` | TTS → 비트별 영상 → 자막 번인 → `out/doseverdict_demo.mp4`, `out/timeline.json` |
| 5 | `docs/video/export_script.py` | `docs/시연영상_스크립트.md`의 장면표를 제작본과 맞춘다 |

- 내용은 `storyboard.json` 한 곳에서 고친다. 장면(scene)은 배점 태그·워터마크·질문 자막을 갖고, 비트(beat)는 내레이션 한 덩어리와 화면 하나다. 비트 길이는 TTS 길이와 gap으로 정해지므로 음성과 화면이 어긋나지 않는다.
- 화면 종류: `image`(카드·정지 화면) · `view`(캡처의 한 창을 확대, `boxes`의 `spot: true`는 그 영역만 남기고 나머지를 흐리게) · `clip`(녹화 구간을 비트 길이에 맞춰 배속) · `seq`(한 비트 안에서 화면을 비율대로 잇기).
- 검수: `sheet.py 0.75`로 비트마다 프레임을 뽑아 접촉 시트(`out/sheet.png`)를 본다. `peek.py`는 캡처의 일부를 CSS 좌표로 잘라 본다.
- `out/`·`shots/`·`clips/`·`fonts/`는 다시 만들 수 있어 git에 넣지 않는다.
- 생성 이미지(GPT image)는 구도 참고로만 썼고 영상에 넣지 않는다.
