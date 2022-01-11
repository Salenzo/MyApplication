import os
import ctypes
import traceback
import cv2
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

def convert_jarray_to_cv2(a, width, height):
    return cv2.cvtColor(np.array(a, dtype=np.uint8).reshape(height, width, 4), cv2.COLOR_BGRA2RGB)

def main(service):
    try:
        os.chdir(os.environ["HOME"])
        exec(open("app.py").read(), {"adb": service})
    except SystemExit:
        pass
    except Exception as e:
        with open("app.py", "w") as f:
            f.write("r\"\"\"" + traceback.format_exc().replace("\"\"\"", "\\\"\"\"") + "\n\"\"\"")
        service.log(f"发生了异常{e}。", 16)
