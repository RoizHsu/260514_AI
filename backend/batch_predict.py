"""
批量預測腳本 - 使用已訓練的模型權重
輸入: test.csv (28000 條測試圖片的像素數據)
輸出: submission.csv (預測結果，格式同 sample_submission.csv)
"""

import pandas as pd
import numpy as np
import torch
from pathlib import Path
import logging
from tqdm import tqdm
from model_compat import DigitRecognitionCNN, DigitRecognitionTransformer, get_model_class

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 路徑
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "content" / "model_weights.pth"
TEST_DATA_PATH = PROJECT_ROOT / "content" / "test.csv"
SUBMISSION_PATH = PROJECT_ROOT / "content" / "submission.csv"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    """加載已訓練的模型"""
    logger.info(f"🔧 加載模型 (設備: {DEVICE})...")
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"❌ 模型文件不存在: {MODEL_PATH}")
    
    # 加載檢查點
    checkpoint = torch.load(str(MODEL_PATH), map_location=DEVICE)
    
    # 提取 state_dict
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
    elif isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint
    
    # 自動選擇模型架構
    try:
        from model_compat import get_model_class
        ModelClass = get_model_class(state_dict)
    except:
        logger.warning("⚠️  無法自動檢測模型，使用 CNN")
        ModelClass = DigitRecognitionCNN
    
    model = ModelClass().to(DEVICE)
    
    try:
        model.load_state_dict(state_dict, strict=True)
        logger.info("✓ 模型加載成功 (完全匹配)！")
    except RuntimeError:
        logger.warning("⚠️  使用寬鬆匹配")
        model.load_state_dict(state_dict, strict=False)
        logger.info("✓ 模型加載成功 (寬鬆匹配)！")
    
    model.eval()
    return model


def load_test_data(batch_size=100):
    """
    加載測試數據
    返回: (image_id_list, image_tensor_list)
    """
    logger.info(f"📊 加載測試數據: {TEST_DATA_PATH}")
    
    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"❌ 測試數據文件不存在: {TEST_DATA_PATH}")
    
    df = pd.read_csv(TEST_DATA_PATH)
    logger.info(f"✓ 加載了 {len(df)} 條測試數據")
    logger.info(f"  特徵數: {len(df.columns)}")
    
    # 歸一化像素值到 0-1
    pixel_data = df.values.astype(np.float32) / 255.0
    
    # 轉換為 [N, 1, 28, 28] 形狀
    images = pixel_data.reshape(-1, 1, 28, 28)
    images = torch.from_numpy(images).to(DEVICE)
    
    return images


def predict_batch(model, images):
    """
    批量預測
    返回: 預測的數字
    """
    with torch.no_grad():
        outputs = model(images)
        predictions = torch.argmax(outputs, dim=1)
        return predictions.cpu().numpy()


def generate_submission(predictions):
    """
    生成提交文件
    格式: ImageId, Label
    """
    logger.info("📝 生成提交文件...")
    
    # ImageId 從 1 開始
    image_ids = np.arange(1, len(predictions) + 1)
    
    submission_df = pd.DataFrame({
        'ImageId': image_ids,
        'Label': predictions
    })
    
    submission_df.to_csv(SUBMISSION_PATH, index=False)
    logger.info(f"✓ 提交文件已生成: {SUBMISSION_PATH}")
    logger.info(f"  共 {len(submission_df)} 條預測")
    
    # 顯示統計信息
    logger.info("\n📊 預測統計:")
    for digit in range(10):
        count = (predictions == digit).sum()
        percentage = count / len(predictions) * 100
        logger.info(f"  數字 {digit}: {count:5d} ({percentage:5.2f}%)")
    
    return submission_df


def main():
    """主函數"""
    logger.info("🤖 批量數字識別預測系統")
    logger.info("=" * 60)
    
    try:
        # 加載模型
        model = load_model()
        
        # 加載測試數據
        test_images = load_test_data()
        
        # 批量預測
        logger.info("\n🔮 開始預測...")
        batch_size = 100
        all_predictions = []
        
        num_batches = (len(test_images) + batch_size - 1) // batch_size
        for i in tqdm(range(num_batches), desc="預測進度"):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(test_images))
            
            batch = test_images[start_idx:end_idx]
            batch_predictions = predict_batch(model, batch)
            all_predictions.extend(batch_predictions)
        
        all_predictions = np.array(all_predictions)
        
        # 生成提交文件
        submission_df = generate_submission(all_predictions)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 預測完成！")
        logger.info(f"   輸出文件: {SUBMISSION_PATH}")
        logger.info("\n📌 後續步驟:")
        logger.info("  1. 查看 content/submission.csv 檢查結果")
        logger.info("  2. 對比 content/sample_submission.csv 格式")
        logger.info("  3. 上傳到 Kaggle 或客戶服務器")
        
        return submission_df
        
    except Exception as e:
        logger.error(f"❌ 預測失敗: {e}")
        raise


if __name__ == "__main__":
    main()
