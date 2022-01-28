import os
import sys
import ctypes
import builtins
import traceback
import cv2
import numpy as np
preloaded_modules = set(sys.modules.keys()) | {"infamous_recidivist_service"}

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

# main函数可能在不重启Python解释器的情况下反复执行，务必注意所做工作应可重复。
# service是InfamousRecidivistService实例。
def main(service):
    # 注入服务对象到模块缓存字典，以便用户代码import infamous_recidivist_service。
    sys.modules["infamous_recidivist_service"] = service
    # 保证目标脚本在搜索路径中，以便其调用周围的模块文件。
    path = os.path.join(os.environ["HOME"], "py")
    if path not in sys.path: sys.path.insert(0, path)
    # 帮进程改变工作目录，以便脚本读取周围的数据文件。
    # Java侧受多线程概念根植影响，没有工作目录一说。
    os.chdir(path)
    # 替换被用烂的输出函数，以便脚本在电脑和手机上都能正常运行。
    builtins.print = redirected_print
    cv2.imshow = service.imshow
    # 执行目标脚本。
    code = open("app.py").read()
    try:
        # 必须传入全局变量字典，否则exec在当前上下文执行代码。
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
