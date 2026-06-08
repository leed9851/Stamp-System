# 🖼️ 印章圖像清理工具 (Seal Cleaner)

一款基於 Streamlit、OpenCV 與 Pillow 開發的印章影像處理工具，可快速完成印章去背、色彩增強與透明背景輸出。

適用於：

* 公司大小章數位化
* 電子簽核系統
* 文件套印
* PDF電子文件製作
* 印章影像修復

---

# 功能特色

## 🎨 印章顏色辨識

支援：

* 紅色印章
* 藍色印章

系統自動透過 HSV 色彩空間偵測印章區域。

---

## 🎛️ 圖像調整功能

### ☀️ 亮度調整

調整整體圖片亮度

範圍：

-100 ～ +100

---

### ◐ 對比度調整

增強或降低影像層次感

範圍：

-100 ～ +100

---

### 🌈 飽和度調整

調整色彩鮮豔程度

範圍：

-100 ～ +100

---

### 🔴 印章顏色強度

僅針對印章區域進行處理：

#### 增強模式

* 提高紅章鮮豔度
* 提高藍章鮮豔度

#### 淡化模式

* 降低顏色濃度
* 轉趨灰階效果

範圍：

-100 ～ +100

---

## ✂️ 智慧去背

可將印章以外背景轉為透明。

支援：

* PNG透明背景輸出
* 保留印章原始色彩

---

## 🌫️ 邊緣羽化

去背後可進一步柔化邊緣。

範圍：

0 ～ 10 px

適用於：

* 文件套印
* 電子簽章
* OCR應用

---

# 預覽功能

提供：

## 原始圖片

上傳後原圖預覽

## 處理後圖片

即時顯示處理結果

所有參數調整皆可即時更新。

---

# 支援格式

## 輸入格式

* PNG
* JPG
* JPEG
* BMP

## 輸出格式

* PNG（支援透明背景）

---

# 系統需求

Python 3.10+

---

# 安裝方式

## 1. Clone 專案

```bash
git clone https://github.com/your-repository/seal-cleaner.git

cd seal-cleaner
```

---

## 2. 安裝套件

```bash
pip install -r requirements.txt
```

或直接安裝：

```bash
pip install streamlit
pip install opencv-python-headless
pip install pillow
pip install numpy
```

---

# 執行方式

```bash
streamlit run app.py
```

執行後瀏覽器開啟：

```text
http://localhost:8501
```

---

# 專案結構

```text
seal-cleaner/
│
├── app.py
├── README.md
├── requirements.txt
│
└── sample/
    ├── red_seal.jpg
    └── blue_seal.jpg
```

---

# 使用流程

## Step 1

上傳印章圖片

---

## Step 2

選擇印章顏色：

* 紅色
* 藍色

---

## Step 3

調整：

* 亮度
* 對比度
* 飽和度
* 印章顏色強度

---

## Step 4

選擇背景模式：

* 保留原始背景
* 透明背景（去背）

---

## Step 5

需要時調整邊緣羽化

---

## Step 6

下載 PNG 檔案

---

# 技術架構

| 模組              | 用途     |
| --------------- | ------ |
| Streamlit       | Web UI |
| OpenCV          | 影像處理   |
| NumPy           | 陣列運算   |
| Pillow          | 色彩調整   |
| HSV Color Space | 印章辨識   |

---

# 演算法說明

## 印章偵測

採用 HSV 色彩空間：

### 紅章

```text
H: 0~12
H: 170~180
```

### 藍章

```text
H: 90~140
```

---

## 遮罩優化

使用：

* Morphology Open
* Morphology Close

消除：

* 雜點
* 孔洞

---

## 羽化處理

使用：

```text
Gaussian Blur
```

產生自然邊緣效果。

---

# 未來規劃

* 自動辨識印章顏色
* 黑色印章支援
* 多印章分離
* AI去噪修復
* OCR文字辨識
* 批次處理
* PDF匯出
* Docker部署

---

# License

MIT License

---

# 作者

Seal Cleaner Project

Powered by:

* Streamlit
* OpenCV
* Pillow
* NumPy
