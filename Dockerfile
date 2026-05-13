# 使用 Python 官方映像
FROM python:3.10-slim
LABEL maintainer="roiz <qqa123456408@gmail.com>"
LABEL version="1.0"
LABEL description="手寫數字識別 API - PyTorch + FastAPI"

# 設置工作目錄
WORKDIR /app

# 環境變量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安裝系統依賴（包括 Pillow 和 OpenCV 編譯所需）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsm6 libxext6 libxrender-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    liblcms2-dev libtiff-dev libwebp-dev \
    libraqm-dev libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴清單
COPY backend/requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個項目
COPY . /app

# 暴露端口
EXPOSE 8000

# 啟動應用
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


