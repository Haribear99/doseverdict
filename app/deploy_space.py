"""
HF Space 배포 — 커밋된 파일(git archive HEAD)만 올린다.

실행: .venv/Scripts/python.exe -m app.deploy_space [--repo Haribear99/doseverdict]

Space 저장소는 큰 바이너리(.pkl·.npy·.pdf …)를 LFS로 저장한다. 저장소의 .gitattributes(`* text=auto`)를 그대로 올리면
LFS 규칙이 사라져 Docker 빌드의 clone이 포인터 파일을 받는다 → bm25.pkl 로드가 "invalid load key, 'v'"로 실패해
배포본에서 규제 조항 검색이 한 번도 동작하지 않았다(2026-09-25 발견). 그래서 Space에는 LFS 규칙을 더한 .gitattributes를 올린다.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import tarfile
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
LFS_EXT = ("pkl", "npy", "pdf", "png", "hwpx", "bin", "safetensors")


def space_gitattributes() -> str:
    base = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    keep = [ln for ln in base if not any(ln.startswith(f"*.{e} ") for e in LFS_EXT)]
    return "\n".join(keep + [f"*.{e} filter=lfs diff=lfs merge=lfs -text" for e in LFS_EXT]) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="Haribear99/doseverdict")
    a = ap.parse_args()
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    tar = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as d:
        with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
            tf.extractall(d, filter="data")
        (Path(d) / ".gitattributes").write_text(space_gitattributes(), encoding="utf-8", newline="\n")
        r = HfApi().upload_folder(folder_path=d, repo_id=a.repo, repo_type="space", commit_message=f"deploy HEAD {sha} (git archive)",
                                  delete_patterns=["app/**", "tests/**"])
    print(r)


if __name__ == "__main__":
    main()
