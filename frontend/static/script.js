// 常量定義
const API_BASE = '/api';
const RECOGNIZE_ENDPOINT = `${API_BASE}/recognize`;

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

let selectedFile = null;

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

    // 顯示結果容器
    resultContainer.classList.remove('hidden');
}

// 重置表單
function resetForm() {
    selectedFile = null;
    fileInput.value = '';
    previewContainer.classList.add('hidden');
    resultContainer.classList.add('hidden');
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
