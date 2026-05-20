# OpenCV_Preview_Tool

[English](README.md) | **中文**

基于 Tkinter 的 GUI 工具，可实时预览各种 OpenCV 算子作用在摄像头画面上的效果。

## 功能概述

- **实时摄像头预览**：从本地摄像头捕获画面，实时预览所选算子的处理效果
- **自适应布局**：窗口缩放时，视频预览区和算子面板均会自动调整大小
- **48 种 OpenCV 算子**，分为两大类：
  - **互斥算子（21 种）**：改变图像通道/颜色空间/数据类型，同时仅能启用一个
  - **可叠加算子（27 种）**：保持图像形状，可任意组合，按列表顺序依次作用
- **参数可调**：每个算子右侧自动渲染参数输入框，修改后实时生效
- **安全机制**：非法参数自动回退默认值；单算子异常不影响整体运行

## 算子列表

### 互斥算子（同时仅能启用一个）

| 分类 | 算子 |
|------|------|
| 颜色空间转换 | GRAY, HSV, YUV, LAB, HLS, XYZ, YCrCb |
| 阈值化 | threshold (BINARY / BINARY_INV / OTSU), adaptiveThreshold |
| 边缘检测 | Canny, Sobel x/y, Laplacian, Scharr x/y |
| 直方图均衡 | equalizeHist, CLAHE |
| 其他 | applyColorMap (12 种色表), distanceTransform |

### 可叠加算子（可任意组合）

| 分类 | 算子 |
|------|------|
| 几何变换 | 水平/垂直/双向翻转, 90°/180°旋转, 任意角度旋转 (warpAffine) |
| 模糊/平滑 | blur, GaussianBlur, medianBlur, bilateralFilter, boxFilter, pyrDown→pyrUp |
| 形态学 | erode, dilate, OPEN, CLOSE, GRADIENT, TOPHAT, BLACKHAT |
| 像素/通道 | 亮度/对比度 (convertScaleAbs), 反色 (bitwise_not), 伽马校正 (LUT) |
| 绘制/叠加 | drawContours, putText, 中心矩形 (rectangle) |

## 环境依赖

- Python 3.6+
- opencv-python
- Pillow
- tkinter（Python 自带）

## 安装

```bash
pip install opencv-python Pillow
```

## 运行

```bash
python main.py
```

## 使用说明

1. 启动程序后，左侧自动显示摄像头实时画面
2. 右侧勾选算子即可叠加效果到预览画面
3. 标有 **[互斥]** 的算子同一时刻只能启用一个，开启新算子时会自动关闭之前的
4. 可叠加算子可随意勾选多个，按列表从上到下的顺序依次作用
5. 修改参数输入框中的数值后立即生效（无需回车确认）
6. 拖拽窗口边缘可缩放窗口，预览画面与面板自动适配

## 项目结构

```
OpenCV_Preview_Tool/
├── main.py          # 主程序入口，构建 GUI 与渲染循环
├── cv2Func.py       # 算子实现 + 算子注册表 (OPERATORS)
├── threadFunc.py    # 多线程辅助函数
├── README.md        # English
└── README_zh.md     # 中文
```

## 提示

> 启动后拖拽窗口即可体验自适应布局，右侧面板支持鼠标滚轮滚动浏览全部算子。
