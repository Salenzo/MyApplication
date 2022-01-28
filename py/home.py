import cv2
import numpy as np
import infamous_recidivist_service as adb

def sift(img, template_path: str): # -> Tuple[Tuple[int, int], Tuple[int, int]]
    sift = cv2.SIFT_create()
    template = cv2.imread(template_path)
    template_height, template_width = template.shape[:2]
    keypoint1, descriptor1 = sift.detectAndCompute(template, None)
    keypoint2, descriptor2 = sift.detectAndCompute(img, None)

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
    return (int(min(quad[:, 0, 0])), int(min(quad[:, 0, 1]))), (int(max(quad[:, 0, 0])), int(max(quad[:, 0, 1])))

def main():
    (x0, y0), (x1, y1) = sift(adb.screenshot(), "templatejijian.png")
    adb.tap((x0 + x1) / 2, (y0 + y1) / 2)
