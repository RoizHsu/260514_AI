"""
手寫數字識別模型
基於 PyTorch CNN 架構
"""

import torch
import torch.nn as nn


class DigitRecognitionCNN(nn.Module):
    """手寫數字識別卷積神經網絡"""
    
    def __init__(self):
        super(DigitRecognitionCNN, self).__init__()
        
        # 卷積層
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        
        # 池化層
        self.pool = nn.MaxPool2d(2, 2)
        
        # 全連接層
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)
        
        # 激活函數和 Dropout
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        """前向傳播"""
        # 卷積 + 激活 + 池化
        x = self.pool(self.relu(self.conv1(x)))  # [N, 32, 14, 14]
        x = self.pool(self.relu(self.conv2(x)))  # [N, 64, 7, 7]
        
        # 展平
        x = x.view(-1, 64 * 7 * 7)
        
        # 全連接層
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        
        return x


def load_model(model_path: str, device: str = "cpu"):
    """加載訓練好的模型"""
    try:
        model = DigitRecognitionCNN().to(device)
        checkpoint = torch.load(model_path, map_location=device)
        
        # 如果保存的是 state_dict
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            model.load_state_dict(checkpoint['state_dict'])
        else:
            # 直接加載 state_dict
            model.load_state_dict(checkpoint)
        
        model.eval()  # 評估模式
        return model
    except Exception as e:
        raise RuntimeError(f"無法加載模型: {str(e)}")
