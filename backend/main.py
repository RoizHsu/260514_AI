"""
圖片識別 RESTful API
使用 FastAPI 框架提供 Swagger 文檔和圖片識別功能
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from PIL import Image
import io
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="圖片識別",
    description="提供圖片識別功能的 RESTful API",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設置文件路徑
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# 掛載靜態文件
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """提供前端 HTML 文件"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return """
    <html>
        <head><title>圖片識別系統</title></head>
        <body>
            <h1>圖片識別系統</h1>
            <p>API 文檔: <a href="/docs">/docs</a></p>
        </body>
    </html>
    """


@app.post("/api/recognize")
async def recognize_image(file: UploadFile = File(...)):
    """
    接收圖片並進行識別
    
    - **file**: 上傳的圖片文件 (JPEG/PNG)
    - **returns**: 識別結果，包括物體名稱、置信度和其他信息
    """
    try:
        # 檢查文件類型
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(
                status_code=400,
                detail="僅支持 JPEG 和 PNG 格式的圖片"
            )
        
        # 讀取上傳的文件
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 轉換為 OpenCV 格式
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 簡單的圖片特徵分析（示例）
        # 實際項目可以集成更複雜的 ML 模型（如 YOLOv8、ResNet 等）
        result = analyze_image(image_cv, image)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"圖片識別失敗: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


def analyze_image(image_cv, image_pil):
    """
    分析圖片特徵（示例實現）
    可以替換為 YOLOv8、ResNet、CLIP 等模型
    """
    # 獲取圖片尺寸
    height, width, _ = image_cv.shape
    
    # 檢測邊緣
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_count = np.count_nonzero(edges)
    
    # 檢測顏色分佈
    hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)
    
    # 簡單的物體分類邏輯（示例）
    object_name = classify_image_simple(gray, edges, hsv)
    
    return {
        "object_name": object_name,
        "confidence": 0.85,
        "image_size": {
            "width": width,
            "height": height
        },
        "features": {
            "edge_count": int(edge_count),
            "brightness": float(np.mean(gray)) / 255.0
        }
    }


def classify_image_simple(gray, edges, hsv):
    """簡單的圖片分類（基於特徵）"""
    edge_density = np.count_nonzero(edges) / edges.size
    brightness = np.mean(gray) / 255.0
    
    if edge_density > 0.1:
        return "複雜物體"
    elif brightness > 0.7:
        return "亮色物體"
    elif brightness < 0.3:
        return "暗色物體"
    else:
        return "中等亮度物體"


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path
    
    # 檢查是否使用 HTTPS
    ssl_keyfile = None
    ssl_certfile = None
    
    # 尋找 SSL 證書
    ssl_dir = Path(__file__).parent.parent / "ssl"
    if ssl_dir.exists():
        cert_file = ssl_dir / "cert.pem"
        key_file = ssl_dir / "key.pem"
        
        if cert_file.exists() and key_file.exists():
            ssl_certfile = str(cert_file)
            ssl_keyfile = str(key_file)
            print("🔐 使用 HTTPS")
    
    # 啟動 Uvicorn 服務器
    uvicorn.run(
        app,
        host="127.0.0.1",  # 改為 localhost，而不是 0.0.0.0
        port=8000,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        reload=True
    )
