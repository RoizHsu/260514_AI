"""
檢查模型架構腳本
分析 model_weights.pth 的實際結構
"""

import torch
from pathlib import Path
import json

MODEL_PATH = Path(__file__).parent.parent / "content" / "model_weights.pth"

def analyze_model_structure():
    """分析模型的狀態字典結構"""
    
    print("🔍 分析模型架構...")
    print("=" * 60)
    
    if not MODEL_PATH.exists():
        print(f"❌ 模型文件不存在: {MODEL_PATH}")
        return
    
    try:
        checkpoint = torch.load(str(MODEL_PATH), map_location='cpu')
        
        # 檢查是否是直接的 state_dict 或包含的字典
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
            print("✓ 模型格式: 完整檢查點 (包含 state_dict)")
        elif isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            print("✓ 模型格式: 完整檢查點 (包含 model_state_dict)")
        else:
            state_dict = checkpoint
            print("✓ 模型格式: 直接 state_dict")
        
        print(f"\n📊 模型層數: {len(state_dict)}")
        print("\n🔗 模型層結構:\n")
        
        # 按層組織輸出
        layers = {}
        for key in sorted(state_dict.keys()):
            layer_name = key.split('.')[0]
            if layer_name not in layers:
                layers[layer_name] = []
            
            tensor = state_dict[key]
            layers[layer_name].append((key, tensor.shape))
        
        # 打印層結構
        for layer_name, params in sorted(layers.items()):
            print(f"📦 {layer_name}:")
            for param_name, shape in params:
                short_name = param_name.replace(f"{layer_name}.", "")
                print(f"   • {short_name:50s} {str(shape):30s}")
            print()
        
        # 檢測模型類型
        print("=" * 60)
        print("🤖 模型類型檢測:\n")
        
        state_dict_keys = set(state_dict.keys())
        
        has_conv = any('conv' in k for k in state_dict_keys)
        has_transformer = any('transformer' in k for k in state_dict_keys)
        has_attention = any('attn' in k or 'self_attn' in k for k in state_dict_keys)
        has_linear = any('fc' in k or 'linear' in k for k in state_dict_keys)
        
        print(f"  卷積層 (Conv2d): {'✓' if has_conv else '✗'}")
        print(f"  Transformer 層: {'✓' if has_transformer else '✗'}")
        print(f"  注意力層 (Attention): {'✓' if has_attention else '✗'}")
        print(f"  全連接層 (FC): {'✓' if has_linear else '✗'}")
        
        if has_transformer and has_attention:
            print("\n🎯 推測模型類型: **混合模型 (CNN + Transformer)**")
            print("   架構可能為:")
            print("   1. CNN 特徵提取 → Transformer 編碼 → FC 分類")
            print("   2. 或其他混合架構")
        elif has_conv:
            print("\n🎯 推測模型類型: **純 CNN**")
        else:
            print("\n🎯 推測模型類型: **其他 (可能是 MLP/Transformer)**")
        
        # 估計模型大小
        total_params = sum(p.numel() for p in state_dict.values())
        print(f"\n📈 總參數數: {total_params:,}")
        print(f"   估計大小: {total_params * 4 / (1024*1024):.1f} MB (float32)")
        
        return state_dict
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        return None


if __name__ == "__main__":
    analyze_model_structure()
