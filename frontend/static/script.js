// 常量定義
const API_BASE = '/api';
const RECOGNIZE_ENDPOINT = `${API_BASE}/recognize`;
const FEEDBACK_ENDPOINT = `${API_BASE}/feedback`;

// DOM 元素引用
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const recognizeBtn = document.getElementById('recognizeBtn');
const resultContainer = document.getElementById('resultContainer');
const resetBtn = document.getElementById('resetBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorMessage = document.getElementById('errorMessage');
const correctDigitInput = document.getElementById('correctDigitInput');
const submitFeedbackBtn = document.getElementById('submitFeedbackBtn');
const feedbackStatus = document.getElementById('feedbackStatus');
const feedbackMessage = document.getElementById('feedbackMessage');
const quickSelectButtons = document.getElementById('quickSelectButtons');

let selectedFile = null;
let lastRecognitionResult = null;

// 初始化事件監聽
function initializeEventListeners() {
    // 拖放事件
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // 文件選擇
    fileInput.addEventListener('change', handleFileSelect);

    // 按鈕事件
    recognizeBtn.addEventListener('click', recognizeImage);
    resetBtn.addEventListener('click', resetForm);
    submitFeedbackBtn.addEventListener('click', submitFeedback);

    // 數字輸入框按 Enter 提交
    correctDigitInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitFeedback();
        }
    });
}

// 拖放事件處理
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect({ target: { files } });
    }
}

// 文件選擇處理
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length === 0) return;

    const file = files[0];

    // 驗證文件類型
    if (!file.type.startsWith('image/')) {
        showError('請選擇有效的圖片文件');
        return;
    }

    selectedFile = file;
    showPreview(file);
}

// 顯示圖片預覽
function showPreview(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        hideError();
    };

    reader.readAsDataURL(file);
}

// 識別圖片
async function recognizeImage() {
    if (!selectedFile) {
        showError('請先選擇圖片');
        return;
    }

    try {
        showLoading(true);
        recognizeBtn.disabled = true;
        hideError();

        // 創建 FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 發送請求
        const response = await fetch(RECOGNIZE_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP 錯誤: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            displayResults(result.data, result.timestamp);
        } else {
            showError('識別失敗，請重試');
        }
    } catch (error) {
        console.error('識別錯誤:', error);
        showError(`錯誤: ${error.message}`);
    } finally {
        showLoading(false);
        recognizeBtn.disabled = false;
    }
}

// 顯示識別結果
function displayResults(data, timestamp) {
    // 存儲識別結果用於反饋
    lastRecognitionResult = {
        predictedDigit: data.predicted_digit,
        confidence: data.confidence,
        timestamp: timestamp
    };

    // 預測數字
    document.getElementById('predictedDigit').textContent = data.predicted_digit;

    // 置信度
    const confidence = Math.round(parseFloat(data.confidence_percentage) * 100) / 100;
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceFill.style.width = `${confidence}%`;
    document.getElementById('confidenceText').textContent = data.confidence_percentage;

    // Top 3 預測
    const predictionsList = document.getElementById('topPredictions');
    predictionsList.innerHTML = '';
    data.all_predictions.forEach(pred => {
        const percentage = Math.round(pred.confidence * 100);
        const item = document.createElement('div');
        item.className = 'prediction-item';
        item.innerHTML = `
            <span class="prediction-digit">數字 ${pred.digit}</span>
            <div class="prediction-bar">
                <div class="prediction-bar-fill" style="width: ${percentage}%"></div>
            </div>
            <span>${percentage}%</span>
        `;
        predictionsList.appendChild(item);
    });

    // 圖片尺寸
    const size = data.image_size;
    document.getElementById('imageSize').textContent = 
        `原始: ${size.original[0]}×${size.original[1]} px → 處理: ${size.processed[0]}×${size.processed[1]} px`;

    // 時間戳
    const date = new Date(timestamp);
    document.getElementById('timestamp').textContent = 
        date.toLocaleString('zh-TW', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

    // 生成快速選擇按鈕
    generateQuickSelectButtons(data.all_predictions);

    // 清除之前的反饋狀態
    feedbackStatus.classList.add('hidden');
    correctDigitInput.value = '';

    // 顯示結果容器
    resultContainer.classList.remove('hidden');
}

// 生成快速選擇按鈕
function generateQuickSelectButtons(predictions) {
    quickSelectButtons.innerHTML = '';
    
    predictions.forEach(pred => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'quick-select-btn';
        btn.textContent = pred.digit;
        btn.dataset.digit = pred.digit;
        
        btn.addEventListener('click', () => {
            // 移除其他按鈕的選中狀態
            document.querySelectorAll('.quick-select-btn').forEach(b => {
                b.classList.remove('selected');
            });
            // 標記當前按鈕為選中
            btn.classList.add('selected');
            // 清除輸入框
            correctDigitInput.value = '';
            // 提交反饋
            submitFeedbackWithDigit(pred.digit);
        });
        
        quickSelectButtons.appendChild(btn);
    });
}

