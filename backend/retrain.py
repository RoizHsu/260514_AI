"""
使用反饋數據進行 AI 學習分析
讀取 feedback.json 中的用戶反饋，分析模型性能
"""

import json
from pathlib import Path
from datetime import datetime
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 路徑
PROJECT_ROOT = Path(__file__).parent.parent
FEEDBACK_FILE = PROJECT_ROOT / "content" / "feedback.json"


def load_feedback_data():
    """加載反饋數據"""
    if not FEEDBACK_FILE.exists():
        logger.warning("❌ 反饋文件不存在")
        return []
    
    try:
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            feedback = json.load(f)
        logger.info(f"✓ 加載 {len(feedback)} 條反饋數據")
        return feedback
    except Exception as e:
        logger.error(f"❌ 加載反饋失敗: {e}")
        return []


def analyze_feedback(feedback):
    """分析反饋數據"""
    if not feedback:
        return
    
    total = len(feedback)
    correct = sum(1 for f in feedback if f['predicted_digit'] == f['correct_digit'])
    incorrect = total - correct
    
    accuracy = correct / total * 100
    
    logger.info("\n📊 反饋數據分析：")
    logger.info(f"  • 總數據數: {total}")
    logger.info(f"  • 正確預測: {correct}")
    logger.info(f"  • 誤分類: {incorrect}")
    logger.info(f"  • 準確率: {accuracy:.2f}%")
    
    # 分析誤分類
    logger.info("\n🔍 誤分類分佈:")
    misclassified = {}
    for f in feedback:
        if f['predicted_digit'] != f['correct_digit']:
            key = f"{f['predicted_digit']} → {f['correct_digit']}"
            misclassified[key] = misclassified.get(key, 0) + 1
    
    for mistake, count in sorted(misclassified.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  • {mistake}: {count} 次")


def create_training_dataset(feedback, min_confidence_threshold=0.0):
    """
    從反饋數據創建訓練集
    主要針對 AI 低置信度且錯誤的情況進行訓練
    """
    logger.info("\n🎯 準備訓練數據...")
    
    training_pairs = []
    
    for f in feedback:
        predicted = f['predicted_digit']
        correct = f['correct_digit']
        confidence = f['confidence']
        
        # 優先使用：
        # 1. AI 錯誤的數據（最需要學習）
        # 2. AI 低置信度的數據（不確定的情況）
        if predicted != correct or confidence < 0.5:
            training_pairs.append({
                'predicted': predicted,
                'correct': correct,
                'confidence': confidence,
                'priority': 1 if predicted != correct else 0.5
            })
    
    logger.info(f"✓ 準備了 {len(training_pairs)} 條訓練數據")
    
    # 按優先級排序（錯誤的優先）
    training_pairs.sort(key=lambda x: x['priority'], reverse=True)
    
    return training_pairs


def suggest_improvements(feedback):
    """根據反饋提出改進建議"""
    if not feedback:
        return
    
    logger.info("\n💡 改進建議：")
    
    total = len(feedback)
    correct = sum(1 for f in feedback if f['predicted_digit'] == f['correct_digit'])
    accuracy = correct / total * 100
    
    if accuracy < 50:
        logger.info("  ⚠️  模型準確率過低，建議：")
        logger.info("     • 用反饋數據進行微調訓練")
        logger.info("     • 檢查模型權重是否正確加載")
        logger.info("     • 考慮使用更大的數據集重新訓練")
    elif accuracy < 80:
        logger.info("  ✓ 模型準確率需要改進，建議：")
        logger.info("     • 對高誤分類率的數字進行針對訓練")
        logger.info("     • 收集更多反饋數據")
    else:
        logger.info("  🎉 模型性能良好！")
    
    # 找出最容易混淆的數字對
    confusions = {}
    for f in feedback:
        if f['predicted_digit'] != f['correct_digit']:
            pair = tuple(sorted([f['predicted_digit'], f['correct_digit']]))
            confusions[pair] = confusions.get(pair, 0) + 1
    
    if confusions:
        logger.info("\n  最容易混淆的數字對：")
        for pair, count in sorted(confusions.items(), key=lambda x: x[1], reverse=True)[:3]:
            logger.info(f"    • 數字 {pair[0]} 和 {pair[1]}: {count} 次混淆")


def export_training_report(feedback):
    """導出訓練報告"""
    if not feedback:
        return
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_feedback": len(feedback),
        "correct_predictions": sum(1 for f in feedback if f['predicted_digit'] == f['correct_digit']),
        "accuracy": sum(1 for f in feedback if f['predicted_digit'] == f['correct_digit']) / len(feedback) * 100,
        "feedback_data": feedback
    }
    
    report_path = PROJECT_ROOT / "content" / "training_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n📄 訓練報告已保存到: {report_path}")


def main():
    """主函數"""
    logger.info("🤖 數字識別 - AI 學習分析系統")
    logger.info("=" * 50)
    
    # 加載反饋
    feedback = load_feedback_data()
    
    if not feedback:
        logger.error("❌ 沒有反饋數據可用")
        return
    
    # 分析反饋
    analyze_feedback(feedback)
    
    # 創建訓練數據
    training_data = create_training_dataset(feedback)
    
    # 提出改進建議
    suggest_improvements(feedback)
    
    # 導出報告
    export_training_report(feedback)
    
    logger.info("\n" + "=" * 50)
    logger.info("✓ 分析完成！")
    logger.info("\n📌 後續步驟：")
    logger.info("  1. 查看 content/training_report.json 獲取詳細報告")
    logger.info("  2. 使用 PyTorch 進行微調訓練")
    logger.info("  3. 部署更新的模型")


if __name__ == "__main__":
    main()
