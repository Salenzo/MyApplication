import cv2
import numpy as np

img = cv2.imread('b1.png')
h, w = img.shape[:2]
bottom = img[int((1-37/216)*h):h, 0:w]#迫真调参
gray = cv2.cvtColor(bottom,cv2.COLOR_BGR2GRAY)
h, w = gray.shape[:2]
tagArea = gray[int(0.025*h):int(0.20*h),] 
ret,thresh = cv2.threshold(tagArea,127,255,cv2.THRESH_BINARY)

print(np.where(np.diff(np.sum(thresh // 200, axis=0, dtype=np.int32)) == -thresh.shape[0])[0] + 1)
#cv2.imwrite('b.png',gray)

#cv2.imshow('', thresh)
#cv2.waitKey()
