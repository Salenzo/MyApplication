import json
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

# 合并列表中相近的数值簇。
# 例如，[1, 1, 4, 5, 1, 4, 1, 9, 1, 9, 8, 1, 0]在阈值略超过1时的结果是[6/7、4 1/3、8 2/3]。
def average_nearby_numbers(array, threshold):
    if len(array) == 0:
        return []
    cluster = []
    retval = []
    for x in np.sort(array):
        if len(cluster) != 0 and x - cluster[0] >= threshold:
            retval.append(np.mean(cluster))
            cluster = [x]
        else:
            cluster.append(x)
    retval.append(np.mean(cluster))
    return retval

# 从通常截图img0与选中干员的子弹时间中的截图img1推断选中干员带来的视角变化。
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
    homography, _ = cv2.findHomography(
        np.array([keypoint0[m.queryIdx].pt for m in matches]) / scale + (x0, y0),
        np.array([keypoint1[m.trainIdx].pt for m in matches]) / scale + (x0, y0),
        cv2.RANSAC
    )
    #video_between_two("114.mp4", cv2.warpPerspective(img0, homography, (width, height)), img1)
    return homography

# 从两张选中干员且暂停时的截图找出闪烁的可部署地块的二值图像。
# homography是选中干员带来的视角变化。
def buildable_mask(homography, img2, img3):
    height, width = img2.shape[:2]
    # 先反变换到通常视角，再比较两张图的不同之处，以避免反变换抗锯齿使得得到的图像不是二值的。
    img2, img3 = [cv2.warpPerspective(img, homography, (width, height), flags=cv2.WARP_INVERSE_MAP) for img in [img2, img3]]
    return cv2.inRange(cv2.cvtColor(cv2.absdiff(img2, img3), cv2.COLOR_BGR2GRAY), 1, 255)

# 根据任意地块的二值图像推断通常视角的透视消失点纵坐标。
def vanishing_point_y(img1):
    height, width = img1.shape[:2]
    # 检测边缘，寻找线段的标准做法。
    img1 = cv2.Canny(img1, 50, 200, None, 3)
    lines = cv2.HoughLinesP(img1, 1, np.pi / 180, 50, None, height // 24, height // 12)
    # 根据找到的线段延长线与中心竖直轴线的交点计算消失点的位置，以及导出水平线列表。
    # 此后img1仅用来输出调试信息。
    img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    vanishing_point_ys = []
    for [[x0, y0, x1, y1]] in lines:
        if abs(x0 - x1) > 3:
            y = y0 + (width / 2 - x0) * (y1 - y0) / (x1 - x0)
            if y < -height:
                vanishing_point_ys.append(y)
                cv2.line(img1, (x0, y0), (x1, y1), (224, 175, 102), 3, cv2.LINE_AA)
                cv2.putText(img1, f"{int(y)}", (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 1, (224, 175, 202), 2)
    return np.median(vanishing_point_ys)

# 转换JSON格式的关卡文件到灰度图像。
# 像素值是位域：128 = 高台地形；64 = 可放置远程单位；32 = 可放置近战单位；2 = 可通行飞行单位（猜想）；1 = 可通行地面单位。
def read_level(filename):
    with open(filename) as f:
        level = json.load(f)
    a = np.array(level["mapData"]["map"], dtype=np.uint8)
    if a.shape[0] != level["mapData"]["height"] or a.shape[1] != level["mapData"]["width"]:
        raise ValueError("地图数据自相矛盾：宽高与数组大小不对应")
    for row, col in np.ndindex(a.shape):
        tile = level["mapData"]["tiles"][a[row, col]]
        a[row, col] = tile["heightType"] << 7 | tile["buildableType"] << 5 | tile["passableMask"]
    return a

# 按消失点解除图像的透视，再用矩形包围框确定缩放和平移量，产生从地图数据到通常视角的透视矩阵。
def perspective(vanishing_point_y, template, img1):
    height, width = img1.shape[:2]
    # 基于可放置位不会出现在偏僻地的假设，此处的透视反变换将丢弃左上和右上的像素。
    inset = width / 2 * height / (height - vanishing_point_y)
    homography, _ = cv2.findHomography(
        np.array([[0, 0], [0, height], [width, height], [width, 0]]),
        np.array([[inset, 0], [0, height], [width, height], [width - inset, 0]]),
        0
    )
    img0 = cv2.warpPerspective(img1, homography, (width, height), flags=cv2.WARP_INVERSE_MAP)
    # 获取矩形包围框，按包围框计算透视矩阵。
    x, y, w, h = cv2.boundingRect(template)
    x0, y0, w0, h0 = cv2.boundingRect(cv2.morphologyEx(img0, cv2.MORPH_OPEN, np.ones((5, 5), dtype=np.uint8)))
    homography, _ = cv2.findHomography(
        np.array([[x, y], [x, y + h], [x + w, y + h], [x + w, y]]),
        cv2.perspectiveTransform(
            np.float32([[[x0, y0]], [[x0, y0 + h0]], [[x0 + w0, y0 + h0]], [[x0 + w0, y0]]]),
            homography
        ),
        0
    )
    return homography

# 在图上绘制算得的网格线，用于调试。
def draw_reseau(img, homography, shape):
    points = np.int32(cv2.perspectiveTransform(np.float32(
        [[[col, row*3] for col in range(shape[1] + 1)] for row in range(shape[0] + 1)]
    ), homography))
    for row in range(shape[0] + 1):
        cv2.line(img, points[row, 0], points[row, shape[1]], [row * 20, 192, 192], 5)
    for col in range(shape[1] + 1):
        cv2.line(img, points[0, col], points[shape[0], col], [192, 192, col * 15], 5)
    for row in range(shape[0] + 1):
        for col in range(shape[1] + 1):
            cv2.circle(img, points[row, col], 10, [row * 20, 255, col * 15], -1)

img0 = cv2.imread("b1.png")
img1 = cv2.imread("b2.png")
img2 = cv2.imread("b3.png")
img3 = cv2.imread("b4.png")
mask = buildable_mask(bullet_time_transform(img0, img1), img2, img3)
print(1)
level = read_level("level_a001_06.json")

template = np.roll(np.repeat(cv2.compare(cv2.bitwise_and(level, 128), 0, cv2.CMP_NE), 3, axis=0), -1, axis=0)
template[-1, :] = 0
template = cv2.subtract(np.repeat(cv2.compare(cv2.bitwise_and(level, 32), 0, cv2.CMP_NE), 3, axis=0), template)
homography = perspective(vanishing_point_y(mask), template, mask)
draw_reseau(img0, homography, level.shape)

cv2.namedWindow("", cv2.WINDOW_KEEPRATIO)
cv2.imshow("", img0)
cv2.waitKey()
