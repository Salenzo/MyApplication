from urllib.request import HTTPPasswordMgrWithPriorAuth
import cv2
import numpy as np

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

def eee(img0, img1):
    homography = bullet_time_transform(img0, img1)
    height, width = img0.shape[:2]
    x0, y0 = height * 2 // 3, height // 12
    x1, y1 = width - height // 3, height * 4 // 5
    img1 = cv2.warpPerspective(img1, homography, (width, height), flags=cv2.WARP_INVERSE_MAP)
    img1 = cv2.divide(img1.astype(np.uint16) * 256, img0, dtype=cv2.CV_8U)
    img1 = cv2.GaussianBlur(img1, (0, 0), 2)
    img1 = cv2.inRange(img1, np.array([128, 255, 128], dtype=np.uint8), np.array([240, 255, 240], dtype=np.uint8))
    cv2.imwrite("out11.png", img1[y0:y1, x0:x1])
    #cv2.imshow("", img2)
    #cv2.waitKey()

print(eee(cv2.imread("b1.jpg"), cv2.imread("b2.jpg")))
