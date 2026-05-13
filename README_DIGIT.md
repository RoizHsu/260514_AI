# 手寫數字識別系統

一個高性能、可靠的手寫數字識別系統，使用 PyTorch 深度學習模型，配備完整的 RESTful API、Web UI 和 Docker 部署支持。專為生產環境設計，能應對高並發和壓力測試。

## 📋 項目背景

公司 AI 團隊完成了手寫數字識別模型的訓練，本系統將該模型轉化為可對外服務的完整解決方案，供客戶端工程師快速部署。

## ✨ 核心特性

- ✅ **高性能 CNN 模型** - 基於 PyTorch 的卷積神經網絡
- ✅ **RESTful API** - FastAPI 框架，自動生成 Swagger 文檔
- ✅ **Swagger 文檔** - `/docs` 端點提供交互式 API 測試
- ✅ **Web UI** - 響應式設計，支持拖放上傳
- ✅ **HTTPS 支持** - SSL 安全連接
- ✅ **Docker 容器化** - 一鍵部署
- ✅ **高可靠性** - 優化的錯誤處理和日誌記錄
- ✅ **可擴展架構** - 易於集成高級模型

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Web UI)                         │
│  HTML5 + CSS3 + JavaScript (拖放上傳、實時預覽)          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────▼──────────────────────────────────┐
│         Nginx 反向代理 (可選生產環境)                    │
│  - SSL/TLS 終止                                         │
│  - 負載均衡                                             │
│  - 靜態文件服務                                         │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│           FastAPI 應用服務器                            │
│  - RESTful API (/api/recognize, /api/health)            │
│  - Swagger 文檔 (/docs)                                │
│  - 靜態文件挂載 (/static)                               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              PyTorch 深度學習模型                        │
│  - CNN 架構 (2 conv layers + 2 FC layers)              │
│  - 輸入: 28×28 灰度圖                                  │
│  - 輸出: 0-9 數字分類 + 置信度                          │
│  - GPU 支持 (CUDA)                                     │
└──────────────────────────────────────────────────────────┘
```

## 📁 項目結構

```
260514_AI/
├── backend/
│   ├── main.py                 # FastAPI 應用 (API 端點、生命週期管理)
│   ├── model.py                # PyTorch 模型定義
│   └── requirements.txt         # Python 依賴
├── frontend/
│   ├── index.html              # 主頁面
│   └── static/
│       ├── style.css           # 樣式
│       └── script.js           # 客戶端邏輯
├── content/                    # AI 團隊交付的模型文件
│   ├── inference.ipynb         # 推論範例
│   ├── model_weights.pth       # 預訓練模型權重 ⭐
│   ├── train.csv              # 訓練資料
│   ├── test.csv               # 測試資料
│   ├── sample_submission.csv   # 輸出格式參考
│   └── saved_images/          # 範例圖片
├── ssl/                        # HTTPS 證書 (首次執行時生成)
│   ├── cert.pem
│   └── key.pem
├── Dockerfile                  # Docker 容器配置
├── docker-compose.yml          # Docker Compose 編排
├── nginx.conf                  # Nginx 反向代理配置
├── generate_ssl.py             # SSL 證書生成工具
├── README.md                   # 本文檔
├── HTTPS_SETUP.md              # HTTPS 配置指南
└── .gitignore                  # Git 忽略規則
```

## 🚀 快速開始

### 方式 1️⃣: 本地開發（推薦新手）

#### 環境要求
- Python 3.10+
- pip

#### 步驟

```bash
# 1. 進入後端目錄
cd backend

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 啟動應用（自動生成 SSL 證書）
python main.py
```

**訪問應用：**
- 前端: `https://localhost:8000`
- API 文檔: `https://localhost:8000/docs`
- 健康檢查: `https://localhost:8000/api/health`

### 方式 2️⃣: Docker 部署（生產推薦）

#### 環境要求
- Docker
- Docker Compose

#### 步驟

