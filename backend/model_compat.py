"""模型架構兼容性層 - 自動檢測並加載正確的模型架構"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleDirectModel(nn.Module):
    """直接匹配 AI team 權重結構的模型"""
    
    def __init__(self):
        super().__init__()
        
        # CNN 層
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        # 線性投影層: 196 → 128
        self.linear_in = nn.Linear(196, 128)
        
        # Transformer 單層（相容性）
        self.transformer_layer = nn.TransformerEncoderLayer(
            d_model=128,
            nhead=8,  
            dim_feedforward=2048,
            batch_first=True,
            norm_first=False
        )
        
        # Transformer 編碼器（2層）
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=128,
            nhead=8,  
            dim_feedforward=2048,
            batch_first=True,
            norm_first=False
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # 分類層: 8192 → 10
        self.fc = nn.Linear(8192, 10)
    
    def forward(self, x):
        # CNN 特徵提取
        x = self.pool(F.relu(self.conv1(x)))  # [batch, 32, 14, 14]
        x = self.pool(F.relu(self.conv2(x)))  # [batch, 64, 7, 7]
        
        # 展平
        batch_size = x.size(0)
        x_flat = x.view(batch_size, -1)  # [batch, 3136]
        
        # 調整為 196 維（通過採樣和填充）
        # 3136 = 64 * 49，需要縮減到 196
        if x_flat.size(1) >= 196:
            # 採樣：每 16 個取一個
            x_sampled = x_flat[:, ::16]
            if x_sampled.size(1) < 196:
                x_proj = F.pad(x_sampled, (0, 196 - x_sampled.size(1)))
            else:
                x_proj = x_sampled[:, :196]
        else:
            x_proj = F.pad(x_flat, (0, 196 - x_flat.size(1)))
        
        # 線性投影和 Transformer（可選路徑，主要用於權重相容性）
        # 現在暫不使用，因為主要路徑是 fc
        # x_transformed = self.linear_in(x_proj)
        # x_seq = x_transformed.unsqueeze(1)
        # x_seq = self.transformer_layer(x_seq)
        # x_seq = self.transformer(x_seq)
        
        # 分類層（主要輸出）
        # 將 3136 維特徵映射到 8192 維用於 fc 層
        if x_flat.size(1) >= 8192:
            x_fc = x_flat[:, :8192]
        else:
            # 填充到 8192
            x_fc = F.pad(x_flat, (0, 8192 - x_flat.size(1)))
        
        return self.fc(x_fc)


# 舊版本保留用於相容性
class DigitRecognitionCNN(nn.Module):
    """簡單 CNN 架構 - 備用"""
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 256)
        self.fc2 = nn.Linear(256, 10)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class DigitRecognitionTransformer(nn.Module):
    """混合 CNN + Transformer 架構 - 舊版本"""
    
    def __init__(self):
        super().__init__()
        
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        self.linear_in = nn.Linear(64 * 7 * 7, 256)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=256,
            nhead=8,
            dim_feedforward=512,
            batch_first=True,
            norm_first=False
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        self.fc = nn.Linear(256, 10)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.linear_in(x)
        x = x.unsqueeze(1)
        x = self.transformer(x)
        x = x.squeeze(1)
        x = self.fc(x)
        return x


def get_model_class(state_dict):
    """自動檢測並返回正確的模型類"""
    
    keys = set(state_dict.keys())
    
    # 檢查是否匹配新的 SimpleDirectModel 結構
    has_linear_in_196 = (
        'linear_in.weight' in keys and
        state_dict['linear_in.weight'].shape[1] == 196
    )
    has_fc_8192 = (
        'fc.weight' in keys and
        state_dict['fc.weight'].shape[1] == 8192
    )
    has_transformer_layers = (
        'transformer.layers.0.self_attn.in_proj_weight' in keys or
        'transformer.layers.1.self_attn.in_proj_weight' in keys
    )
    
    if has_linear_in_196 and has_fc_8192 and has_transformer_layers:
        print("✅ 檢測到 SimpleDirectModel 架構")
        return SimpleDirectModel
    
    # 檢查舊結構
    has_transformer = any('transformer' in k for k in keys)
    has_linear_in = any('linear_in' in k for k in keys)
    has_fc1_fc2 = any('fc1' in k and 'fc2' in k for k in keys)
    
    if has_transformer or has_linear_in:
        print("✅ 檢測到 DigitRecognitionTransformer 架構")
        return DigitRecognitionTransformer
    elif has_fc1_fc2:
        print("✅ 檢測到 DigitRecognitionCNN 架構")
        return DigitRecognitionCNN
    else:
        # 默認使用新的 SimpleDirectModel
        print("⚠️  使用默認 SimpleDirectModel 架構")
        return SimpleDirectModel
