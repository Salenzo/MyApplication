import os
import math
import time
import cv2
import numpy as np
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from app.config import cfg

PATH = './config.ini'


class ADBClient(object):
    def __init__(self):
        super().__init__()
        CFG = cfg(PATH)
        self.device = AdbDeviceTcp(
            CFG.read(
                'network', 'ip'), CFG.read(
                'network', 'port'))
        key_path = "adb.local.key"
        if not os.path.isfile(key_path):
            keygen(key_path)
        self.device.connect(
            rsa_keys=[
                PythonRSASigner.FromRSAKeyPath(key_path)])

    def __del__(self):
        self.device.close()

    def screenshot(self):
        img_data = self.device.shell(
            "screencap", decode=False, transport_timeout_s=None)
        width = int.from_bytes(img_data[0:4], "little")
        height = int.from_bytes(img_data[4:8], "little")
        pixel_format = int.from_bytes(img_data[8:12], "little")
        assert pixel_format == 1, "Unsupported pixel format: %s" % pixel_format
        return cv2.cvtColor(np.frombuffer(img_data, np.uint8)[12:(
            width * height * 4 + 12)].reshape(height, width, 4), cv2.COLOR_BGRA2RGB)

    def tap(self, x, y):
        print("ADB.tap(%.0f, %.0f)" % (x, y))
        res = self.device.shell(f"input tap {x} {y}")
        assert not res, res
        time.sleep(0.5)

    def swipe(self, x1, y1, x2, y2, duration):
        print("ADB.swipe(%.0f, %.0f, %.0f, %.0f, %g)" %
              (x1, y1, x2, y2, duration))
        duration_ms = max(200, int(duration * 1000))
        res = self.device.shell(
            f"input swipe {x1} {y1} {x2} {y2} {duration_ms}", read_timeout_s=10 + duration)
        assert not res, res
        time.sleep(0.5)

    def __on_mouse(self, event, x, y, flags, param):
        img2 = self.img.copy()
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x0, self.y0 = x, y
            cv2.circle(img2, (x, y), 10, (128, 255, 0), 5)
            cv2.imshow('fig', img2)
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
            cv2.line(img2, (self.x0, self.y0), (x, y),
                     (255, 128, 0), thickness=2)
            cv2.imshow('fig', img2)
        elif event == cv2.EVENT_LBUTTONUP:
            self.x1, self.y1 = x, y
            cv2.destroyAllWindows()

    def run(self):
        while self.__run():
            pass

    def __run(self):
        self.img = self.screenshot()
        self.x0 = self.y0 = self.x1 = self.y1 = -999
        cv2.namedWindow('fig', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow('fig', self.img)
        cv2.setMouseCallback('fig', self.__on_mouse)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        if self.x0 == -999:
            return False
        if math.hypot(self.x0 - self.x1, self.y0 - self.y1) < 10:
            self.tap(self.x0, self.y0)
        else:
            self.swipe(self.x0, self.y0, self.x1, self.y1, 1)
        return True