```bash
# 1. 構建和啟動容器
docker-compose up --build

# 2. 訪問應用
# 前端: http://localhost
# API: http://localhost/api
# 文檔: http://localhost/docs
```

**停止服務：**
```bash
docker-compose down
```

## 📚 API 端點

### 1. 手寫數字識別

```http
POST /api/recognize
Content-Type: multipart/form-data

file: <binary image data>
```

**請求示例 (Python)：**
```python
import requests

with open('digit.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/recognize',
        files={'file': f}
    )
    print(response.json())
```

**請求示例 (PowerShell)：**
```powershell
$file = Get-Item 'digit.jpg'
$response = Invoke-WebRequest `
  -Uri "http://localhost:8000/api/recognize" `
  -Method Post `
  -Form @{file = $file}

$response.Content | ConvertFrom-Json | Format-List
```

**響應示例：**
```json
{
  "success": true,
  "data": {
    "predicted_digit": 7,
    "confidence": 0.9847,
    "confidence_percentage": "98.47%",
    "all_predictions": [
      {"digit": 7, "confidence": 0.9847},
      {"digit": 1, "confidence": 0.0089},
      {"digit": 4, "confidence": 0.0032}
    ],
    "image_size": {
      "original": [600, 400],
      "processed": [28, 28]
    }
  },
  "timestamp": "2026-05-13T15:30:00.123456"
}
```

### 2. 健康檢查

```http
GET /api/health
```

**響應：**
```json
{
  "status": "healthy",
  "model_status": "已加載",
  "device": "cpu",
  "timestamp": "2026-05-13T15:30:00.123456"
}
```

### 3. 系統統計

```http
GET /api/stats
```

**響應：**
```json
{
  "api_version": "1.0.0",
  "model_path": "/path/to/model_weights.pth",
  "model_exists": true,
  "device": "cpu",
  "cuda_available": false,
  "input_size": "28x28 灰度圖",
  "output_classes": 10,
  "timestamp": "2026-05-13T15:30:00.123456"
}
```

## 🧠 模型詳情

### 架構

```
Input: [Batch, 1, 28, 28]  (28×28 灰度圖)
   ↓
Conv2d(1→32, kernel=3) + ReLU + MaxPool2d(2)  → [Batch, 32, 14, 14]
   ↓
Conv2d(32→64, kernel=3) + ReLU + MaxPool2d(2)  → [Batch, 64, 7, 7]
   ↓
Flatten  → [Batch, 64×7×7=3136]
   ↓
Linear(3136→128) + ReLU + Dropout(0.5)
   ↓
Linear(128→10)  (輸出層，10 個類別: 0-9)
   ↓
Output: [Batch, 10]  (每個數字的概率)
```

### 模型性能

- **輸入**: 28×28 灰度圖像
- **輸出**: 10 類（數字 0-9）+ 置信度
- **預期準確率**: 95%+（根據訓練資料）
- **推論時間**: < 50ms（CPU），< 10ms（GPU）

## 🔒 HTTPS 配置

### 本地開發（自簽名證書）

第一次運行時會自動生成 HTTPS 證書：

```bash
# 手動生成（如需）
python generate_ssl.py
```

**Chrome 安全警告處理：**
1. 點擊「高級」
2. 點擊「繼續前往 localhost」

### 生產環境（真實證書）

參考 [HTTPS_SETUP.md](HTTPS_SETUP.md) 使用 Let's Encrypt 或商業 CA 頒發的證書。

## 📊 技術棧

| 組件 | 技術 | 版本 |
|-----|------|------|
| **後端框架** | FastAPI | 0.136.1 |
| **Web 服務器** | Uvicorn | 0.46.0 |
| **深度學習** | PyTorch | 2.1.2 |
| **影像處理** | Pillow + OpenCV | 12.2.0 + 4.13.0.92 |
| **反向代理** | Nginx | Alpine |
| **容器** | Docker | 29.4.3 |
| **容器編排** | Docker Compose | 5.1.3 |
| **前端** | HTML5 + CSS3 + JavaScript | - |

## 🔧 環境變量

創建 `.env` 文件（可選）：

```env
# API 配置
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=False

