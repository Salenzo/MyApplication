import os
import time
from configparser import ConfigParser
import cv2
import numpy as np
import hsv

CFG = ConfigParser()
CFG.read('config.ini')
with open('config.ini', 'w') as f:
    CFG.write(f)

if 'adb' in globals():
    def print(x):
        adb.log(x)

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

    def sift(self, template_path: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
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

ImgO = imgOper('F9.png')
b, g, ImgO.img = cv2.split(ImgO.img)
ImgO.img = cv2.resize(ImgO.img, (ImgO.img.shape[1] * 480 // ImgO.img.shape[0], 480), interpolation=cv2.INTER_LINEAR)
#ret, ImgO.img = cv2.threshold(ImgO.img, 150, 255, cv2.THRESH_BINARY)
((x0, x1), (y0, y1)) = ImgO.sift('a.png')
((_, y2), (_, _)) = ImgO.sift('r.png')
x0 = x0 - 3
cost = []
for y in range(y1 + 1, y2):
    # 真正的计算机图形学家不需要imshow，都是用print看图像的。
    print(''.join(map(lambda x: '1' if x >= 224 else '0', ImgO.img[y, x0 - 3:])))
    transitions = np.where(np.diff(ImgO.img[y, x0:] + [0] >= 224))[0]
    if len(transitions) > 1:
        cost.append((transitions[1] - transitions[0]) / (ImgO.img.shape[1] - transitions[0] - x0))
cost = 0.0 if len(cost) == 0 else np.median(cost)


print(f'Cost = ?{cost}')
print(hsv.hsv())
#point = ImgO.sift('r.png')
#cv2.rectangle(ImgO.img, point[0], point[1], (192, 192, 192), thickness=2)
#cv2.imshow('矩形', ImgO.img)
#cv2.waitKey(0)

#cv2.namedWindow('image', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('image', ImgO.height, ImgO.width)
#cv2.imshow('image', ImgO.img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
