# 手寫數字識別系統

完整的深度學習手寫數字識別系統，採用 PyTorch CNN+Transformer 混合架構，包含 RESTful API、Web UI 和 Docker 容器化部署。
用dcoker匯入後打入 docker run -d --name test-digit-api -p 8000:8000 260514_ai:v3就可以進入http://localhost:8000網頁

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
### 端口被佔用

```bash
# 改用其他端口，編輯 docker-compose.yml：
ports:
  - "9000:8000"  # 改為 9000
```

**解決方案：**
- 確保 FastAPI 正確運行：`http://localhost:8000/docs`

### 圖片上傳失敗

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