# HTTPS
USE_HTTPS=true

# 日誌
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 模型
MODEL_PATH=content/model_weights.pth
```

## 🛡️ 可靠性和穩定性

### 架構優化

✅ **應用生命週期管理**
- 使用 FastAPI lifespan context manager
- 應用啟動時預加載模型
- 優雅的關閉序列

✅ **錯誤處理**
- 完整的異常捕獲和日誌記錄
- 明確的錯誤信息返回
- 模型加載失敗時的降級方案

✅ **性能優化**
- 模型預加載（避免重複加載）
- GPU 支持（if available）
- 高效的圖片預處理

✅ **監控和診斷**
- 詳細的應用日誌
- 健康檢查端點
- 系統統計信息

### 壓力測試建議

```bash
# 使用 Apache Bench
ab -n 1000 -c 100 http://localhost:8000/api/health

# 使用 wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/health

# 使用 locust
locust -f locustfile.py --host=http://localhost:8000
```

## 🔄 持續部署

### 更新模型

```bash
# 替換模型文件
cp /path/to/new_model.pth content/model_weights.pth

# 重啟應用
docker-compose restart api
```

### 更新代碼

```bash
# 提交更改
git add .
git commit -m "更新信息"

# 構建新映像
docker-compose up --build -d
```

## 📈 可擴展性

### 集成更高級的模型

在 `backend/model.py` 中替換模型架構：

```python
from torchvision.models import resnet50

class DigitRecognitionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = resnet50(pretrained=True)
        # 修改輸出層...
```

### 添加數據庫

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@db/dbname"
engine = create_engine(DATABASE_URL)
```

### 添加隊列系統

```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_image(image_path):
    # 異步處理...
```

## ❓ 常見問題

### Q1: 模型加載失敗怎麼辦？

**A:** 檢查：
1. 模型文件是否在 `content/model_weights.pth`
2. PyTorch 是否已安裝
3. 查看日誌：`docker-compose logs api`

### Q2: GPU 加速支持嗎？

**A:** 是的！系統自動檢測 CUDA：
- 有 GPU：自動使用
- 無 GPU：自動降級到 CPU
- 檢查：訪問 `/api/stats` 查看 `device` 字段

### Q3: 如何修改模型輸入大小？

**A:** 修改 `backend/model.py` 中的卷積層配置和 `main.py` 中的 resize 尺寸。

### Q4: 支持並發請求嗎？

**A:** 是的！FastAPI 天生支持異步。可通過調整 Uvicorn workers 來增加並發：

```bash
uvicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Q5: 如何部署到雲端？

**A:** 支持所有主流云平台：
- **AWS**: ECS / Fargate
- **阿里雲**: ACR / ECS
- **騰訊雲**: TCR / TKE
- **Azure**: ACI / AKS
- **Google Cloud**: GCR / GKE

參考各云平台的 Docker 部署文檔。

## 📝 Git 提交歷史

```
✅ 完成手寫數字識別系統 - 集成 PyTorch 模型、前端適配、穩定性優化
🔐 添加 HTTPS 支持 - SSL 证書配置和完整說明文檔
🔧 修復 Uvicorn reload 警告 - 使用應用導入字符串
📦 添加 cryptography 依賴並更新 SSL 生成腳本
✅ 修復前端顯示問題 - 正確提供 index.html 和靜態文件
✅ 修復依賴安裝異常 - 更新至 Python 3.14 兼容版本
✅ 完整的圖片識別系統：FastAPI 後端 + 前端網頁 + Docker 配置
```

## 📞 支持

遇到問題？

1. 查看日誌：`docker-compose logs -f api`
2. 檢查健康狀態：`curl http://localhost:8000/api/health`
3. 查看 API 文檔：`http://localhost:8000/docs`

## 📄 許可證

MIT License

---

**最後更新**：2026-05-13  
**系統版本**：1.0.0  
**維護狀態**：✅ 主動維護
