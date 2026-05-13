# HTTPS 配置指南

## 本地開發 (HTTP)

### 快速開始

```bash
cd backend
pip install -r requirements.txt
python main.py
```

訪問：`http://localhost:8000`

---

## 本地開發 (HTTPS)

### 第 1 步：生成 SSL 證書

#### Windows - 使用 Python 腳本

```bash
python generate_ssl.py
```

#### Windows - 使用 Git Bash 或 WSL

```bash
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=TW/ST=Taiwan/L=Taipei/O=Local/CN=localhost"
```

#### macOS / Linux

```bash
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=TW/ST=Taiwan/L=Taipei/O=Local/CN=localhost"
```

### 第 2 步：啟動應用

```bash
cd backend
python main.py
```

應用會自動檢測 SSL 證書並使用 HTTPS。

訪問：`https://localhost:8000`

⚠️ **瀏覽器警告**：因為是自簽名證書，Chrome/Edge 會顯示安全警告，點擊「繼續前往」即可。

---

## Docker 部署 (HTTPS)

### 第 1 步：生成 SSL 證書

```bash
python generate_ssl.py
```

會在 `ssl/` 目錄生成 `cert.pem` 和 `key.pem`

### 第 2 步：啟動 Docker Compose

```bash
docker-compose up --build
```

訪問：
- 前端（HTTPS）：`https://localhost`
- API（HTTPS）：`https://localhost/api`
- Swagger 文檔：`https://localhost/docs`

---

## Chrome 安全警告處理

### 方法 1：接受風險（開發用）
1. 看到紅色安全警告
2. 點擊「高級」
3. 點擊「繼續前往 localhost（不安全）」

### 方法 2：添加例外（Edge）
1. 設置 → 隱私、搜尋和服務
2. 安全性 → 管理例外
3. 新增 `localhost:8000` 或 `localhost`

### 方法 3：使用 Firefox
Firefox 對自簽名證書較寬鬆，可以直接訪問

---

## 生產環境 (使用真實 SSL 證書)

### 使用 Let's Encrypt (推薦)

```bash
# 安裝 Certbot
pip install certbot certbot-nginx

# 生成證書
sudo certbot certonly --standalone -d yourdomain.com

# 更新 nginx.conf
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

### AWS / 阿里雲 / 騰訊雲

各雲服務商提供免費或付費 SSL 證書：
- **AWS**: Certificate Manager (ACM)
- **阿里雲**: 免費 SSL 証書或付費版本
- **騰訊雲**: SSL 証書服務

---

## 常見問題

### Q1: Chrome 仍顯示「不安全」

**解決**：這是預期行為（自簽名證書）。生產環境必須使用真實 SSL 證書。

### Q2: Firefox 無法訪問

**解決**：
1. 在地址欄輸入 `about:config`
2. 搜索 `security.insecure_connection_icon.pbmode.ui_enabled`
3. 設置為 `true`

### Q3: Docker 中 HTTPS 無效

**解決**：
```bash
# 確保 ssl 目錄已掛載
ls ssl/
ls -la cert.pem key.pem

# 重建容器
docker-compose down
docker-compose up --build
```

### Q4: 如何禁用 HTTPS 警告？

**不建議**。應該：
- 開發環境：接受警告或使用 HTTP
- 生產環境：使用正式 SSL 證書

---

## 安全最佳實踐

✅ **開發環境**
- 使用自簽名證書
- 允許 CORS（僅限開發）
- 可禁用某些驗證

✅ **生產環境**
- 使用正式 SSL 證書（Let's Encrypt 或付費）
- 配置 CORS 白名單
- 啟用 HSTS (HTTP Strict Transport Security)
- 使用防火牆規則
- 定期更新依賴
- 啟用 API 認證（JWT/OAuth2）

---

## 更新 Nginx HSTS 配置

```nginx
server {
    listen 443 ssl;
    
    # ... SSL 配置 ...
    
    # HSTS 配置（強制 HTTPS）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

**最後更新**：2026-05-13
