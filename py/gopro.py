"""狂暴猎狗组长，为某个品牌的监控设备代言。
*只是作为监控设备，会不会太奢侈了？*

保存不属于其他模块的函数。
最终本文件一定会演变成堆放杂物的地方，正如每个项目里一定会有的名为Util的类或模块一样。

文件名是因为敌人“猎狗”的内部标识符是enemy_1000_gopro。
"""

import numpy as np
import cv2

def resize(img, height, **kwargs):
    """根据目标高度，锁定原图比例缩放。"""
    return cv2.resize(img, (img.shape[1] * height // img.shape[0], height), **kwargs)

def video_between_two(video_filename, img0, img1):
    """创建对比两张图的视频。"""
    if img0.shape[:2] != img1.shape[:2]:
        raise ValueError("两个图的大小怎么不一样啊？")
    height, width = img0.shape[:2]
    video = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*"avc1"), 60, (width, height))
    for x in range(0, width, width // 500):
        video.write(np.hstack((img0[:, :x], img1[:, x:])))
    video.release()

def line_line_intersection(a0, b0, a1, b1):
    """求两直线a0 -- b0和a1 -- b1的交点，各点以元组给出，共计八个数值。"""
    A0 = b0[1] - a0[1]
    B0 = a0[0] - b0[0]
    C0 = a0[0] * A0 + a0[1] * B0
    A1 = b1[1] - a1[1]
    B1 = a1[0] - b1[0]
    C1 = a1[0] * A1 + a1[1] * B1
    det = A0 * B1 - A1 * B0
    if abs(det) > 1e-8:
        return (C0 * B1 - C1 * B0) / det, (C1 * A0 - C0 * A1) / det
    else:
        return None

def average_nearby_numbers(array, threshold):
    """合并列表中相近的数值簇。

    例如，[1, 1, 4, 5, 1, 4, 1, 9, 1, 9, 8, 1, 0]在阈值略超过1时的结果是[6/7、4 1/3、8 2/3]。
    """
    if len(array) == 0:
        return []
    cluster = []
    retval = []
    for x in np.sort(array):
        if len(cluster) != 0 and x - cluster[0] >= threshold:
            retval.append(np.mean(cluster))
            cluster = [x]
        else:
            cluster.append(x)
    retval.append(np.mean(cluster))
    return retval

def p_hash(img):
    """OpenCV pHash的Python再实现。"""
    dct = cv2.dct(cv2.cvtColor(cv2.resize(img, (32, 32), interpolation=cv2.INTER_LINEAR_EXACT), cv2.COLOR_BGR2GRAY).astype(np.float32))[:8, :8]
    dct[0, 0] = 0
    return cv2.compare(dct, float(np.mean(dct)), cv2.CMP_GT) // 255

def color_moment_hash(img):
    """OpenCV颜色矩散列的Python再实现。"""
    img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img, (3, 3), 0, 0)
    return np.ravel([
        cv2.HuMoments(cv2.moments(channel))
        for code in [cv2.COLOR_BGR2HSV, cv2.COLOR_BGR2YCrCb]
        for channel in cv2.split(cv2.cvtColor(img, code))
    ])
