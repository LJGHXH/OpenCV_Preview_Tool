import cv2


def func_test(frame):
    """测试专用"""
    # return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # return cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2XYZ)


def func_cvtColorGRAY(frame):
    """调用cvtColor中的灰度图"""
    return cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


def func_cvtColorHSV(frame):
    """"""
    return cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)


def func_cvtColorYUV(frame):
    """"""
    return cv2.cvtColor(frame, cv2.COLOR_RGB2YUV)


def func_GaussianBlur(frame):
    """"""
    return cv2.GaussianBlur(frame, (5, 5), 0)


def func_blur(frame):
    """"""
    return cv2.blur(frame, (5, 5))


def func_medianBlur(frame):
    """"""
    return cv2.medianBlur(frame, 5)


def func_Canny(frame):
    """"""
    return cv2.Canny(frame, 100, 200)


def func_Sobel_x(frame):
    """"""
    return cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=5)


def func_Sobel_y(frame):
    """"""
    return cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=5)


def func_Laplacian(frame):
    """"""
    return cv2.Laplacian(frame, cv2.CV_64F)


def func_erode(frame, kernel):
    """"""
    return cv2.erode(frame, kernel, iterations=1)


def func_dilate(frame, kernel):
    """"""
    return cv2.dilate(frame, kernel, iterations=1)


def func_morphologyEx_OPEN(frame, kernel):
    """"""
    return cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)


def func_morphology_CLOSE(frame, kernel):
    """"""
    return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)


def func_drawContours(frame, contours):
    """"""
    return cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

