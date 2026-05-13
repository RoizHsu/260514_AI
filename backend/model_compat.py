"""
兼容模型定義
支持 AI 團隊的混合 CNN + Transformer 架構
"""

import torch
import torch.nn as nn


class DigitRecognitionTransformer(nn.Module):
    """
    混合 CNN + Transformer 架構
    匹配 model_weights.pth 的結構
    """
    def __init__(self, num_classes=10):
        super(DigitRecognitionTransformer, self).__init__()
        
        # CNN 特徵提取層
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        
        # 線性投影層
        self.linear_in = nn.Linear(64 * 7 * 7, 256)
        
        # Transformer 編碼層
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=256,
            nhead=8,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # 分類層
        self.fc = nn.Linear(256, num_classes)
    
    def forward(self, x):
        # CNN 特徵提取
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 線性投影
        x = self.linear_in(x)
        
        # Transformer 編碼 (需要 [batch, seq_len, d_model] 格式)
        x = x.unsqueeze(1)  # [batch, 1, 256]
        x = self.transformer(x)
        x = x.squeeze(1)  # [batch, 256]
        
        # 分類
        x = self.fc(x)
        return x


class DigitRecognitionCNN(nn.Module):
    """原始簡單 CNN 架構"""
    def __init__(self):
        super(DigitRecognitionCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.relu3 = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = self.relu3(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def get_model_class(state_dict):
    """
    根據 state_dict 自動選擇正確的模型類
    """
    keys = set(state_dict.keys())
    
    # 檢測模型特徵
    has_transformer = any('transformer' in k for k in keys)
    has_linear_in = any('linear_in' in k for k in keys)
    has_fc1_fc2 = any('fc1' in k and 'fc2' in k for k in keys)
    
    if has_transformer or has_linear_in:
        return DigitRecognitionTransformer
    elif has_fc1_fc2:
        return DigitRecognitionCNN
    else:
        # 默認使用 Transformer (因為文件包含 transformer)
        return DigitRecognitionTransformer
