# DoseVerdict — Hugging Face Spaces(Docker SDK, CPU) / Cloud Run 공용 이미지
# 임베딩 인덱스(dense.npy·bm25.pkl)는 저장소에 포함되어 있어 빌드 시 재계산하지 않는다.
# bge-m3(질의 인코딩)·DeBERTa NLI는 첫 실행 시 HF Hub에서 내려받아 /data/hf 캐시에 둔다.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/data/hf HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
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
RUN mkdir -p /data/hf logs && chown -R user:user /data /home/user/app
USER user

EXPOSE 7860
HEALTHCHECK --interval=60s --timeout=10s --start-period=180s CMD curl -fs http://localhost:7860/_stcore/health || exit 1
CMD ["python", "-m", "streamlit", "run", "app/ui/main.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
