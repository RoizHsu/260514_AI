"""
圖片識別 RESTful API
使用 FastAPI 框架提供 Swagger 文檔和圖片識別功能
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from PIL import Image
import io
import os
from datetime import datetime

app = FastAPI(
    title="圖片識別 API",
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

# 掛載靜態文件
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """根路徑重定向到前端"""
    return {
        "message": "圖片識別 API",
        "docs_url": "/docs",
        "frontend_url": "/frontend"
    }


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
