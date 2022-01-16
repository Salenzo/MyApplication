import cv2
import numpy as np

img = cv2.imread('psrc.png')
h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)

# 代表应该检测到的行的最小长度
lines = cv2.HoughLines(edges, 1, np.pi/180, int(h/13))

for i in range(len(lines)):
    for rho, theta in lines[i]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + w*(-b))
        y1 = int(y0 + w*(a))
        x2 = int(x0 - w*(-b))
        y2 = int(y0 - w*(a))

        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        print(x1, y1, x2, y2)

cv2.namedWindow('')
cv2.resizeWindow('', 940, 480)
cv2.imshow('', img)
cv2.waitKey()
cv2.destroyAllWindows()