// 提交反饋
async function submitFeedback() {
    const inputValue = correctDigitInput.value.trim();
    
    if (!inputValue) {
        showFeedbackError('請輸入正確的數字 (0-9)');
        return;
    }

    const digit = parseInt(inputValue);
    if (isNaN(digit) || digit < 0 || digit > 9) {
        showFeedbackError('請輸入有效的數字 (0-9)');
        return;
    }

    await submitFeedbackWithDigit(digit);
}

// 提交反饋（帶有數字）
async function submitFeedbackWithDigit(correctDigit) {
    if (!lastRecognitionResult) {
        showFeedbackError('沒有可用的識別結果');
        return;
    }

    try {
        submitFeedbackBtn.disabled = true;
        correctDigitInput.disabled = true;

        // 準備反饋數據
        const feedbackData = {
            predicted_digit: lastRecognitionResult.predictedDigit,
            correct_digit: correctDigit,
            confidence: lastRecognitionResult.confidence,
            timestamp: lastRecognitionResult.timestamp
        };

        // 發送反饋到後端
        const response = await fetch(FEEDBACK_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        });

        if (!response.ok) {
            // 即使後端沒有實現，我們也顯示成功（客戶端記錄）
            if (response.status === 404) {
                console.warn('反饋端點未實現，本地記錄反饋');
                recordFeedbackLocally(feedbackData);
                showFeedbackSuccess(`✓ 已記錄反饋：正確數字是 ${correctDigit}`);
            } else {
                throw new Error(`HTTP 錯誤: ${response.status}`);
            }
        } else {
            const result = await response.json();
            showFeedbackSuccess(`✓ ${result.message || `已記錄反饋：正確數字是 ${correctDigit}`}`);
        }
    } catch (error) {
        console.error('反饋錯誤:', error);
        // 本地記錄反饋
        recordFeedbackLocally({
            predicted_digit: lastRecognitionResult.predictedDigit,
            correct_digit: correctDigit,
            confidence: lastRecognitionResult.confidence,
            timestamp: lastRecognitionResult.timestamp
        });
        showFeedbackSuccess(`✓ 已記錄反饋：正確數字是 ${correctDigit}`);
    } finally {
        submitFeedbackBtn.disabled = false;
        correctDigitInput.disabled = false;
    }
}

// 本地記錄反饋（使用 localStorage）
function recordFeedbackLocally(feedbackData) {
    try {
        const feedback = JSON.parse(localStorage.getItem('digitFeedback') || '[]');
        feedback.push({
            ...feedbackData,
            recordedAt: new Date().toISOString()
        });
        localStorage.setItem('digitFeedback', JSON.stringify(feedback));
        console.log('反饋已本地記錄:', feedbackData);
    } catch (error) {
        console.error('本地記錄失敗:', error);
    }
}

// 顯示反饋成功信息
function showFeedbackSuccess(message) {
    feedbackMessage.textContent = message;
    feedbackStatus.className = 'feedback-status success';
    feedbackStatus.classList.remove('hidden');
    
    // 3 秒後隱藏
    setTimeout(() => {
        feedbackStatus.classList.add('hidden');
    }, 3000);
}

// 顯示反饋錯誤信息
function showFeedbackError(message) {
    feedbackMessage.textContent = message;
    feedbackStatus.className = 'feedback-status error';
    feedbackStatus.classList.remove('hidden');
}

// 重置表單
function resetForm() {
    selectedFile = null;
    lastRecognitionResult = null;
    fileInput.value = '';
    previewContainer.classList.add('hidden');
    resultContainer.classList.add('hidden');
    feedbackStatus.classList.add('hidden');
    correctDigitInput.value = '';
    quickSelectButtons.innerHTML = '';
    hideError();
}

// 顯示載入指示器
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

// 顯示錯誤信息
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// 隱藏錯誤信息
function hideError() {
    errorMessage.classList.add('hidden');
}

// 頁面載入完成時初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    console.log('圖片識別系統已初始化');
});
