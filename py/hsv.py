import cv2
import numpy as np

cv2.namedWindow("")
cv2.resizeWindow('', 940, 480)

#94,117,70
Lower = np.array([94, 74, 0])
Upper = np.array([117, 255, 255])
filenames = ["F9.png", "F10.png"]
def on_trackbar(val):
    a = cv2.imread(filenames[im])
    a1 = cv2.inRange(cv2.cvtColor(a, cv2.COLOR_BGR2HSV), Lower, Upper)
    cv2.imshow("", a1)
trackbar_name = '114514'
im = 0
def aa(x):
    global im
    im = x
    on_trackbar(114514)
cv2.createTrackbar("x", "", im, len(filenames)-1, aa)
#cv2.createTrackbar("0 H", "", Lower[0], 255, lambda x: on_trackbar(Lower.put(0, x)))
#cv2.createTrackbar("1 H", "", Upper[0], 255, lambda x: on_trackbar(Upper.put(0, x)))
cv2.createTrackbar("0 S", "", Lower[1], 255, lambda x: on_trackbar(Lower.put(1, x)))
cv2.createTrackbar("1 S", "", Upper[1], 255, lambda x: on_trackbar(Upper.put(1, x)))
cv2.createTrackbar("0 V", "", Lower[2], 255, lambda x: on_trackbar(Lower.put(2, x)))
cv2.createTrackbar("1 V", "", Upper[2], 255, lambda x: on_trackbar(Upper.put(2, x)))
# Show some stuff
on_trackbar(0)
# Wait until user press some key
cv2.waitKey(0)