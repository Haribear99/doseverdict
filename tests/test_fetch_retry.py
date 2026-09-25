"""외부 API 호출 재시도 — 5xx는 재시도, 4xx는 즉시 실패(네트워크 없이 검증)."""
import io
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evidence"))
import pharmacology_evidence as pe  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, codes):
    calls = []

    def fake(req, timeout):
        calls.append(1)
        code = codes[len(calls) - 1]
        if code != 200:
            raise urllib.error.HTTPError(req.full_url, code, "err", {}, None)
        return _Resp(b'{"ok": true}')

    monkeypatch.setattr(pe.urllib.request, "urlopen", fake)
    monkeypatch.setattr(pe.time, "sleep", lambda s: None)
    return calls


def test_retries_5xx_then_succeeds(monkeypatch):
    calls = _patch(monkeypatch, [500, 502, 200])
    assert pe.fetch_json("http://x") == {"ok": True}
    assert len(calls) == 3


def test_4xx_fails_without_retry(monkeypatch):
    calls = _patch(monkeypatch, [404, 200])
    with pytest.raises(urllib.error.HTTPError):
        pe.fetch_json("http://x")
    assert len(calls) == 1


def test_gives_up_after_retries(monkeypatch):
    calls = _patch(monkeypatch, [500, 500, 500, 200])
    with pytest.raises(urllib.error.HTTPError):
        pe.fetch_json("http://x")
    assert len(calls) == 3
