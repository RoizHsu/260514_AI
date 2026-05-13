# 手寫數字識別系統

完整的深度學習手寫數字識別系統，採用 PyTorch CNN+Transformer 混合架構，包含 RESTful API、Web UI 和 Docker 容器化部署。

## ⚡ 一鍵啟動

```bash
docker-compose up
```

訪問: **http://localhost:8000** 📸

---

## ✨ 功能特性

- ✅ **Web UI** - 拖拽上傳手寫數字圖片，實時識別
- ✅ **REST API** - FastAPI 框架，自動生成 Swagger 文檔 (/docs)
- ✅ **深度學習模型** - 預訓練 PyTorch CNN+Transformer（1.9M 參數）
- ✅ **用戶反饋** - 收集識別結果和正確標籤，改進模型
- ✅ **Docker 部署** - 一鍵部署，跨平台運行
- ✅ **健康檢查** - 自動監控系統狀態

## 🏗️ 系統架構

```
客戶端瀏覽器
    ↓
Web UI (HTML5/CSS3/JS)
    ↓
FastAPI REST API (Port 8000)
    ↓
PyTorch CNN+Transformer Model
    ↓
數字分類 (0-9)
```

## 🚀 快速開始

### 前置要求

- Docker 19.03+
- Docker Compose 1.25+
- 2GB 可用磁盤空間
- 網路連接（首次下載 ~2GB）

### 方法 1：使用 Docker Compose（推薦）

```bash
# 啟動整個系統
docker-compose up

# 系統會在以下地址運行：
# Web UI: http://localhost:8000
# API 文檔: http://localhost:8000/docs
# 健康檢查: http://localhost:8000/api/health
```

### 方法 2：本地運行

#### 1. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 啟動 FastAPI 服務器

```bash
cd ..
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 訪問應用

打開瀏覽器訪問：
- Web UI: `http://localhost:8000/`
- API 文檔: `http://localhost:8000/docs`

## 📚 API 文檔

### 健康檢查

```http
GET /api/health
```

**響應示例：**
```json
{
  "status": "healthy",
  "model_status": "已加載",
  "device": "cpu",
  "timestamp": "2026-05-13T09:07:57.632176"
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
  "predicted_digit": 8,
  "confidence": 0.9523,
  "all_predictions": [
    {"digit": 8, "confidence": 0.9523},
    {"digit": 3, "confidence": 0.0421},
    {"digit": 0, "confidence": 0.0056}
  ]
}
```

### 獲取統計數據

```http
GET /api/stats
```

### 提交用戶反饋

```http
POST /api/feedback
Content-Type: application/json

{
  "predicted_digit": 3,
  "correct_digit": 8,
  "confidence": 0.95
}
```

## 📂 項目結構

```
260514_AI/
├── backend/
│   ├── main.py                 # FastAPI 應用程式
│   ├── model_compat.py         # 模型架構自動檢測
│   ├── requirements.txt         # Python 依賴
│   └── test_model_loading.py   # 模型測試腳本
├── frontend/
│   ├── index.html              # Web UI 主頁面
│   └── static/
│       ├── style.css           # 樣式（黑/灰色主題）
│       └── script.js           # 客戶端邏輯
├── content/
│   ├── model_weights.pth       # 預訓練 PyTorch 模型
│   └── feedback.json           # 用戶反饋數據
├── Dockerfile                  # Docker 映像配置
├── docker-compose.yml          # Docker Compose 配置
├── DEPLOYMENT.md               # 詳細部署指南
└── README.md                   # 本文檔
```

## 🔧 技術棧

### 後端
- **FastAPI 0.136.1** - 高性能 Python Web 框架
- **PyTorch 2.x** - 深度學習框架（CNN+Transformer）
- **Uvicorn** - ASGI 應用服務器
- **OpenCV** - 圖片處理
- **Pillow** - 圖片操作

### 前端
- **HTML5** - 標記語言
- **CSS3** - 樣式和動畫
- **JavaScript** - 交互邏輯

### 基礎設施
- **Docker** - 容器化
- **Docker Compose** - 多容器編排

## 📋 常用命令

| 命令 | 用途 |
|------|------|
| `docker-compose up` | 前台啟動（查看日誌） |
| `docker-compose up -d` | 後台啟動 |
| `docker-compose down` | 停止服務 |
| `docker-compose logs -f api` | 查看實時日誌 |
| `docker-compose ps` | 查看容器狀態 |

## ⚙️ 環境配置

### 系統要求
- CPU: 1+ 核心（推薦 2+ 核心）
- 記憶體: 2GB+（推薦 4GB+）
- 存儲: 2GB+（用於模型和依賴）

### Docker 資源限制

編輯 `docker-compose.yml` 添加資源限制（可選）：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🐛 故障排查

### 連接被拒絕

```
error: connection refused at 127.0.0.1:8000
```

解決方案：
```bash
docker-compose ps              # 檢查容器是否運行
docker-compose logs api        # 查看錯誤日誌
docker-compose restart api     # 重啟服務
```

### 模型加載失敗

檢查 `content/model_weights.pth` 是否存在且完整。

### 端口被佔用

```bash
# 改用其他端口，編輯 docker-compose.yml：
ports:
  - "9000:8000"  # 改為 9000
```

## 📊 生產部署建議

詳見 [DEPLOYMENT.md](DEPLOYMENT.md)

主要包括：
- 移除開發模式 `--reload` 標誌
- 配置反向代理（Nginx）
- 設置持久化卷
- 配置日誌和監控
- 實施負載測試

## ✅ 部署驗證

```bash
# 1. 檢查容器運行狀態
docker-compose ps
# 預期: api 容器狀態為 "Up"

# 2. 健康檢查
curl http://localhost:8000/api/health

# 3. 訪問 Web UI
# 瀏覽器打開: http://localhost:8000

# 4. 查看 API 文檔
# 瀏覽器打開: http://localhost:8000/docs
```

## 📞 技術支持

遇到問題？查看 [DEPLOYMENT.md](DEPLOYMENT.md) 中的故障排查部分。

## 📄 許可證

本項目為教學和商業用途開發。

---

**開始部署：`docker-compose up` 🚀**

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
