import cv2
from config import cfg

PATH = './config.ini'

class image(object):
    def __init__(self, origin_path, save_path, threshold) -> None:
        super().__init__()
        CFG = cfg(PATH)
        h, w = CFG.read('ui', 'window_size').split('x', 1)

        img = cv2.imread(origin_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, self.img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        self.save_path = save_path
        self.height = h
        self.width = w
        self.point1 = (0, 0)
        self.point2 = (0, 0)
        self.cut_img = None

    def get_image_roi(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.width, self.height)
        while True:
            cv2.setMouseCallback('image', self.__on_mouse)
            cv2.imshow('image', self.img)
            key = cv2.waitKey(0)
            if key != None:
                break
        cv2.destroyAllWindows()
        try:
            cv2.imwrite(self.save_path, self.cut_img)
        except Exception as err:
            print(err)

    def __on_mouse(self, event, x, y, flags, param):
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
