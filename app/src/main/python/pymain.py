import os
import sys
import ctypes
import builtins
import traceback
import cv2
import numpy as np
preloaded_modules = set(sys.modules.keys()) | {"infamous_recidivist_service"}

# 保留测试用
def aaa(a):
    return a + cv2.__version__

def kill_thread(tid):
    tid = ctypes.c_long(tid)
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
    if ret != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
    return ret

def convert_jarray_to_cv2(a, width, height):
    return cv2.cvtColor(np.array(a, dtype=np.uint8).reshape(height, width, 4), cv2.COLOR_BGRA2RGB)

def convert_cv2_to_1darray(a):
    return cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2BGRA).flatten()

def redirected_print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
    s = sep.join(map(str, objects)) + end
    if file is sys.stdout or file is sys.stderr:
        sys.modules["infamous_recidivist_service"].log(s)
    else:
        file.write(s)
        if flush: file.flush()

def main(service):
    # 保证目标脚本在搜索路径中，以便其调用周围的模块文件。
    path = os.path.join(os.environ["HOME"], "py")
    sys.modules["infamous_recidivist_service"] = service
    if path not in sys.path: sys.path.insert(0, path)
    cv2.imshow = service.imshow
    builtins.print = redirected_print
    os.chdir(path)
    code = open("app.py").read()
    try:
        exec(code, {})
    except SystemExit:
        pass
    except Exception as e:
        with open("app.py", "w") as f:
            f.write("r\"\"\"" + traceback.format_exc().replace("\"\"\"", "\\\"\"\"") + "\n\"\"\"\n\n" + code)
        service.log(f"发生了异常{e}。", 16)
    # 卸载由exec之代码新加载的模块，以便热更新。
    for key in set(sys.modules.keys()) - preloaded_modules:
        del sys.modules[key]
