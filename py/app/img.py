import cv2
from app.config import cfg
import numpy as np
import time

class imgOper(object):
    def __init__(self, path, origin_path) -> None:
        super().__init__()
        CFG = cfg(path)
        h, w = CFG.read('ui', 'window_size').split('x', 1)

        self.origin_path = origin_path
        self.height = int(h)
        self.width = int(w)
        self.point1 = (0, 0)
        self.point2 = (0, 0)

        self.img = cv2.imread(self.origin_path)

    def crop(self, save_path) -> None:
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.height, self.width)
        while True:
            cv2.setMouseCallback('image', self.__on_mouse)
            cv2.imshow('image', self.img)
            key = cv2.waitKey(0)
            if key is not None:
                break
        cv2.destroyAllWindows()
        try:
            cv2.imwrite(save_path, self.cut_img)
        except Exception as err:
            print(err)

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
            cv2.rectangle(img2, self.point1, self.point2,
                          (0, 0, 255), thickness=2)
            cv2.imshow('image', img2)
            if self.point1 != self.point2:
                min_x = min(self.point1[0], self.point2[0])
                min_y = min(self.point1[1], self.point2[1])
                width = abs(self.point1[0] - self.point2[0])
                height = abs(self.point1[1] - self.point2[1])
                cut_img = self.img[min_y:min_y + height, min_x:min_x + width]
                self.cut_img = cut_img
                cv2.imshow('ROI', cut_img)

    def sift(self, template_path):
        sift = cv2.SIFT_create()
        template = cv2.imread(template_path)
        height, width = self.img.shape[:2]
        img = cv2.resize(self.img, (width * 480 // height, 480), interpolation = cv2.INTER_LINEAR)
        keypoint1, descriptor1 = sift.detectAndCompute(template, None)
        t0=time.time()#########检查下列语句运行时间#########
        keypoint2, descriptor2 = sift.detectAndCompute(img, None)
        print(time.time()-t0)###############################

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptor1, descriptor2, k=2)
        good = [[m] for m, n in matches if m.distance < 0.75 * n.distance]
        print('matched' if len(good) > 5 else 'template not matched')
        list_kp1 = [keypoint1[m.queryIdx].pt for [m] in good]
        list_kp2 = [keypoint2[m.trainIdx].pt for [m] in good]
        X = np.median([pt[0] for pt in list_kp2])
        Y = np.median([pt[1] for pt in list_kp2])

        cv2.namedWindow('BFmatch', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('BFmatch', self.height, self.width)
        cv2.imshow('BFmatch', cv2.drawMatchesKnn(template, keypoint1, img, keypoint2, good, None, flags=2))
        cv2.waitKey(0)

        return int(X), int(Y)
