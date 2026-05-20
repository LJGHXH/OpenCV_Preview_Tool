"""
OpenCV 算子效果预览工具

- 左侧：摄像头实时预览（已应用所选算子）
- 右侧：算子勾选区
    * 红色区：互斥算子（改变图像通道 / 数据类型 / 颜色空间），同时仅能启用一个
    * 绿色区：可叠加算子（保持图像形状），可任意组合
- 每个有参数的算子右侧会自动渲染输入框，实时生效；非法输入回退默认值
"""

import cv2
import tkinter as tk
from tkinter import Canvas, Label
from PIL import Image, ImageTk

import cv2Func


# 视频捕获
cap = cv2.VideoCapture(0)

# 预览画布尺寸
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 500


class OperatorPanel:
    """单个算子的 UI 面板：复选框 + 参数输入框"""

    def __init__(self, parent, op):
        self.op = op
        self.var = tk.IntVar(value=0)
        self.param_vars = {}  # name -> (StringVar, type, default)

        self.frame = tk.Frame(parent)

        # 复选框（统一宽度，便于对齐）
        self.cb = tk.Checkbutton(
            self.frame, text=op['label'], variable=self.var,
            onvalue=1, offvalue=0, anchor='w', width=32
        )
        self.cb.grid(row=0, column=0, sticky='w')

        # 参数输入框
        col = 1
        for pname, default, ptype in op['params']:
            tk.Label(self.frame, text=pname + '=').grid(row=0, column=col, sticky='e')
            col += 1
            sv = tk.StringVar(value=str(default))
            entry_w = 10 if ptype == 'str' else 6
            tk.Entry(self.frame, textvariable=sv, width=entry_w).grid(
                row=0, column=col, padx=(0, 6))
            col += 1
            self.param_vars[pname] = (sv, ptype, default)

        # 互斥标记
        if op['exclusive']:
            tk.Label(self.frame, text='[互斥]', fg='red').grid(row=0, column=col)

        self.frame.pack(fill='x', anchor='w', padx=4, pady=1)

    def is_on(self):
        return self.var.get() == 1

    def set_on(self, v):
        self.var.set(1 if v else 0)

    def get_params(self):
        """读取参数输入框，转换类型；非法输入回退默认值"""
        result = {}
        for pname, (sv, ptype, default) in self.param_vars.items():
            text = sv.get()
            try:
                if ptype == 'int':
                    result[pname] = int(float(text))
                elif ptype == 'float':
                    result[pname] = float(text)
                else:
                    result[pname] = text
            except (ValueError, TypeError):
                result[pname] = default
        return result


def build_scrollable_area(parent, x, y, width, height):
    """在 parent 中放置可滚动的 Frame，返回内层 Frame"""
    container = tk.Frame(parent)
    container.place(x=x, y=y, width=width, height=height)

    canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
    vsb = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)

    inner = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner, anchor='nw')

    def _on_configure(_e):
        canvas.configure(scrollregion=canvas.bbox('all'))

    inner.bind('<Configure>', _on_configure)

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-e.delta / 120), 'units')

    # 当鼠标进入区域时绑定滚轮，离开时解绑（避免影响其他控件）
    canvas.bind('<Enter>', lambda _e: canvas.bind_all('<MouseWheel>', _on_mousewheel))
    canvas.bind('<Leave>', lambda _e: canvas.unbind_all('<MouseWheel>'))

    return inner


def build_ui(top):
    # 标题与画布
    Label(top, text='OpenCV 算子效果预览', font=("黑体", 16)).place(x=50, y=15)
    canvas = Canvas(top, bg='white', width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
    canvas.place(x=50, y=50)

    tip = (
        '使用说明：\n'
        '1. 标 [互斥] 的算子会改变图像通道 / 颜色空间 / 数据类型，\n'
        '   同一时刻只能启用一个，开启新的会自动关闭其他互斥算子。\n'
        '2. 其余「可叠加算子」可以任意组合，按列表顺序依次作用。\n'
        '3. 修改参数后会实时生效，参数非法时自动回退默认值。'
    )
    Label(top, text=tip, fg='blue', justify='left',
          font=("微软雅黑", 10)).place(x=50, y=560)

    # 右侧滚动算子区
    inner = build_scrollable_area(top, x=700, y=20, width=780, height=950)

    panels = []

    # 互斥算子
    Label(inner, text='—— 互斥算子（同时仅能启用一个） ——',
          fg='red', font=("黑体", 11)).pack(anchor='w', padx=4, pady=(6, 4))
    for op in cv2Func.OPERATORS:
        if op['exclusive']:
            panels.append(OperatorPanel(inner, op))

    # 可叠加算子
    Label(inner, text='—— 可叠加算子（可任意组合） ——',
          fg='green', font=("黑体", 11)).pack(anchor='w', padx=4, pady=(12, 4))
    for op in cv2Func.OPERATORS:
        if not op['exclusive']:
            panels.append(OperatorPanel(inner, op))

    # 互斥逻辑：开启某互斥算子时，关闭其他所有互斥算子
    def make_mutex_handler(p):
        def handler(*_args):
            if p.is_on() and p.op['exclusive']:
                for q in panels:
                    if q is not p and q.op['exclusive'] and q.is_on():
                        q.set_on(False)
        return handler

    for p in panels:
        if p.op['exclusive']:
            p.var.trace_add('write', make_mutex_handler(p))

    return canvas, panels


def make_tk_image(panels):
    """读取一帧并依次应用启用的算子"""
    ret, frame = cap.read()
    if not ret:
        return None

    frame = cv2.flip(frame, 1)  # 摄像头水平翻转，便于观察
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    for p in panels:
        if not p.is_on():
            continue
        try:
            params = p.get_params()
            frame = p.op['func'](frame, **params)
        except Exception as e:
            print(f"[警告] 算子 {p.op['key']} 执行失败: {e}")

    try:
        pil_image = Image.fromarray(frame)
    except Exception as e:
        print(f"[警告] 帧转换失败: {e}")
        return None

    pil_image = pil_image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)
    return ImageTk.PhotoImage(image=pil_image)


def update_frame(top, canvas, panels):
    """循环刷新画面"""
    pic = make_tk_image(panels)
    if pic is not None:
        canvas.create_image(0, 0, anchor='nw', image=pic)
        canvas.image = pic  # 保留引用，防止被回收
    top.after(33, update_frame, top, canvas, panels)


if __name__ == '__main__':
    top = tk.Tk()
    top.title('OpenCV 算子效果预览')
    top.geometry('1500x1000')

    canvas, panels = build_ui(top)

    top.after(33, update_frame, top, canvas, panels)
    try:
        top.mainloop()
    finally:
        cap.release()
