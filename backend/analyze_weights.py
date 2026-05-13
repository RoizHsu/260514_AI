#!/usr/bin/env python3
"""分析 model_weights.pth 的確切架構"""

import torch
import os
from pathlib import Path

# 智能查找模型文件 - 支持相對路徑
script_dir = Path(__file__).parent
project_root = script_dir.parent

possible_paths = [
    project_root / "content" / "model_weights.pth",  # 從 backend 目錄相對查找
    script_dir / "content" / "model_weights.pth",     # 從同級目錄查找
    Path("content") / "model_weights.pth",             # 當前目錄
]

MODEL_PATH = None
for path in possible_paths:
    if path.exists():
        MODEL_PATH = path
        break

if not MODEL_PATH:
    print(f"❌ 找不到模型文件")
    print(f"搜索位置:")
    for path in possible_paths:
        print(f"  - {path.absolute()}")
    exit(1)

MODEL_PATH = str(MODEL_PATH)  # 轉換為字符串供 torch.load 使用

# 加載權重
state_dict = torch.load(MODEL_PATH, map_location='cpu')

print("=" * 80)
print("📊 模型權重結構分析")
print("=" * 80)
print(f"\n總參數數: {len(state_dict)}")
print(f"\n所有層的名稱和尺寸:\n")

total_params = 0
layer_groups = {}

for name, param in state_dict.items():
    total_params += param.numel()
    
    # 分類層
    prefix = name.split('.')[0]
    if prefix not in layer_groups:
        layer_groups[prefix] = []
    layer_groups[prefix].append((name, param.shape))
    
    print(f"  {name:50s} → {str(param.shape):30s}  ({param.numel():,} 參數)")

print(f"\n✅ 總參數數: {total_params:,}")

print("\n" + "=" * 80)
print("📋 按層分組統計")
print("=" * 80)
for prefix in sorted(layer_groups.keys()):
    group = layer_groups[prefix]
    group_params = sum(p[1].numel() for p in group)
    print(f"\n{prefix:20s}({len(group):2d} 層, {group_params:,} 參數)")
    for name, shape in group:
        print(f"  └─ {name.replace(prefix + '.', ''):40s} {str(shape):25s}")

print("\n" + "=" * 80)
print("🔍 推斷的模型結構")
print("=" * 80)

# 推斷輸入尺寸
if 'conv1.weight' in state_dict:
    print("\n✓ 有 CNN 層 (conv1)")
    print(f"  輸入通道: {state_dict['conv1.weight'].shape[1]}")
    print(f"  輸出通道: {state_dict['conv1.weight'].shape[0]}")

if 'linear_in.weight' in state_dict:
    print("\n✓ 線性投影層 (linear_in)")
    print(f"  輸入尺寸: {state_dict['linear_in.weight'].shape[1]}")
    print(f"  輸出尺寸: {state_dict['linear_in.weight'].shape[0]}")

if 'transformer' in state_dict or any('transformer' in k for k in state_dict.keys()):
    print("\n✓ Transformer 層存在")
    # 查找 embedding_dim
    for key in state_dict.keys():
        if 'norm' in key and 'weight' in key and 'transformer' in key:
            norm_dim = state_dict[key].numel()
            print(f"  Embedding 維度: {norm_dim}")
            break

if 'fc.weight' in state_dict:
    print("\n✓ 分類層 (fc)")
    print(f"  輸入尺寸: {state_dict['fc.weight'].shape[1]}")
    print(f"  輸出類別: {state_dict['fc.weight'].shape[0]}")
elif 'classifier.weight' in state_dict:
    print("\n✓ 分類層 (classifier)")
    print(f"  輸入尺寸: {state_dict['classifier.weight'].shape[1]}")
    print(f"  輸出類別: {state_dict['classifier.weight'].shape[0]}")

print("\n" + "=" * 80)
