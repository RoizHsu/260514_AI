# 使用 Python 官方映像
FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製後端文件
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個項目
COPY . /app

# 暴露端口
EXPOSE 8000

# 啟動應用
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
