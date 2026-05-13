# 📦 手寫數字識別系統 - 部署指南

## 🚀 快速開始（5分鐘內完成部署）

### 前置要求
- ✅ Docker 已安裝 (19.03+)
- ✅ Docker Compose 已安裝 (1.25+)
- ✅ 網路連接穩定（首次需下載映像，~2-3GB）

### 一鍵部署

```bash
# 1. 進入項目目錄
cd 260514_AI

# 2. 啟動所有服務
docker-compose up

# 3. 等待日誌出現 "Application startup complete"
```

### 訪問應用

| 功能 | URL |
|------|-----|
| 🖼️ Web UI（圖片上傳） | http://localhost:8000 |
| 📚 API 文檔 | http://localhost:8000/docs |
| 🔍 API 健康檢查 | http://localhost:8000/api/health |

---

## 📋 功能清單

### 1. **Web UI - 手寫數字識別**
- 📤 拖拽上傳手寫數字圖片
- 🔍 實時識別結果（0-9）
- 📊 顯示置信度和前 3 個預測
- 👍 提交反饋幫助改進模型

### 2. **REST API**
```bash
# 上傳圖片進行識別
curl -X POST -F "file=@digit.png" http://localhost:8000/api/recognize

# 獲取系統狀態
curl http://localhost:8000/api/health

# 獲取統計信息
curl http://localhost:8000/api/stats

# 提交用戶反饋
curl -X POST -H "Content-Type: application/json" \
  -d '{"predicted_digit": 3, "correct_digit": 8, "confidence": 0.95}' \
  http://localhost:8000/api/feedback
```

### 3. **自動生成的 Swagger 文檔**
訪問 http://localhost:8000/docs 查看完整 API 規範和測試工具

---

## 🔧 常用命令

### 啟動服務
```bash
docker-compose up              # 前台運行（看到日誌）
docker-compose up -d           # 後台運行
```

### 停止服務
```bash
docker-compose down            # 停止並刪除容器
docker-compose stop            # 停止但保留容器
```

### 查看日誌
```bash
docker-compose logs -f api     # 持續查看 API 日誌
docker-compose logs api        # 查看歷史日誌
```

### 清理資源
```bash
docker-compose down -v         # 停止並刪除所有卷（包括數據）
docker system prune            # 清理未使用的映像和容器
```

---

## 📊 系統架構

```
Client Browser
       ↓
   Web UI (HTML/CSS/JS)
       ↓
FastAPI REST API (Port 8000)
       ↓
PyTorch CNN+Transformer Model
       ↓
數字分類 (0-9)
```

### 核心組件

| 組件 | 技術 | 用途 |
|------|------|------|
| 後端 | FastAPI 0.136.1 | REST API + 模型推理 |
| 深度學習 | PyTorch 2.x | CNN+Transformer 混合架構 |
| 前端 | HTML5/CSS3/JS | 用戶介面 + 圖片上傳 |
| 容器 | Docker 19.03+ | 跨平台部署 |

---

## 🐳 Docker 配置說明

### docker-compose.yml
- **build**: 自動從 Dockerfile 構建映像
- **ports**: 映射容器 8000 端口到主機 8000
- **volumes**: 
  - `./frontend`: 前端靜態文件
  - `./backend`: 後端代碼（支持熱重載）
  - `./content`: 模型權重和用戶反饋數據
- **healthcheck**: 每 30s 檢查一次服務健康狀況

### Dockerfile
- **Base Image**: python:3.10-slim（輕量級）
- **系統依賴**: OpenCV、Pillow 等圖像處理库
- **PyTorch**: 使用官方 CPU 索引加速安裝
- **預設命令**: 自動啟動 Uvicorn 伺服器

---

## ⚠️ 故障排查

### 問題 1: 連接被拒絕
```
error: connection refused at 127.0.0.1:8000
```
**解決**:
```bash
docker-compose ps              # 檢查容器是否在運行
docker-compose logs api        # 查看錯誤日誌
docker-compose restart api     # 重啟 API 服務
```

### 問題 2: 模型加載失敗
```
WARNING: ⚠️ 未能導入模型類
```
**解決**:
- 確保 `content/model_weights.pth` 存在
- 檢查文件大小（應為 ~20MB）
- 查看日誌找到具體錯誤

### 問題 3: 內存不足
如果容器頻繁重啟，可限制內存：
```yaml
# docker-compose.yml 中添加
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

### 問題 4: 端口被占用
```
bind: address already in use
```
**解決**:
```bash
# 改用其他端口
docker-compose up -e "API_PORT=9000"

# 或修改 docker-compose.yml
ports:
  - "9000:8000"
```

---

## 🔐 生產部署建議

針對生產環境（壓力測試、高可用性）：

1. **移除 --reload 標誌**
   ```yaml
   command: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. **增加工作進程數**
   ```yaml
   command: gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
   ```

3. **配置反向代理（Nginx）**
   ```yaml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
   ```

4. **啟用持久卷**
   ```yaml
   volumes:
     feedback_data:
     model_cache:
   ```

5. **限制資源使用**
   ```yaml
   deploy:
     resources:
      limits:
        cpus: '2'
        memory: 4G
   ```

---

## 📞 技術支持

如遇問題，請檢查：
1. Docker 版本 (`docker --version`)
2. Docker Compose 版本 (`docker-compose --version`)
3. 容器日誌 (`docker-compose logs`)
4. 系統資源 (`docker stats`)

---

## ✅ 驗證部署成功

```bash
# 1. 容器運行
docker-compose ps
# 預期: api 容器狀態為 "Up"

# 2. 健康檢查
curl http://localhost:8000/api/health
# 預期: {"status":"healthy","model_status":"已加載",...}

# 3. Web UI 可訪問
# 在瀏覽器打開 http://localhost:8000

# 4. API 文檔可訪問
# 在瀏覽器打開 http://localhost:8000/docs
```

---

**部署完成！🎉 系統已準備好接收圖片和進行手寫數字識別。**
