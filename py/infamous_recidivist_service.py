# 这个文件没什么用，纯粹是为了让不识时务的编辑器闭嘴的。

def tap(x: float, y: float) -> None:
    """模拟点击。
    - 不阻塞，操作固定定时20毫秒。
    - 打断当前正在执行的其他触摸操作。
    - 其实是在指定点附近两像素区域内滑动。
    """
    pass

def swipe(x0: float, y0: float, x1: float, y1: float, duration: float) -> None:
    """模拟直线滑动。
    - 不阻塞，duration单位为秒。
    - 打断当前正在执行的其他触摸操作。
    - Android 11及以后才能流畅模拟，早期版本的系统高傲地以为100毫秒的采样周期能满足所有人的需求。
    """
    pass

def screenshot():
    """截取屏幕。
    如果没有权限，或者画面距上次截图以来没有变化，或者还没来得及截到最新一张图，返回None。成功截到的话，返回的是适合cv2直接处理的图像。
    - 目前固定分辨率1920 × 1080。
    """
    import cv2
    return cv2.imread("F9.png")

def log(object) -> None:
    """在迫真控制台中打印信息。
    迫真控制台只能显示最近的一行文本，没有任何滚屏手段。"""
    print(object)
