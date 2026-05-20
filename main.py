"""
OpenCV 算子效果预览工具（自适应布局版）

- 左侧：摄像头实时预览，随窗口大小自动缩放
- 右侧：算子勾选区（可滚动）
    * 红色区：互斥算子（改变图像通道 / 数据类型 / 颜色空间），同时仅能启用一个
    * 绿色区：可叠加算子（保持图像形状），可任意组合
- 每个有参数的算子右侧会自动渲染输入框，实时生效；非法输入回退默认值
"""

import cv2
import tkinter as tk
from tkinter import Canvas, Label
from tkinter import ttk
from PIL import Image, ImageTk

import cv2Func


# 视频捕获
cap = cv2.VideoCapture(0)


class OperatorPanel:
    """单个算子的 UI 面板：复选框 + 参数输入框"""

    def __init__(self, parent, op):
        self.op = op
        self.var = tk.IntVar(value=0)
        self.param_vars = {}  # name -> (StringVar, type, default)

        self.frame = tk.Frame(parent)

        # 复选框
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


def build_scrollable_area(parent):
    """在 parent 中构建可滚动区域，返回内层 Frame（用于填充子控件）"""
    sc = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
    vsb = tk.Scrollbar(parent, orient='vertical', command=sc.yview)
    sc.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    sc.pack(side='left', fill='both', expand=True)

    inner = tk.Frame(sc)
    win_id = sc.create_window((0, 0), window=inner, anchor='nw')

    # 内容变化时更新滚动区域
    def _on_inner_configure(_e):
        sc.configure(scrollregion=sc.bbox('all'))

    # 滚动画布宽度跟随容器宽度变化
    def _on_sc_configure(e):
        sc.itemconfig(win_id, width=e.width)

    inner.bind('<Configure>', _on_inner_configure)
    sc.bind('<Configure>', _on_sc_configure)

    # 鼠标滚轮仅在悬停区域内有效
    def _on_mousewheel(e):
        sc.yview_scroll(int(-e.delta / 120), 'units')

    sc.bind('<Enter>', lambda _e: sc.bind_all('<MouseWheel>', _on_mousewheel))
    sc.bind('<Leave>', lambda _e: sc.unbind_all('<MouseWheel>'))

    return inner


def build_ui(top):
    """构建自适应布局 UI，返回 (canvas, panels)"""

    # === 主窗口网格权重 ===
    # 列 0（左/视频区）随窗口扩张，列 1（右/算子区）保持最小宽度并适度扩张
    top.columnconfigure(0, weight=3, minsize=300)
    top.columnconfigure(1, weight=1, minsize=420)
    top.rowconfigure(0, weight=1)

    # ----------------------------------------------------------------
    # 左侧：标题 + 视频画布 + 提示文字
    # ----------------------------------------------------------------
    left_frame = tk.Frame(top)
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(1, weight=1)   # 画布行随高度扩张

    Label(left_frame, text='OpenCV 算子效果预览', font=("黑体", 16)).grid(
        row=0, column=0, sticky='nw', pady=(0, 6))

    video_canvas = Canvas(left_frame, bg='#1e1e1e', cursor='crosshair')
    video_canvas.grid(row=1, column=0, sticky='nsew')

    tip = (
        '使用说明：\n'
        '① 标 [互斥] 的算子会改变图像通道 / 颜色空间，同一时刻只能启用一个，\n'
        '   开启新的互斥算子时会自动关闭当前互斥算子。\n'
        '② 其余「可叠加算子」可任意组合，按列表顺序依次作用于画面。\n'
        '③ 修改参数输入框后实时生效，参数非法时自动回退默认值。'
    )
    Label(left_frame, text=tip, fg='steelblue', justify='left',
          font=("微软雅黑", 10)).grid(row=2, column=0, sticky='nw', pady=(6, 0))

    # ----------------------------------------------------------------
    # 右侧：算子滚动列表
    # ----------------------------------------------------------------
    right_outer = tk.Frame(top, bd=1, relief='sunken')
    right_outer.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
    right_outer.columnconfigure(0, weight=1)
    right_outer.rowconfigure(1, weight=1)

    Label(right_outer, text='算子列表', font=("黑体", 13, 'bold'),
          anchor='w').grid(row=0, column=0, sticky='ew', padx=6, pady=(4, 2))
    ttk.Separator(right_outer, orient='horizontal').grid(
        row=0, column=0, sticky='ews', padx=4)

    scroll_host = tk.Frame(right_outer)
    scroll_host.grid(row=1, column=0, sticky='nsew')
    scroll_host.columnconfigure(0, weight=1)
    scroll_host.rowconfigure(0, weight=1)

    inner = build_scrollable_area(scroll_host)

    # ----------------------------------------------------------------
    # 填充算子面板
    # ----------------------------------------------------------------
    panels = []

    Label(inner, text='—— 互斥算子（同时仅能启用一个） ——',
          fg='red', font=("黑体", 10, 'bold')).pack(
        anchor='w', padx=4, pady=(6, 4))
    for op in cv2Func.OPERATORS:
        if op['exclusive']:
            panels.append(OperatorPanel(inner, op))

    tk.Frame(inner, height=2, bg='#cccccc').pack(fill='x', padx=4, pady=4)
    Label(inner, text='—— 可叠加算子（可任意组合） ——',
          fg='green', font=("黑体", 10, 'bold')).pack(
        anchor='w', padx=4, pady=(4, 4))
    for op in cv2Func.OPERATORS:
        if not op['exclusive']:
            panels.append(OperatorPanel(inner, op))

    # 互斥逻辑：开启一个互斥算子时，自动关闭其他互斥算子
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

    return video_canvas, panels


def make_tk_image(canvas, panels):
    """读取一帧，依次应用启用的算子，按画布实际大小缩放后返回 PhotoImage"""
    ret, frame = cap.read()
    if not ret:
        return None

    frame = cv2.flip(frame, 1)                          # 摄像头水平翻转
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    for p in panels:
        if not p.is_on():
            continue
        try:
            params = p.get_params()
            frame = p.op['func'](frame, **params)
        except Exception as e:
            print(f"[警告] 算子 {p.op['key']} 执行失败: {e}")

    # 读取画布当前尺寸（响应式缩放）
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 10 or h < 10:           # 窗口还未渲染时的安全回退
        w, h = 640, 480

    try:
        pil_image = Image.fromarray(frame)
    except Exception as e:
        print(f"[警告] 帧转换失败: {e}")
        return None

    pil_image = pil_image.resize((w, h), Image.LANCZOS)
    return ImageTk.PhotoImage(image=pil_image)


def update_frame(top, canvas, panels):
    """循环刷新画面（约 30 fps）"""
    pic = make_tk_image(canvas, panels)
    if pic is not None:
        canvas.create_image(0, 0, anchor='nw', image=pic)
        canvas.image = pic      # 持有引用，防止被 GC 回收
    top.after(33, update_frame, top, canvas, panels)


if __name__ == '__main__':
    top = tk.Tk()
    top.title('OpenCV 算子效果预览')
    top.geometry('1500x900')
    top.minsize(900, 600)       # 防止缩得太小导致布局混乱

    canvas, panels = build_ui(top)

    top.after(33, update_frame, top, canvas, panels)
    try:
        top.mainloop()
    finally:
        cap.release()
