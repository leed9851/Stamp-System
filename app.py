import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance

# ===== 页面配置 =====
st.set_page_config(page_title="印章图像清理", layout="centered")
st.title("🖼️ 印章圖像清理工具 (21×21mm)")

# ===== 工具函数 =====

def get_seal_mask(hsv, color):
    """提取印章颜色遮罩（支持红色/蓝色）"""
    if color == "紅色":
        # 红色在 HSV 色相环两端：0~12 和 170~180
        lower1 = np.array([0, 40, 40])
        upper1 = np.array([12, 255, 255])
        lower2 = np.array([170, 40, 40])
        upper2 = np.array([180, 255, 255])
        return cv2.bitwise_or(
            cv2.inRange(hsv, lower1, upper1),
            cv2.inRange(hsv, lower2, upper2)
        )
    else:
        # 蓝色：色相 90~140
        lower = np.array([90, 40, 40])
        upper = np.array([140, 255, 255])
        return cv2.inRange(hsv, lower, upper)


def refine_mask(mask, feather=0):
    """形态学清理遮罩 + 可选羽化边缘"""
    kernel = np.ones((3, 3), np.uint8)
    # 开运算去噪点
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # 闭运算填孔洞
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    # 边缘羽化
    if feather > 0:
        ksize = feather * 2 + 1  # 确保是奇数
        mask = cv2.GaussianBlur(mask, (ksize, ksize), 0)
    return mask


def slider_to_factor(value):
    """将滑块值 [-100, 100] 映射为调整因子 [0.0, 2.0]，0→1.0"""
    if value >= 0:
        return 1.0 + value / 100.0  # [1.0, 2.0]
    else:
        return 1.0 + value / 100.0  # [0.0, 1.0]


def adjust_brightness(pil_img, value):
    """调整亮度，value ∈ [-100, 100]"""
    if value == 0:
        return pil_img
    factor = slider_to_factor(value)
    return ImageEnhance.Brightness(pil_img).enhance(factor)


def adjust_contrast(pil_img, value):
    """调整对比度，value ∈ [-100, 100]"""
    if value == 0:
        return pil_img
    factor = slider_to_factor(value)
    return ImageEnhance.Contrast(pil_img).enhance(factor)


def adjust_saturation(pil_img, value):
    """调整饱和度，value ∈ [-100, 100]"""
    if value == 0:
        return pil_img
    factor = slider_to_factor(value)
    return ImageEnhance.Color(pil_img).enhance(factor)


def adjust_seal_intensity(pil_img, mask, color, value):
    """
    调整印章颜色强度，value ∈ [-100, 100]
    - 正值：增强印章颜色（叠加颜色层）
    - 负值：减弱印章颜色（混入灰度）
    - 零值：不做处理
    """
    if value == 0:
        return pil_img

    img_np = np.array(pil_img.convert("RGB")).astype(np.float32)

    # 将 mask 归一化到 [0, 1]，尺寸匹配图像
    mask_resized = cv2.resize(mask, (pil_img.width, pil_img.height))
    mask_norm = mask_resized.astype(np.float32) / 255.0

    if value > 0:
        # 增强：向印章区域叠加颜色
        strength = value / 100.0  # [0.01, 1.0]

        if color == "紅色":
            overlay = np.array([0.86, 0.0, 0.0])  # RGB 红色 (220,0,0) 归一化
        else:
            overlay = np.array([0.0, 0.0, 0.78])  # RGB 蓝色 (0,0,200) 归一化

        # 将原图归一化到 [0, 1]
        img_norm = img_np / 255.0

        # 在遮罩区域混合颜色
        for c in range(3):
            img_norm[:, :, c] = (
                img_norm[:, :, c] * (1 - mask_norm * strength * 0.5)
                + overlay[c] * mask_norm * strength * 0.5
            )

        img_np = img_norm * 255.0

    else:
        # 减弱：在遮罩区域降低饱和度（混入灰度）
        strength = abs(value) / 100.0  # [0.01, 1.0]

        # 计算灰度值
        gray = np.dot(img_np, [0.299, 0.587, 0.114])

        for c in range(3):
            img_np[:, :, c] = (
                img_np[:, :, c] * (1 - mask_norm * strength)
                + gray * mask_norm * strength
            )

    img_np = np.clip(img_np, 0, 255).astype(np.uint8)
    return Image.fromarray(img_np).convert("RGBA")


def apply_transparent_bg(pil_img, mask):
    """
    将遮罩外的区域变为透明
    - 遮罩区域（印章）：保留原色
    - 非遮罩区域（背景）：alpha = 0
    """
    img_rgba = pil_img.convert("RGBA")
    img_np = np.array(img_rgba)

    # 调整 mask 尺寸匹配图像
    mask_resized = cv2.resize(mask, (pil_img.width, pil_img.height))
    mask_norm = mask_resized.astype(np.float32) / 255.0

    # Alpha 通道 = mask（印章区域不透明，背景区域透明）
    img_np[:, :, 3] = (mask_norm * 255).astype(np.uint8)

    return Image.fromarray(img_np, "RGBA")


