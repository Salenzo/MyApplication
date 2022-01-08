import os
import sys
import math
import time
import cv2
import ctypes
import numpy as np

# 保留测试用
def aaa(a):
    return a + cv2.__version__

def kill_thread(tid):
    tid = ctypes.c_long(tid)
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    if ret != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
    print("kill_thread = " + str(ret))
    return ret

def main(service):
    with open(os.path.join(os.environ["HOME"], "more.py"), "w") as f:
        f.write("while True:\n    adb.swipe(400,1000,400,400,0.05)\n    time.sleep(0.5)")
    try:
        #while True:
        #    service.swipe(400,1000,400,400,0.05)
        #    service.screenshot() # 可能返回None，如果不是空那应该是个数组吧，我也不知道具体是什么
        #    time.sleep(0.5)
        exec("import time\nwhile True:\n    adb.swipe(400,1000,400,400,0.05)\n    time.sleep(0.5)", {"adb": service})
    except SystemExit:
        pass
