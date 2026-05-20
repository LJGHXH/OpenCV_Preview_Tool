"""
OpenCV 算子封装与注册表

每个算子描述包含：
    key        : 唯一标识
    label      : 界面显示名
    func       : 实际执行的函数 (frame, **params) -> frame
    params     : [(参数名, 默认值, 类型)]，类型为 'int' / 'float' / 'str'
    exclusive  : True 表示与其他互斥算子不能同时启用
                 （会改变通道数 / 数据类型 / 颜色空间，叠加易导致崩溃）
"""

import cv2
import numpy as np


# ---------------- 工具函数 ----------------
def _ensure_odd(n, min_v=1, max_v=31):
    """将 n 修正为 [min_v, max_v] 范围内的奇数"""
    n = int(n)
    if n < min_v:
        n = min_v
    if n > max_v:
        n = max_v
    if n % 2 == 0:
        n += 1
    return n


def _to_gray(frame):
    """确保得到单通道灰度图（输入可能是 RGB 或灰度）"""
    if frame.ndim == 3:
        return cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    return frame


def _to_rgb(frame):
    """确保得到 3 通道 RGB 图"""
    if frame.ndim == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    return frame


def _kernel(ksize):
    k = max(1, int(ksize))
    return cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))


# ============================================================
# ============== 互斥算子（改变图像格式） =====================
# ============================================================

# ---- 颜色空间转换 ----
def func_cvtColorGRAY(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


def func_cvtColorHSV(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)


def func_cvtColorYUV(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2YUV)


def func_cvtColorLAB(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)


def func_cvtColorHLS(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2HLS)


def func_cvtColorXYZ(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2XYZ)


def func_cvtColorYCrCb(frame):
    return cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)


# ---- 阈值化 ----
def func_threshold(frame, thresh=127, maxval=255):
    g = _to_gray(frame)
    _, out = cv2.threshold(g, int(thresh), int(maxval), cv2.THRESH_BINARY)
    return out


def func_threshold_inv(frame, thresh=127, maxval=255):
    g = _to_gray(frame)
    _, out = cv2.threshold(g, int(thresh), int(maxval), cv2.THRESH_BINARY_INV)
    return out


def func_threshold_otsu(frame):
    g = _to_gray(frame)
    _, out = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return out


def func_adaptiveThreshold(frame, blockSize=11, C=2):
    g = _to_gray(frame)
    bs = _ensure_odd(blockSize, min_v=3, max_v=99)
    return cv2.adaptiveThreshold(
        g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, bs, int(C)
    )


# ---- 边缘检测 ----
def func_Canny(frame, threshold1=100, threshold2=200):
    return cv2.Canny(frame, int(threshold1), int(threshold2))


def func_Sobel_x(frame, ksize=5):
    k = _ensure_odd(ksize, min_v=1, max_v=31)
    s = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=k)
    return cv2.convertScaleAbs(s)


def func_Sobel_y(frame, ksize=5):
    k = _ensure_odd(ksize, min_v=1, max_v=31)
    s = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=k)
    return cv2.convertScaleAbs(s)


def func_Laplacian(frame, ksize=3):
    k = _ensure_odd(ksize, min_v=1, max_v=31)
    s = cv2.Laplacian(frame, cv2.CV_64F, ksize=k)
    return cv2.convertScaleAbs(s)


def func_Scharr_x(frame):
    g = _to_gray(frame)
    return cv2.convertScaleAbs(cv2.Scharr(g, cv2.CV_64F, 1, 0))


def func_Scharr_y(frame):
    g = _to_gray(frame)
    return cv2.convertScaleAbs(cv2.Scharr(g, cv2.CV_64F, 0, 1))


# ---- 直方图均衡 ----
def func_equalizeHist(frame):
    return cv2.equalizeHist(_to_gray(frame))


def func_CLAHE(frame, clipLimit=2.0, tileSize=8):
    g = _to_gray(frame)
    ts = max(1, int(tileSize))
    clahe = cv2.createCLAHE(clipLimit=float(clipLimit), tileGridSize=(ts, ts))
    return clahe.apply(g)


# ---- 伪彩色映射 ----
_COLORMAPS = {
    0: cv2.COLORMAP_AUTUMN, 1: cv2.COLORMAP_BONE, 2: cv2.COLORMAP_JET,
    3: cv2.COLORMAP_WINTER, 4: cv2.COLORMAP_RAINBOW, 5: cv2.COLORMAP_OCEAN,
    6: cv2.COLORMAP_SUMMER, 7: cv2.COLORMAP_SPRING, 8: cv2.COLORMAP_COOL,
    9: cv2.COLORMAP_HSV, 10: cv2.COLORMAP_PINK, 11: cv2.COLORMAP_HOT,
}