# ===== UI 组件 =====

uploaded_file = st.file_uploader(
    "📤 上傳印章圖片",
    type=["png", "jpg", "jpeg", "bmp"],
    help="支援 PNG、JPG、BMP 格式"
)

if uploaded_file is not None:
    # 读取图片
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img_bgr is None:
        st.error("❌ 無法讀取圖片，請確認格式正確。")
    else:
        # 转为 PIL RGBA（保留原始图片用于预览）
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        original_pil = Image.fromarray(img_rgb).convert("RGBA")

        # 印章颜色选择
        color = st.radio(
            "🎨 印章顏色",
            ["紅色", "藍色"],
            horizontal=True
        )

        # ===== 颜色调整区域 =====
        st.markdown("---")
        st.subheader("🎛️ 顏色調整")

        col1, col2 = st.columns(2)
        with col1:
            brightness_val = st.slider(
                "☀️ 亮度",
                -100, 100, 0,
                help="正值增亮，負值變暗"
            )
            contrast_val = st.slider(
                "◐ 對比度",
                -100, 100, 0,
                help="正值增強對比，負值減弱對比"
            )
        with col2:
            saturation_val = st.slider(
                "🌈 飽和度",
                -100, 100, 0,
                help="正值色彩更鮮豔，負值趨向灰階"
            )
            intensity_val = st.slider(
                "🔴 印章顏色強度",
                -100, 100, 0,
                help="正值增強印章顏色，負值淡化印章顏色"
            )

        # ===== 背景处理区域 =====
        st.markdown("---")
        st.subheader("🖼️ 背景處理")

        bg_mode = st.radio(
            "背景模式",
            ["保留原始背景", "透明背景（去背）"],
            horizontal=True
        )

        feather_val = 0
        if bg_mode == "透明背景（去背）":
            feather_val = st.slider(
                "邊緣羽化",
                0, 10, 2,
                help="羽化像素越大，印章邊緣越柔和"
            )

        # ===== 图像处理管道 =====
        # Step 1: 提取 HSV 遮罩
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask = get_seal_mask(hsv, color)
        mask = refine_mask(mask, feather=feather_val)

        # Step 2: 转换为 PIL 图像进行处理
        processed = original_pil.copy()

        # Step 3: 亮度调整
        processed = adjust_brightness(processed, brightness_val)

        # Step 4: 对比度调整
        processed = adjust_contrast(processed, contrast_val)

        # Step 5: 饱和度调整
        processed = adjust_saturation(processed, saturation_val)

        # Step 6: 印章颜色强度调整
        processed = adjust_seal_intensity(processed, mask, color, intensity_val)

        # Step 7: 背景透明化（如需要）
        if bg_mode == "透明背景（去背）":
            processed = apply_transparent_bg(processed, mask)

        # ===== 预览区域 =====
        st.markdown("---")
        st.subheader("📸 預覽對比")

        col_before, col_after = st.columns(2)
        with col_before:
            st.markdown("**原始圖片**")
            st.image(original_pil, use_container_width=True)
        with col_after:
            st.markdown("**處理後圖片**")
            st.image(processed, use_container_width=True)

        # ===== 下载 =====
        st.markdown("---")

        # 将处理后的图片转为字节
        img_bytes = processed.tobytes() if processed.mode == "RGBA" else processed.convert("RGBA").tobytes()

        st.download_button(
            label="📥 下載處理後的圖片 (PNG)",
            data=img_bytes,
            file_name="seal_cleaned.png",
            mime="image/png",
            use_container_width=True
        )

        # 显示当前遮罩（调试用，可折叠）
        with st.expander("🔍 查看印章遮罩"):
            st.image(mask, caption="印章遮罩（白色 = 偵測到的印章區域）", use_container_width=True)

else:
    # 未上传图片时的占位提示
    st.info("👆 請上傳一張 21×21mm 印章圖片以開始處理。")

    # 显示功能说明
    st.markdown("---")
    st.markdown("""
    ### ✨ 功能說明

    | 功能 | 說明 |
    |------|------|
    | **亮度 / 對比度** | 調整整張圖片的明暗和層次 |
    | **飽和度** | 增強或減弱整體色彩鮮豔程度 |
    | **印章顏色強度** | 針對印章區域增強或淡化顏色 |
    | **透明背景** | 自動偵測印章並移除背景 |
    | **邊緣羽化** | 讓去背後的印章邊緣更自然 |

    🎨 支援**紅色**和**藍色**印章。
    """)
