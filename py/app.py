import os
import sys
import time
from configparser import ConfigParser
import cv2
import numpy as np

CFG = ConfigParser()
CFG.read('config.ini')
with open('config.ini', 'w') as f:
    CFG.write(f)

if 'adb' in globals():
    def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        s = sep.join(map(str, objects)) + end
        if file is sys.stdout or file is sys.stderr:
            adb.log(s)
        else:
            file.write(s)
            if flush:
                file.flush()

class imgOper(object):
    def __init__(self, origin_path):
        super().__init__()
        self.height, self.width = map(int, CFG['ui']['window_size'].split('x', 1))
        self.origin_path = origin_path
        self.img = cv2.imread(self.origin_path)

    def crop(self, save_path) -> None:
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.height, self.width)
        self.point1 = self.point2 = (0, 0)
        cv2.setMouseCallback('image', self.__on_mouse)
        cv2.imshow('image', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite(save_path, self.cut_img)

    def __on_mouse(self, event, x, y, flags, param) -> None:
        img2 = self.img.copy()
        if event == cv2.EVENT_LBUTTONDOWN:
            self.point1 = (x, y)
            cv2.circle(img2, self.point1, 10, (255, 0, 0), 5)
            cv2.imshow('image', img2)

        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
            cv2.rectangle(img2, self.point1, (x, y), (0, 255, 0), thickness=2)
            cv2.imshow('image', img2)

        elif event == cv2.EVENT_LBUTTONUP:
            self.point2 = (x, y)
            cv2.rectangle(img2, self.point1, self.point2, (0, 0, 255), thickness=2)
            cv2.imshow('image', img2)
            if self.point1 != self.point2:
                min_x = min(self.point1[0], self.point2[0])
                min_y = min(self.point1[1], self.point2[1])
                width = abs(self.point1[0] - self.point2[0])
                height = abs(self.point1[1] - self.point2[1])
                self.cut_img = self.img[min_y:min_y + height, min_x:min_x + width]
                cv2.imshow('ROI', self.cut_img)

    def sift(self, template_path: str): # -> Tuple[Tuple[int, int], Tuple[int, int]]
        sift = cv2.SIFT_create()
        template = cv2.imread(template_path)
        template_height, template_width = template.shape[:2]
        keypoint1, descriptor1 = sift.detectAndCompute(template, None)
        t0=time.time()#########检查下列语句运行时间#########
        keypoint2, descriptor2 = sift.detectAndCompute(self.img, None)
        print(time.time()-t0)###############################

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptor1, descriptor2, k=2)
        good = [[m] for m, n in matches if m.distance < 0.75 * n.distance]
        # 如果好点个数不到4个，将无法取得变换矩阵，因此提前返回。
        if len(good) < 6:
            return (0, 0), (0, 0)
        list_kp1 = np.reshape([keypoint1[m.queryIdx].pt for [m] in good], (-1, 1, 2))
        list_kp2 = np.reshape([keypoint2[m.trainIdx].pt for [m] in good], (-1, 1, 2))
        quad = cv2.perspectiveTransform(np.float32([
            [0, 0], [0, template_height - 1],
            [template_width - 1, template_height - 1], [template_width - 1, 0]
        ]).reshape(-1, 1, 2), cv2.findHomography(list_kp1, list_kp2, cv2.RANSAC, 5.0)[0])

        #cv2.namedWindow('BFmatch', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('BFmatch', self.height, self.width)
        #cv2.imshow('BFmatch', cv2.drawMatchesKnn(template, keypoint1, self.img, keypoint2, good, None, flags=2))
        #cv2.waitKey(0)

        return (int(min(quad[:, 0, 0])), int(min(quad[:, 0, 1]))), (int(max(quad[:, 0, 0])), int(max(quad[:, 0, 1])))

#img = ADB.screenshot()
#cv2.imwrite('F10.png', img)

#img = cv2.imread('F9.png')
#IMG = imgOper('F9.png')
#IMG.crop('b.png')
#print(IMG.sift('b.png'))

#ImgO = imgOper('F9.png')
#b, g, ImgO.img = cv2.split(ImgO.img)
#ImgO.img = cv2.resize(ImgO.img, (ImgO.img.shape[1] * 480 // ImgO.img.shape[0], 480), interpolation=cv2.INTER_LINEAR)
# 真正的计算机图形学家不需要imshow，都是用print看图像的。
#cv2.imshow('wtf ok it works', cv2.imread('F9.png'))



import prts

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
            level = prts.read_level("level_main_01-07.json")
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

#point = ImgO.sift('r.png')
#cv2.rectangle(ImgO.img, point[0], point[1], (192, 192, 192), thickness=2)
#cv2.imshow('矩形', ImgO.img)
#cv2.waitKey(0)

#cv2.namedWindow('image', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('image', ImgO.height, ImgO.width)
#cv2.imshow('image', ImgO.img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
