import os
import sys
import math
import ctypes
import traceback

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
    try:
        #import time
        #while True:
        #    adb.swipe(400,1000,400,400,0.05)
        #    adb.screenshot() # 可能返回None，如果不是空那应该是个数组吧，我也不知道具体是什么
        #    time.sleep(0.5)
        exec(open(os.path.join(os.environ["HOME"], "more.py")).read(), {"adb": service})
    except SystemExit:
        pass
    except Exception as e:
        with open(os.path.join(os.environ["HOME"], "more.py"), "w") as f:
            f.write("\"\"\"" + traceback.format_exc() + "\"\"\"")
