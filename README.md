# 圖片識別系統

一個完整的圖片識別系統，包含 RESTful API、前端網頁和 Docker 支持。

## 功能特性

- ✅ **RESTful API** - FastAPI 框架，自動生成 Swagger 文檔
- ✅ **Swagger 文檔** - `/docs` 端點提供交互式 API 文檔
- ✅ **前端網頁** - 響應式設計，支持拖放上傳
- ✅ **Docker 支持** - 一鍵部署，包含 Nginx 反向代理
- ✅ **CORS 支持** - 支持跨域請求
- ✅ **圖片識別** - 支持 JPEG 和 PNG 格式

## 系統架構

```
┌─────────────────────┐
│   前端（HTML/JS）   │
└──────────┬──────────┘
           │
        HTTP
           │
┌──────────▼──────────┐
│   Nginx 反向代理    │
└──────────┬──────────┘
           │
        HTTP
           │
┌──────────▼──────────┐
│   FastAPI 後端      │
│  (圖片識別邏輯)     │
└─────────────────────┘
```

## 快速開始

### 方法 1：使用 Docker Compose（推薦）

```bash
# 啟動整個系統
docker-compose up --build

# 系統會在以下地址運行：
# 前端: http://localhost
# API Swagger: http://localhost/docs
# API: http://localhost/api
```

### 方法 2：本地運行

#### 1. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 啟動 FastAPI 服務器

```bash
python main.py
# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 訪問應用

打開瀏覽器訪問：
- 前端: `http://localhost:8000/`
- API 文檔: `http://localhost:8000/docs`

## API 端點

### 健康檢查

```http
GET /api/health
```

**響應示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### 圖片識別

```http
POST /api/recognize
Content-Type: multipart/form-data

file: <binary image data>
```

**響應示例：**
```json
{
  "success": true,
  "data": {
    "object_name": "複雜物體",
    "confidence": 0.85,
    "image_size": {
      "width": 1920,
      "height": 1080
    },
    "features": {
      "edge_count": 45289,
      "brightness": 0.65
    }
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## 項目結構

```
260514_AI/
├── backend/
│   ├── main.py                 # FastAPI 應用
│   └── requirements.txt         # Python 依賴
├── frontend/
│   ├── index.html              # 主頁面
│   └── static/
│       ├── style.css           # 樣式文件
│       └── script.js           # 客戶端邏輯
├── Dockerfile                  # Docker 映像配置
├── docker-compose.yml          # Docker Compose 配置
├── nginx.conf                  # Nginx 配置
├── .gitignore                  # Git 忽略文件
└── README.md                   # 本文檔
```

## 技術棧

### 後端
- **FastAPI** - 高性能 Python Web 框架
- **Uvicorn** - ASGI 應用服務器
- **OpenCV** - 圖片處理和計算機視覺
- **Pillow** - 圖片操作
- **NumPy** - 數值計算

### 前端
- **HTML5** - 標記語言
- **CSS3** - 樣式和動畫
- **JavaScript** - 交互邏輯
- **Fetch API** - 網絡請求

### 基礎設施
- **Docker** - 容器化
- **Nginx** - 反向代理和靜態文件服務
- **Docker Compose** - 多容器編排

## 環境變量

創建 `.env` 文件（可選）：

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# 圖片配置
MAX_IMAGE_SIZE=10485760
ALLOWED_FORMATS=jpeg,png
```

## 部署指南

### AWS 部署

1. **建立 EC2 實例**

```bash
# 安裝 Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **部署應用**

```bash
# 克隆倉庫
git clone <your-repo-url>
cd 260514_AI

# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 阿里雲 / 騰訊雲部署

類似流程，使用各雲服務商提供的 CVM/ECS 實例。

## 使用 CURL 測試 API

### 上傳圖片進行識別

```bash
curl -X POST "http://localhost:8000/api/recognize" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

### 檢查健康狀態

```bash
curl "http://localhost:8000/api/health"
```

## 擴展和自定義

### 集成高級模型

替換 `analyze_image()` 函數以使用更強大的模型：

```python
# 例：使用 YOLOv8
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

def analyze_image(image_cv, image_pil):
    results = model(image_cv)
    # 處理結果...
```

### 添加數據庫

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 常見問題

### Q1: Docker 容器無法啟動

**解決方案：**
```bash
# 檢查日誌
docker-compose logs api

# 重建映像
docker-compose down
docker-compose up --build --force-recreate
```

### Q2: 無法訪問 API 文檔

**解決方案：**
- 確保 FastAPI 正確運行：`http://localhost:8000/docs`
- 檢查防火牆設置

### Q3: 圖片上傳失敗

**解決方案：**
- 檢查文件格式（需要 JPEG 或 PNG）
- 檢查文件大小限制（默認 10MB）

## 效能優化

1. **啟用 Gzip 壓縮** - Nginx 配置
2. **使用 CDN** - 靜態文件分發
3. **實現緩存策略** - Redis / Memcached
4. **異步處理** - Celery 任務隊列

## 安全性考慮

- ✅ CORS 設置限制
- ✅ 文件類型驗證
- ✅ 文件大小限制
- ✅ 輸入驗證

建議添加：
- API 認證（JWT/OAuth2）
- 速率限制
- HTTPS/TLS

## 許可證

MIT License

## 支持

如有問題，請提交 Issue 或 Pull Request。

---

**最後更新：** 2024-01-15
