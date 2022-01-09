import os
import sys
import math
import ctypes
import traceback
from queue import Queue
from io import TextIOBase
from java.android.stream import BytesOutputWrapper

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

real_stdout = sys.stdout
real_stderr = sys.stderr

class ConsoleOutputStream(TextIOBase):
    def __init__(self, service, stream, style):
        self.stream = stream
        self.service = service
        self.style = style
        self.buffer = BytesOutputWrapper(self)

    def __repr__(self):
        return f"<ConsoleOutputStream {self.stream}>"

    @property
    def encoding(self):
        return self.stream.encoding

    @property
    def errors(self):
        return self.stream.errors

    def writable(self):
        return self.stream.writable()

    def write(self, s):
        # Pass the write to the underlying stream first, so that if it throws an exception,
        # the app crashes in the same way whether it's using ConsoleOutputStream or not (chaquo/chaquopy #5712).
        result = self.stream.write(s)
        if len(s) > 0:
            self.service.log(s, self.style)
        return result

    def flush(self):
        self.stream.flush()

def main(service):
    try:
        #import time
        #while True:
        #    adb.swipe(400,1000,400,400,0.05)
        #    adb.screenshot() # 可能返回None，如果不是空那应该是个数组吧，我也不知道具体是什么
        #    time.sleep(0.5)
        sys.stdout = ConsoleOutputStream(service, real_stdout, 1)
        sys.stderr = ConsoleOutputStream(service, real_stderr, 2)
        exec(open(os.path.join(os.environ["HOME"], "more.py")).read(), {"adb": service})
    except SystemExit:
        pass
    except Exception as e:
        with open(os.path.join(os.environ["HOME"], "more.py"), "w") as f:
            f.write("r\"\"\"" + traceback.format_exc().replace("\"\"\"", "\\\"\"\"") + "\n\"\"\"")
    sys.stdout = real_stdout
    sys.stderr = real_stderr
    service.log("Python止步于此。", 16)
