"""多线程实现"""


import threading


def threadIt(func, *args):
    """创建线程"""
    t = threading.Thread(target=func, args=args)
    # 守护线程
    t.setDaemon(True)
    # 启动
    t.start()
