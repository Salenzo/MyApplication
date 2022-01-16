from itertools import combinations
import cv2
import numpy as np
import math

# 根据目标高度，锁定原图比例缩放。
def resize(img, height, **kwargs):
    return cv2.resize(img, (img.shape[1] * height // img.shape[0], height), **kwargs)

# 创建对比两张图的视频。
def video_between_two(video_filename, img0, img1):
    if img0.shape[:2] != img1.shape[:2]:
        raise ValueError("两个图的大小怎么不一样啊？")
    height, width = img0.shape[:2]
    video = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*"avc1"), 60, (width, height))
    for x in range(0, width, width // 500):
        video.write(np.hstack((img0[:, :x], img1[:, x:])))
    video.release()

# 求两直线a0 -- b0和a1 -- b1的交点，各点以元组给出，共计八个数值。
def line_line_intersection(a0, b0, a1, b1):
    A0 = b0[1] - a0[1]
    B0 = a0[0] - b0[0]
    C0 = a0[0] * A0 + a0[1] * B0
    A1 = b1[1] - a1[1]
    B1 = a1[0] - b1[0]
    C1 = a1[0] * A1 + a1[1] * B1
    det = A0 * B1 - A1 * B0
    if abs(det) > 1e-8:
        return (C0 * B1 - C1 * B0) / det, (C1 * A0 - C0 * A1) / det
    else:
        return None

# 从通常截图与选中干员的子弹时间中的截图推断选中干员带来的视角变化。
def bullet_time_transform(img0, img1):
    height, width = img0.shape[:2]
    x0, y0 = height * 2 // 3, height // 12
    x1, y1 = width - height // 3, height * 4 // 5
    scale = 360 / (y1 - y0)
    reduced_img0, reduced_img1 = [
        cv2.resize(cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), None, fx=scale, fy=scale)
        for img in [img0, img1]
    ]
    sift = cv2.SIFT_create()
    keypoint0, descriptor0 = sift.detectAndCompute(reduced_img0, None)
    keypoint1, descriptor1 = sift.detectAndCompute(reduced_img1, None)
    matches = cv2.BFMatcher().match(descriptor0, descriptor1)
    homography, mask = cv2.findHomography(
        np.array([keypoint0[m.queryIdx].pt for m in matches]) / scale + (x0, y0),
        np.array([keypoint1[m.trainIdx].pt for m in matches]) / scale + (x0, y0),
        cv2.RANSAC
    )
    #video_between_two("114.mp4", cv2.warpPerspective(img0, homography, (width, height)), img1)
    return homography

def eee(img0, img1, img2, img3):
    homography = bullet_time_transform(img0, img1)
    height, width = img0.shape[:2]
    x0, y0 = height * 2 // 3, height // 12
    x1, y1 = width - height // 3, height * 4 // 5
    img2, img3 = [cv2.warpPerspective(img, homography, (width, height), flags=cv2.WARP_INVERSE_MAP) for img in [img2, img3]]
    img1 = cv2.inRange(cv2.cvtColor(cv2.absdiff(img2, img3), cv2.COLOR_BGR2GRAY), 1, 255)
    img1 = cv2.Canny(img1, 50, 200, None, 3)
    lines = cv2.HoughLinesP(img1, 1, math.pi / 180, 50, None, height // 24, height // 12)
    if lines is None:
        lines = []
    img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    print(lines)
    for [l] in lines:
        cv2.line(img1, (l[0], l[1]), (l[2], l[3]), (224, 175, 102), 3, cv2.LINE_AA)
    points = [p for p in [line_line_intersection((l0[0], l0[1]), (l0[2], l0[3]), (l1[0], l1[1]), (l1[2], l1[3])) for l0, l1 in combinations([line for [line] in lines if abs(line[1] - line[3]) > 2], 2)] if p is not None and abs(p[0] - width // 2) < height // 240]
    print(list(points))
    cv2.imwrite("out11.png", img1)
    #cv2.imshow("", img2)
    #cv2.waitKey()

print(eee(cv2.imread("b1.png"), cv2.imread("b2.png"), cv2.imread("b3.png"), cv2.imread("b4.png")))
