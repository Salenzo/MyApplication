import cv2
from app.config import cfg
from app.img import imgOper

PATH = "./config.ini"

#import cv2
#ADB = ADBClient()
#img = ADB.screenshot()
#cv2.imwrite('./app/img/F10.png', img)

#img = cv2.imread('./app/img/F9.png')
#IMG = imgOper(PATH, './app/img/F9.png')
#IMG.crop('./app/template/b.png')
#print(IMG.sift('./app/template/b.png'))

ImgO = imgOper(PATH, './app/img/F9.png')
b, g, ImgO.img = cv2.split(ImgO.img)
#ret, ImgO.img = cv2.threshold(ImgO.img, 150, 255, cv2.THRESH_BINARY)
point = ImgO.sift('./app/template/a.png')
cv2.circle(ImgO.img, point, 100, (255, 255, 255), 10)
print(point)

#cv2.namedWindow('image', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('image', ImgO.height, ImgO.width)
#cv2.imshow('image', ImgO.img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
