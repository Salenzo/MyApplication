import os
import math
import time
import cv2
import numpy as np

# 保留测试用
def aaa(a):
    return a + cv2.__version__

def main(service):
    while True:
        service.swipe(400,1000,400,400,0.05)
        service.screenshot() # 可能返回None，如果不是空那应该是个数组吧，我也不知道具体是什么
        time.sleep(0.5)
