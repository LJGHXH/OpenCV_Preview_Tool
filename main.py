"""
这是一个预览OpenCV各种函数效果的程序
它将支持直接预览并修改从摄像头捕获的画面，亦或是用户自定义导入的照片
"""
import cv2
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

import cv2Func
from threadFunc import threadIt


# 创建视频捕获对象，读取本地摄像头流
cap = cv2.VideoCapture(0)


def tkImage():
    """界面画布更新图像"""
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        return None
    frame = cv2.flip(frame, 1)  # 摄像头翻转
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 预设内核
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    '''画面叠加判定'''
    if set_func_test.get() == 1:
        frame = cv2Func.func_test(frame)
    if set_cvtColor_RGB2GRAY.get() == 1:
        frame = cv2Func.func_cvtColorGRAY(frame)
    if set_cvtColor_RGB2HSV.get() == 1:
        frame = cv2Func.func_cvtColorHSV(frame)
    if set_cvtColor_RGB2YUV.get() == 1:
        frame = cv2Func.func_cvtColorYUV(frame)
    if set_GaussianBlur.get() == 1:
        frame = cv2Func.func_GaussianBlur(frame)
    if set_blur.get() == 1:
        frame = cv2Func.func_blur(frame)
    if set_medianBlur.get() == 1:
        frame = cv2Func.func_medianBlur(frame)
    if set_Canny.get() == 1:
        frame = cv2Func.func_Canny(frame)
    if set_Sobel_x.get() == 1:
        frame = cv2Func.func_Sobel_x(frame)
    if set_Sobel_y.get() == 1:
        frame = cv2Func.func_Sobel_y(frame)
    if set_Laplacian.get() == 1:
        frame = cv2Func.func_Laplacian(frame)
    if set_erode.get() == 1:
        frame = cv2Func.func_erode(frame, kernel)
    if set_dilate.get() == 1:
        frame = cv2Func.func_dilate(frame, kernel)
    if set_morphologyEx_OPEN.get() == 1:
        frame = cv2Func.func_morphologyEx_OPEN(frame, kernel)
    if set_morphologyEx_CLOSE.get() == 1:
        frame = cv2Func.func_morphology_CLOSE(frame, kernel)
    if set_drawContour.get() == 1:
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, threshold_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2Func.func_drawContours(frame, contours)

    pilImage = Image.fromarray(frame)
    pilImage = pilImage.resize((image_width, image_height), Image.LANCZOS)
    tkImage = ImageTk.PhotoImage(image=pilImage)
    return tkImage


def update_frame():
    """更新画面"""
    global image_container
    pic = tkImage()
    if pic:
        canvas.create_image(0, 0, anchor='nw', image=pic)
        image_container = pic  # 保存引用
    else:
        print("No image to display")
    top.after(33, update_frame)  # 每33毫秒更新一次图像


