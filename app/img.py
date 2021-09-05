import cv2
from app.config import cfg

PATH = './config.ini'


class image(object):
    def __init__(self, origin_path, threshold) -> None:
        super().__init__()
        CFG = cfg(PATH)
        h, w = CFG.read('ui', 'window_size').split('x', 1)

        self.origin_path = origin_path
        self.threshold = threshold
        self.height = int(h)
        self.width = int(w)
        self.point1 = (0, 0)
        self.point2 = (0, 0)

        self.refresh()

    def refresh(self) -> None:
        img = cv2.imread(self.origin_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, self.img = cv2.threshold(
            img, self.threshold, 255, cv2.THRESH_BINARY)

    def crop(self, save_path) -> None:
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.height, self.width)
        while True:
            cv2.setMouseCallback('image', self.__on_mouse)
            cv2.imshow('image', self.img)
            key = cv2.waitKey(0)
            if key is not None:
                break
        cv2.descriptortroyAllWindows()
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
        img = self.img
        keypoint1, descriptor1 = sift.detectAndCompute(template, None)
        keypoint2, descriptor2 = sift.detectAndCompute(img, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptor1, descriptor2, k=2)

        good = []
        for m, n in matches:
            if m.distance < 0.90 * n.distance:
                good.append([m])

        if len(good) > 20:
            print('template matched')
        else:
            print('template not matched')

        img5 = cv2.drawMatchesKnn(
            template,
            keypoint1,
            img,
            keypoint2,
            good,
            None,
            flags=2)
        # TODO get the roi region from the matches and return
        cv2.namedWindow('BFmatch', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('BFmatch', self.height, self.width)
        cv2.imshow('BFmatch', img5)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
