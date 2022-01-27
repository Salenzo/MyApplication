import sys
import time
import json
import cv2
import numpy as np
import prts

if 'adb' in globals():
    def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        s = sep.join(map(str, objects)) + end
        if file is sys.stdout or file is sys.stderr:
            adb.log(s)
        else:
            file.write(s)
            if flush:
                file.flush()

def screenshot(drop_count = 0):
    while True:
        img = adb.screenshot()
        if img is not None:
            if drop_count > 0:
                drop_count -= 1
            else:
                return img

def adb_main():
    if adb.screenshot() is None:
        print("第一张图就是None，是不是没开截图权限？")
        return
    # 等待战斗界面完成加载，以费用标志出现且费用条开始走动为准。
    print("Polling till in battle.")
    img = screenshot()
    if prts.in_battle(img):
        print("第一章图在战斗中，恕我无法提供服务。")
        return
    while True:
        img = screenshot()
        if prts.in_battle(img) and 1 / 30 <= prts.fractional_cost(img) <= 29 / 30:
            break
    action_sequence = {
        # 0：第一帧操作（肯定来不及，同代理指挥一样在第一次来得及的时候操作）
        # 1：干员条中第二个干员
        # 4：放之前干员条中共四个干员
        # 2：行号（0起）
        # 7：列号（0起）
        # R：朝向，U/D/L/R
        0: (1, 4, 2, 7, "R"),
        30 * 19 + 1: (1, 3, 3, 1, "R"),
        30 * 30: (0, 2, 5, 8, "L"),
    }
    frame = 0
    perspective = None
    width, height = 1920, 1080 # 无障碍那边暂时没写多分辨率，待做！
    while True:
        img = screenshot()
        if not prts.in_battle(img):
            break
        # 初次运行到此处时插入一段估计透视的程序。
        if perspective is None:
            print("估计透视：数据采集之子弹时间。")
            # 点击干员的动画效果播放约¼秒。
            img0 = img
            adb.tap(width - 8, height - 8)
            time.sleep(0.4)
            img1 = screenshot()
            print("估计透视：数据采集之暂停。")
            adb.tap(width - height // 12, height // 12)
            time.sleep(0.2)
            img2 = screenshot()
            time.sleep(0.4)
            img3 = screenshot()
            adb.tap(width - 8, height - 8)
            adb.tap(width - height // 12, height // 12)
            print("估计透视：图像处理。")
            with open("level_main_01-07.json") as f:
                level = prts.level_map(json.load(f))
            perspective, bullet_time_homography = prts.Perspective(level, img0, img1, img2, img3, 1)
            prts.draw_reseau(img0, perspective, level.shape)
        # 认为延迟不会超过29帧。
        delta_frame = (round(prts.fractional_cost(img) * 30) - frame) % 30
        if delta_frame:
            frame += delta_frame
        else:
            continue
        print(f"处理帧. 当前时间：{frame/30=:.2f}")
        for i in action_sequence.keys():
            if i < frame:
                nn, n, row, col, direction = action_sequence[i]
                del action_sequence[i]
                x, y = np.int32(cv2.perspectiveTransform(cv2.perspectiveTransform(np.float32([[[col + 0.5, row + 0.5]]]), perspective), bullet_time_homography))[0, 0]
                adb.swipe(prts.operator_xs((width, height), n, None)[nn] + 8, height - 8, x, y, 0.6)
                cv2.line(img1, (int(prts.operator_xs((width, height), n, None)[nn] + 8), height - 8), (x, y), [255,i//8,255], 3)
                time.sleep(0.8)
                adb.swipe(x, y, {
                    "U": x,
                    "D": x,
                    "L": x - height // 4,
                    "R": x + height // 4,
                }[direction], {
                    "U": y - height // 4,
                    "D": y + height // 4,
                    "L": y,
                    "R": y,
                }[direction], 0.3)
                time.sleep(0.5)
                break
    cv2.imshow("", img1)
    print("结束。")
if "adb" in globals():
    adb_main()
else:
    print("要传到手机上运行。")
