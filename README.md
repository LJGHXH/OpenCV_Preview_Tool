# OpenCV_Preview_Tool

**English** | [中文](README_zh.md)

A Tkinter-based GUI tool for previewing the real-time effects of various OpenCV operators on your webcam feed.

## Features

- **Real-time webcam preview** — Captures frames from the local camera and displays operator effects live
- **Responsive layout** — Video preview and operator panel resize automatically with the window
- **48 OpenCV operators** in two categories:
  - **Exclusive operators (21)** — Change image channels / color space / dtype; only one can be active at a time
  - **Stackable operators (27)** — Preserve image shape; can be freely combined and applied in listed order
- **Adjustable parameters** — Each operator renders input fields for its parameters, taking effect immediately
- **Fault-tolerant** — Invalid parameters fall back to defaults; a single operator failure won't crash the app

## Operator List

### Exclusive Operators (only one active at a time)

| Category | Operators |
|----------|-----------|
| Color Space Conversion | GRAY, HSV, YUV, LAB, HLS, XYZ, YCrCb |
| Thresholding | threshold (BINARY / BINARY_INV / OTSU), adaptiveThreshold |
| Edge Detection | Canny, Sobel x/y, Laplacian, Scharr x/y |
| Histogram Equalization | equalizeHist, CLAHE |
| Other | applyColorMap (12 color maps), distanceTransform |

### Stackable Operators (freely combinable)

| Category | Operators |
|----------|-----------|
| Geometric | flip (horizontal / vertical / both), rotate 90°/180°, arbitrary angle rotation (warpAffine) |
| Blur / Smooth | blur, GaussianBlur, medianBlur, bilateralFilter, boxFilter, pyrDown→pyrUp |
| Morphology | erode, dilate, OPEN, CLOSE, GRADIENT, TOPHAT, BLACKHAT |
| Pixel / Channel | brightness/contrast (convertScaleAbs), invert (bitwise_not), gamma correction (LUT) |
| Drawing | drawContours, putText, center rectangle |

## Requirements

- Python 3.6+
- opencv-python
- Pillow
- tkinter (bundled with Python)

## Installation

```bash
pip install opencv-python Pillow
```

## Usage

```bash
python main.py
```

1. The left panel shows the live webcam feed after launch.
2. Check operators on the right panel to apply effects to the preview.
3. Operators marked **[Exclusive]** are mutually exclusive — enabling one automatically disables others in the same group.
4. Stackable operators can be combined freely; they are applied top-to-bottom in list order.
5. Parameter changes in the input fields take effect immediately (no Enter key needed).
6. Drag the window edges to resize — the preview and panel adapt automatically.

## Project Structure

```
OpenCV_Preview_Tool/
├── main.py          # Entry point: builds the GUI and rendering loop
├── cv2Func.py       # Operator implementations + registry (OPERATORS)
├── threadFunc.py    # Threading utility
├── README.md        # English
└── README_zh.md     # 中文
```

## Notice

> Drag the window to experience the responsive layout. The right panel supports mouse-wheel scrolling through all operators.