def func_applyColorMap(frame, mapId=2):
    g = _to_gray(frame)
    cmap = _COLORMAPS.get(int(mapId), cv2.COLORMAP_JET)
    out = cv2.applyColorMap(g, cmap)  # 输出 BGR
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


# ---- 距离变换 ----
def func_distanceTransform(frame, thresh=127):
    g = _to_gray(frame)
    _, b = cv2.threshold(g, int(thresh), 255, cv2.THRESH_BINARY)
    d = cv2.distanceTransform(b, cv2.DIST_L2, 5)
    d = cv2.normalize(d, None, 0, 255, cv2.NORM_MINMAX)
    return d.astype(np.uint8)


# ============================================================
# ================== 可叠加算子（保形） =======================
# ============================================================

# ---- 几何变换 ----
def func_flip_h(frame):
    return cv2.flip(frame, 1)


def func_flip_v(frame):
    return cv2.flip(frame, 0)


def func_flip_both(frame):
    return cv2.flip(frame, -1)


def func_rotate_cw(frame):
    return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)


def func_rotate_ccw(frame):
    return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)


def func_rotate_180(frame):
    return cv2.rotate(frame, cv2.ROTATE_180)


def func_rotate_angle(frame, angle=30, scale=1.0):
    h, w = frame.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), float(angle), float(scale))
    return cv2.warpAffine(frame, M, (w, h))


# ---- 模糊 / 平滑 ----
def func_blur(frame, ksize=5):
    k = max(1, int(ksize))
    return cv2.blur(frame, (k, k))


def func_GaussianBlur(frame, ksize=5, sigma=0):
    k = _ensure_odd(ksize, min_v=1, max_v=31)
    return cv2.GaussianBlur(frame, (k, k), float(sigma))


def func_medianBlur(frame, ksize=5):
    k = _ensure_odd(ksize, min_v=1, max_v=31)
    return cv2.medianBlur(frame, k)


def func_bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75):
    return cv2.bilateralFilter(frame, int(d), float(sigmaColor), float(sigmaSpace))


def func_boxFilter(frame, ksize=5):
    k = max(1, int(ksize))
    return cv2.boxFilter(frame, -1, (k, k))


def func_pyrDownUp(frame):
    """金字塔下采样再上采样，得到模糊效果"""
    h, w = frame.shape[:2]
    d = cv2.pyrDown(frame)
    u = cv2.pyrUp(d)
    return cv2.resize(u, (w, h))


# ---- 形态学 ----
def func_erode(frame, ksize=5, iterations=1):
    return cv2.erode(frame, _kernel(ksize), iterations=int(iterations))


def func_dilate(frame, ksize=5, iterations=1):
    return cv2.dilate(frame, _kernel(ksize), iterations=int(iterations))


def func_morph_open(frame, ksize=5):
    return cv2.morphologyEx(frame, cv2.MORPH_OPEN, _kernel(ksize))


def func_morph_close(frame, ksize=5):
    return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, _kernel(ksize))


def func_morph_gradient(frame, ksize=5):
    return cv2.morphologyEx(frame, cv2.MORPH_GRADIENT, _kernel(ksize))


def func_morph_tophat(frame, ksize=9):
    return cv2.morphologyEx(frame, cv2.MORPH_TOPHAT, _kernel(ksize))


def func_morph_blackhat(frame, ksize=9):
    return cv2.morphologyEx(frame, cv2.MORPH_BLACKHAT, _kernel(ksize))


# ---- 像素 / 通道操作 ----
def func_brightness_contrast(frame, alpha=1.0, beta=0):
    """alpha：对比度倍数；beta：亮度偏移"""
    return cv2.convertScaleAbs(frame, alpha=float(alpha), beta=float(beta))


def func_bitwise_not(frame):
    return cv2.bitwise_not(frame)


