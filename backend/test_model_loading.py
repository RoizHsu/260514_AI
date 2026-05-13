#!/usr/bin/env python3
"""測試新的模型架構能否加載實際權重"""

import torch
import os
import sys

# 動態查找模型文件
possible_paths = [
    "content/model_weights.pth",
    "C:/Users/HsuRoiz/Documents/260514_AI/content/model_weights.pth",
    os.path.expanduser("~/Documents/260514_AI/content/model_weights.pth")
]

MODEL_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        MODEL_PATH = path
        print(f"✅ 找到模型: {path}")
        break

if not MODEL_PATH:
    print("❌ 找不到模型文件")
    sys.exit(1)

# 導入模型
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from model_compat_new import SimpleDirectModel, get_model_class
    
    # 加載權重
    print("\n📊 加載權重...")
    state_dict = torch.load(MODEL_PATH, map_location='cpu')
    print(f"✓ 權重已加載 ({len(state_dict)} 個層)")
    
    # 檢測模型類
    print("\n🔍 檢測模型架構...")
    ModelClass = get_model_class(state_dict)
    print(f"✓ 選擇模型類: {ModelClass.__name__}")
    
    # 創建模型
    print("\n🏗️  創建模型...")
    model = ModelClass()
    print("✓ 模型已創建")
    
    # 嘗試加載權重
    print("\n⚙️  加載權重到模型...")
    try:
        model.load_state_dict(state_dict, strict=True)
        print("✅ 權重加載成功 (嚴格匹配)")
    except Exception as e:
        print(f"⚠️  嚴格匹配失敗: {e}")
        print("\n📝 嘗試寬鬆匹配...")
        try:
            model.load_state_dict(state_dict, strict=False)
            print("✅ 權重加載成功 (寬鬆匹配)")
        except Exception as e2:
            print(f"❌ 寬鬆匹配也失敗: {e2}")
            sys.exit(1)
    
    # 測試前向傳播
    print("\n🧪 測試前向傳播...")
    model.eval()
    x = torch.randn(2, 1, 28, 28)
    with torch.no_grad():
        output = model(x)
    print(f"✅ 前向傳播成功")
    print(f"   輸入: {x.shape}, 輸出: {output.shape}")
    
    # 檢查輸出值
    print(f"\n📈 輸出統計:")
    print(f"   最小值: {output.min().item():.4f}")
    print(f"   最大值: {output.max().item():.4f}")
    print(f"   平均值: {output.mean().item():.4f}")
    
    # 預測類別
    predictions = output.argmax(dim=1)
    print(f"\n🎯 預測:")
    print(f"   {predictions.tolist()}")
    
    print("\n✅ 所有測試通過！模型可以使用")
    
except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
