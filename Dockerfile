# DoseVerdict — Hugging Face Spaces(Docker SDK, CPU) / Cloud Run 공용 이미지
# 임베딩 인덱스(dense.npy·bm25.pkl)는 저장소에 포함되어 있어 빌드 시 재계산하지 않는다.
# bge-m3(질의 인코딩)·DeBERTa NLI는 **빌드 시** 이미지에 내려받는다(런타임 다운로드는 컨테이너 기동마다 4GB·3분 이상을 소모했다 — 2026-09-11 실측).
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/home/user/hf HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    DV_NLI_DEVICE=cpu STREAMLIT_SERVER_HEADLESS=true STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN apt-get update && apt-get install -y --no-install-recommends libxrender1 libxext6 libsm6 graphviz curl \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces는 uid 1000 사용자로 실행한다
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY requirements-deploy.txt ./
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r requirements-deploy.txt sentence-transformers graphviz

COPY --chown=user:user . .
RUN mkdir -p /home/user/hf logs && chown -R user:user /home/user
USER user

# 로컬 모델 사전 다운로드(약 3.6GB): 임베딩(bge-m3 bin)·영문 NLI·다국어 NLI(safetensors만). onnx·bin 중복 형식은 제외 —
# 전부 받으면 11GB, chown 레이어 중복까지 더하면 이미지가 41GB가 됐다(2026-09-11 실측). USER user 이후에 받아 chown 중복을 없앤다.
RUN python -c "from huggingface_hub import snapshot_download as d; d('BAAI/bge-m3', ignore_patterns=['onnx/*', 'imgs/*', '*.jpg', '*.md']); d('MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli', ignore_patterns=['onnx/*', '*.bin', '*.h5', '*.msgpack', '*.md']); d('MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7', ignore_patterns=['onnx/*', '*.bin', '*.h5', '*.msgpack', '*.md'])"

EXPOSE 7860
HEALTHCHECK --interval=60s --timeout=10s --start-period=180s CMD curl -fs http://localhost:7860/_stcore/health || exit 1
CMD ["python", "-m", "streamlit", "run", "app/ui/main.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