def func_gamma(frame, gamma=1.5):
    g = max(0.01, float(gamma))
    inv = 1.0 / g
    table = np.array([((i / 255.0) ** inv) * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(frame, table)


# ---- 绘制 / 叠加 ----
def func_drawContours(frame, thresh=127):
    out = _to_rgb(frame).copy()
    gray = _to_gray(frame)
    _, t = cv2.threshold(gray, int(thresh), 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cv2.drawContours(out, contours, -1, (0, 255, 0), 2)


def func_putText(frame, text='OpenCV', x=20, y=40, scale=1.0):
    out = _to_rgb(frame).copy()
    return cv2.putText(out, str(text), (int(x), int(y)),
                       cv2.FONT_HERSHEY_SIMPLEX, float(scale), (0, 255, 0), 2)


def func_drawCenterRect(frame, size=200):
    out = _to_rgb(frame).copy()
    h, w = out.shape[:2]
    s = max(2, int(size))
    x1, y1 = (w - s) // 2, (h - s) // 2
    cv2.rectangle(out, (x1, y1), (x1 + s, y1 + s), (255, 0, 0), 2)
    return out


# ============================================================
# ====================== 算子注册表 ===========================
# ============================================================
OPERATORS = [
    # ---------- 互斥算子 ----------
    {'key': 'cvt_gray', 'label': 'cvtColor → GRAY',
     'func': func_cvtColorGRAY, 'params': [], 'exclusive': True},
    {'key': 'cvt_hsv', 'label': 'cvtColor → HSV',
     'func': func_cvtColorHSV, 'params': [], 'exclusive': True},
    {'key': 'cvt_yuv', 'label': 'cvtColor → YUV',
     'func': func_cvtColorYUV, 'params': [], 'exclusive': True},
    {'key': 'cvt_lab', 'label': 'cvtColor → LAB',
     'func': func_cvtColorLAB, 'params': [], 'exclusive': True},
    {'key': 'cvt_hls', 'label': 'cvtColor → HLS',
     'func': func_cvtColorHLS, 'params': [], 'exclusive': True},
    {'key': 'cvt_xyz', 'label': 'cvtColor → XYZ',
     'func': func_cvtColorXYZ, 'params': [], 'exclusive': True},
    {'key': 'cvt_ycc', 'label': 'cvtColor → YCrCb',
     'func': func_cvtColorYCrCb, 'params': [], 'exclusive': True},

    {'key': 'thresh_bin', 'label': 'threshold (BINARY)',
     'func': func_threshold,
     'params': [('thresh', 127, 'int'), ('maxval', 255, 'int')], 'exclusive': True},
    {'key': 'thresh_inv', 'label': 'threshold (BINARY_INV)',
     'func': func_threshold_inv,
     'params': [('thresh', 127, 'int'), ('maxval', 255, 'int')], 'exclusive': True},
    {'key': 'thresh_otsu', 'label': 'threshold (OTSU)',
     'func': func_threshold_otsu, 'params': [], 'exclusive': True},
    {'key': 'thresh_adapt', 'label': 'adaptiveThreshold',
     'func': func_adaptiveThreshold,
     'params': [('blockSize', 11, 'int'), ('C', 2, 'int')], 'exclusive': True},

    {'key': 'canny', 'label': 'Canny 边缘',
     'func': func_Canny,
     'params': [('threshold1', 100, 'int'), ('threshold2', 200, 'int')],
     'exclusive': True},
    {'key': 'sobel_x', 'label': 'Sobel x',
     'func': func_Sobel_x,
     'params': [('ksize', 5, 'int')], 'exclusive': True},
    {'key': 'sobel_y', 'label': 'Sobel y',
     'func': func_Sobel_y,
     'params': [('ksize', 5, 'int')], 'exclusive': True},
    {'key': 'laplacian', 'label': 'Laplacian',
     'func': func_Laplacian,
     'params': [('ksize', 3, 'int')], 'exclusive': True},
    {'key': 'scharr_x', 'label': 'Scharr x',
     'func': func_Scharr_x, 'params': [], 'exclusive': True},
    {'key': 'scharr_y', 'label': 'Scharr y',
     'func': func_Scharr_y, 'params': [], 'exclusive': True},

    {'key': 'eq_hist', 'label': 'equalizeHist 直方图均衡',
     'func': func_equalizeHist, 'params': [], 'exclusive': True},
    {'key': 'clahe', 'label': 'CLAHE 自适应均衡',
     'func': func_CLAHE,
     'params': [('clipLimit', 2.0, 'float'), ('tileSize', 8, 'int')],
     'exclusive': True},

    {'key': 'colormap', 'label': 'applyColorMap (mapId 0-11)',
     'func': func_applyColorMap,
     'params': [('mapId', 2, 'int')], 'exclusive': True},
    {'key': 'dist', 'label': 'distanceTransform',
     'func': func_distanceTransform,
     'params': [('thresh', 127, 'int')], 'exclusive': True},

    # ---------- 可叠加算子 ----------
    {'key': 'flip_h', 'label': '水平翻转 flip(1)',
     'func': func_flip_h, 'params': [], 'exclusive': False},
    {'key': 'flip_v', 'label': '垂直翻转 flip(0)',
     'func': func_flip_v, 'params': [], 'exclusive': False},
    {'key': 'flip_b', 'label': '双向翻转 flip(-1)',
     'func': func_flip_both, 'params': [], 'exclusive': False},
    {'key': 'rot_cw', 'label': 'rotate 90° 顺时针',
     'func': func_rotate_cw, 'params': [], 'exclusive': False},
    {'key': 'rot_ccw', 'label': 'rotate 90° 逆时针',
     'func': func_rotate_ccw, 'params': [], 'exclusive': False},
    {'key': 'rot_180', 'label': 'rotate 180°',
     'func': func_rotate_180, 'params': [], 'exclusive': False},
    {'key': 'rot_any', 'label': '任意角度旋转 warpAffine',
     'func': func_rotate_angle,
     'params': [('angle', 30, 'float'), ('scale', 1.0, 'float')],
     'exclusive': False},

    {'key': 'blur', 'label': '均值模糊 blur',
     'func': func_blur,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'gauss', 'label': '高斯模糊 GaussianBlur',
     'func': func_GaussianBlur,
     'params': [('ksize', 5, 'int'), ('sigma', 0, 'float')], 'exclusive': False},
    {'key': 'median', 'label': '中值模糊 medianBlur',
     'func': func_medianBlur,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'bilateral', 'label': '双边滤波 bilateralFilter',
     'func': func_bilateralFilter,
     'params': [('d', 9, 'int'), ('sigmaColor', 75, 'float'),
                ('sigmaSpace', 75, 'float')], 'exclusive': False},
    {'key': 'box', 'label': '盒式滤波 boxFilter',
     'func': func_boxFilter,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'pyr', 'label': '金字塔模糊 pyrDown→pyrUp',
     'func': func_pyrDownUp, 'params': [], 'exclusive': False},

    {'key': 'erode', 'label': '腐蚀 erode',
     'func': func_erode,
     'params': [('ksize', 5, 'int'), ('iterations', 1, 'int')],
     'exclusive': False},
    {'key': 'dilate', 'label': '膨胀 dilate',
     'func': func_dilate,
     'params': [('ksize', 5, 'int'), ('iterations', 1, 'int')],
     'exclusive': False},
    {'key': 'morph_open', 'label': '开运算 MORPH_OPEN',
     'func': func_morph_open,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'morph_close', 'label': '闭运算 MORPH_CLOSE',
     'func': func_morph_close,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'morph_grad', 'label': '形态学梯度 GRADIENT',
     'func': func_morph_gradient,
     'params': [('ksize', 5, 'int')], 'exclusive': False},
    {'key': 'morph_top', 'label': '顶帽 TOPHAT',
     'func': func_morph_tophat,
     'params': [('ksize', 9, 'int')], 'exclusive': False},
    {'key': 'morph_black', 'label': '黑帽 BLACKHAT',
     'func': func_morph_blackhat,
     'params': [('ksize', 9, 'int')], 'exclusive': False},

    {'key': 'bc', 'label': '亮度/对比度 convertScaleAbs',
     'func': func_brightness_contrast,
     'params': [('alpha', 1.0, 'float'), ('beta', 0, 'int')],
     'exclusive': False},
    {'key': 'invert', 'label': '反色 bitwise_not',
     'func': func_bitwise_not, 'params': [], 'exclusive': False},
    {'key': 'gamma', 'label': '伽马校正 LUT',
     'func': func_gamma,
     'params': [('gamma', 1.5, 'float')], 'exclusive': False},

    {'key': 'contour', 'label': '绘制轮廓 drawContours',
     'func': func_drawContours,
     'params': [('thresh', 127, 'int')], 'exclusive': False},
    {'key': 'puttext', 'label': '叠加文字 putText',
     'func': func_putText,
     'params': [('text', 'OpenCV', 'str'), ('x', 20, 'int'),
                ('y', 40, 'int'), ('scale', 1.0, 'float')],
     'exclusive': False},
    {'key': 'rect', 'label': '画中心矩形 rectangle',
     'func': func_drawCenterRect,
     'params': [('size', 200, 'int')], 'exclusive': False},
]