if __name__ == '__main__':
    # 创建Tkinter窗口
    top = tk.Tk()
    top.title('视频窗口')
    top.geometry('1500x1000')
    image_width = 600
    image_height = 500
    canvas = Canvas(top, bg='white', width=image_width, height=image_height)
    Label(top, text='OpenCV函数效果预览', font=("黑体", 14)).place(x=50, y=20, anchor='nw')
    canvas.place(x=50, y=50)

    '''设置复选框专用变量'''
    # 测试专用
    set_func_test = tk.IntVar()
    # cvtColor专用
    set_cvtColor_RGB2GRAY = tk.IntVar()     # RGB转灰度图
    set_cvtColor_RGB2HSV = tk.IntVar()      # RGB转HSV输出
    set_cvtColor_RGB2YUV = tk.IntVar()      # RGB转YUV输出
    # 高斯模糊
    set_GaussianBlur = tk.IntVar()      # 基本
    set_blur = tk.IntVar()          # 均值模糊
    set_medianBlur = tk.IntVar()    # 中值模糊
    # 边缘检测
    set_Canny = tk.IntVar()     # Canny
    set_Sobel_x = tk.IntVar()   # Sobel x
    set_Sobel_y = tk.IntVar()   # Sobel y
    set_Laplacian = tk.IntVar()     # Laplacian
    # 形态学
    set_erode = tk.IntVar()     # 腐蚀
    set_dilate = tk.IntVar()    # 膨胀
    set_morphologyEx_OPEN = tk.IntVar()      # 开运算，用于去除小物体
    set_morphologyEx_CLOSE = tk.IntVar()     # 闭运算，用于填补小孔洞
    # 轮廓检测
    set_drawContour = tk.IntVar()

    '''设置按钮'''
    cb_cv2test = tk.Checkbutton(top, text='cv2testPreview', variable=set_func_test, onvalue=1, offvalue=0)
    cb_cvtColorGARY = tk.Checkbutton(top, text='cvtColor(img,COLOR_BGR2GRAY)', variable=set_cvtColor_RGB2GRAY, onvalue=1, offvalue=0)
    cb_cvtColorHSV = tk.Checkbutton(top, text='cvtColor(img,COLOR_BGR2HSV)', variable=set_cvtColor_RGB2HSV, onvalue=1, offvalue=0)
    cb_cvtColorYUV = tk.Checkbutton(top, text='cvtColor(img,COLOR_BGR2YUV)', variable=set_cvtColor_RGB2YUV, onvalue=1, offvalue=0)
    cb_GaussianBlur = tk.Checkbutton(top, text='GaussianBlur(img, (5, 5), 0)', variable=set_GaussianBlur, onvalue=1, offvalue=0)
    cb_blur = tk.Checkbutton(top, text='blur.(img, (5, 5), 0)', variable=set_blur, onvalue=1, offvalue=0)
    cb_medianBlur = tk.Checkbutton(top, text='medianBlur(img,5)', variable=set_medianBlur, onvalue=1, offvalue=0)
    cb_Canny = tk.Checkbutton(top, text='Canny(img, 100, 200)', variable=set_Canny, onvalue=1, offvalue=0)
    cb_Sobel_x = tk.Checkbutton(top, text='Sobel(img, CV_64F, 1, 0, ksize=5)', variable=set_Sobel_x, onvalue=1, offvalue=0)
    cb_Sobel_y = tk.Checkbutton(top, text='Spbel(img, CV_64F, 0, 1, ksize=5)', variable=set_Sobel_y, onvalue=1, offvalue=0)
    cb_Laplacian = tk.Checkbutton(top, text='Laplacian(img, CV_64F)', variable=set_Laplacian, onvalue=1, offvalue=0)
    tx_kernel = tk.Label(top, text='kernel = getStructuringElement(MORPH_RECT, (5,5))')
    cb_erode = tk.Checkbutton(top, text='erode(img, kernel, iterations=1)', variable=set_erode, onvalue=1, offvalue=0)
    cb_morphologyEx_OPEN = tk.Checkbutton(top, text='morphologyEx(img, MORPH_OPEN, kernel)', variable=set_morphologyEx_OPEN, onvalue=1, offvalue=0)
    cb_morphologyEx_CLOSE = tk.Checkbutton(top, text='morphologyEx(img, MORPH_CLOSE, kernel)', variable=set_morphologyEx_CLOSE, onvalue=1, offvalue=0)
    tx_gray_img = tk.Label(top, text='gray_img = cvtColor(img, COLOR_BGR2GRAY)')
    tx_threshold_img = tk.Label(top, text='_, threshold_img = threshold(gray_img, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)')
    tx_contours = tk.Label(top, text='contours, _ = findContours(threshold_img, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)')
    cb_drawContour = tk.Checkbutton(top, text='drawContours(img, contours, -1, (0, 255, 0), 3)', variable=set_drawContour, onvalue=1, offvalue=0)

    '''布局'''
    cb_cv2test.place(x=700, y=10)
    cb_cvtColorGARY.place(x=700, y=30)
    cb_cvtColorHSV.place(x=700, y=50)
    cb_cvtColorYUV.place(x=700, y=70)
    cb_GaussianBlur.place(x=700, y=90)
    cb_blur.place(x=700, y=110)
    cb_medianBlur.place(x=700, y=130)
    cb_Canny.place(x=700, y=150)
    cb_Sobel_x.place(x=700, y=170)
    cb_Sobel_y.place(x=700, y=190)
    cb_Laplacian.place(x=700, y=210)
    tx_kernel.place(x=700, y=230)
    cb_erode.place(x=700, y=250)
    cb_morphologyEx_OPEN.place(x=700, y=270)
    cb_morphologyEx_CLOSE.place(x=700, y=290)
    tx_gray_img.place(x=700, y=310)
    tx_threshold_img.place(x=700, y=330)
    tx_contours.place(x=700, y=350)
    cb_drawContour.place(x=700, y=370)

    # 保存图像对象，以防止被垃圾回收
    image_container = None

    top.after(33, update_frame())  # 启动定时器
    top.mainloop()  # 释放摄像头
    cap.release()
