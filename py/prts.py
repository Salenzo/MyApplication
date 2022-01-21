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
    # 实际上，空间地面上间隔相等的水平线，透视后仍为水平线，其到消失点距离的倒数之差也相等。

# 按消失点解除图像的透视，再用矩形包围框确定缩放和平移量，返回从地图数据到通常视角的透视矩阵和归一化误差。误差用于确定高台遮挡修正值。
# template是二值地图数据，img1是二值可放置位视图。
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
    x0, y0, w0, h0 = cv2.boundingRect(img0)
    homography, _ = cv2.findHomography(
        np.array([[x, y], [x, y + h], [x + w, y + h], [x + w, y]]),
        cv2.perspectiveTransform(
            np.float32([[[x0, y0]], [[x0, y0 + h0]], [[x0 + w0, y0 + h0]], [[x0 + w0, y0]]]),
            homography
        ),
        0
    )
    return homography, np.mean(cv2.absdiff(cv2.resize(template[y:y + h, x:x + w], (w0, h0), interpolation=cv2.INTER_NEAREST), img0[y0:y0 + h0, x0:x0 + w0])) / 255

# 综合练习：估计透视矩阵。
# level：level_map函数返回的地图数据。
# img0：通常视角截图；img1：子弹时间截图；img2、img3：选中干员且暂停时的截图。
# operator_position：位域，选中干员的可部署位置，1 = 可部署在近战位，2 = 可部署在远程位。
def Perspective(level, img0, img1, img2, img3, operator_position):
    bullet_time_homography = bullet_time_transform(img0, img1)
    mask = buildable_mask(bullet_time_homography, img2, img3)
    # 高台可能遮挡可部署位，因此寻找不可放置近战单位的高台地形并上移一定程度。
    # 假设遮挡物处在地面上，从0到17/18格枚举遮挡物格中占比，计算每种情况的误差。
    # template是每格图块占用18行1列的矩阵，求出的透视矩阵y分量还需变换。
    # TODO operator_position
    # TODO 左右对称修正
    template1 = np.repeat(cv2.compare(cv2.bitwise_and(level, 32), 0, cv2.CMP_NE), 18, axis=0)
    template2 = np.repeat(cv2.compare(cv2.bitwise_and(level, 128 | 32), 128, cv2.CMP_EQ), 18, axis=0)
    homography, _ = min([
        perspective(
            vanishing_point_y(mask),
            cv2.subtract(
                template1,
                np.vstack((
                    template2[i:],
                    np.zeros((i, template2.shape[1]), dtype=np.uint8)
                ))
            ),
            mask
        ) for i in range(18)
    ], key=lambda x: x[1])
    homography[:, 1] *= 18
    return homography, bullet_time_homography

# 在图上绘制算得的网格线，用于调试。
def draw_reseau(img, homography, shape):
    points = np.int32(cv2.perspectiveTransform(np.float32(
        [[[col, row] for col in range(shape[1] + 1)] for row in range(shape[0] + 1)]
    ), homography))
    for row in range(shape[0] + 1):
        cv2.line(img, tuple(points[row, 0]), tuple(points[row, shape[1]]), [row * 20, 192, 192], 5)
    for col in range(shape[1] + 1):
        cv2.line(img, tuple(points[0, col]), tuple(points[shape[0], col]), [192, 192, col * 15], 5)
    for row in range(shape[0] + 1):
        for col in range(shape[1] + 1):
            cv2.circle(img, tuple(points[row, col]), 10, [row * 20, 255, col * 15], -1)

# 字形的均值散列值表。
# 我可以从十六进制散列中直接读出原图，你也可以。
# Novecento字体主要用于作战中。这里的散列值来自部署费用。
OCR_NOVECENTO = np.uint8([
    [0x3c, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3c], # 0
    [0xe0, 0xfc, 0xe7, 0xe0, 0xe0, 0xe0, 0xe0, 0xe0], # 1
    [0x3c, 0xc3, 0x80, 0xc0, 0x60, 0x18, 0x06, 0xff], # 2
    [0x7c, 0xc2, 0xc0, 0x70, 0x40, 0x80, 0xc3, 0x7c], # 3
    [0x60, 0x70, 0x48, 0x44, 0x42, 0xff, 0x60, 0x60], # 4
    [0x7e, 0x02, 0x02, 0x77, 0xc0, 0x80, 0xc3, 0x3e], # 5
    [0x10, 0x08, 0x04, 0x66, 0x83, 0x81, 0xc3, 0x3c], # 6
    [0xff, 0x40, 0x20, 0x30, 0x18, 0x08, 0x04, 0x02], # 7
    [0x3c, 0x42, 0x42, 0x3c, 0x42, 0x81, 0x83, 0x7e], # 8
    [0x3c, 0xc3, 0x81, 0x81, 0x66, 0x20, 0x10, 0x08], # 9
])
# Bender字体主要用于基建中。
OCR_BENDER = np.uint8([
    # 等用到再说吧。
])

# 识别背景较暗、前景白色的自然数。
def ocr_natural_number(img, font):
    if len(img.shape) > 2:
        raise ValueError("你这图片怎么不是灰度的啊？")
    # 曲线“_/”：使较暗的灰色转换为黑色。
    img = cv2.addWeighted(img, 2, 255, -1, 0)
    phash = cv2.img_hash.AverageHash_create()
    # 以字形连续原理切开每个数字。
    value = 0
    for x0, x1 in (np.where(np.diff(np.concatenate(([False], np.bitwise_or.reduce(img != 0, axis=0), [False]))))[0]).reshape(-1, 2):
        # 裁切到最小包围框，然后用感知散列识别数字。
        _, y0, _, h = cv2.boundingRect(img[:, x0:x1])
        h = phash.compute(img[y0:y0 + h, x0:x1]).flatten()
        value *= 10
        value += np.argmin([phash.compare(g, h) for g in font])
    return value

# 计算部署费用的小数部分。
def fractional_cost(img):
    height = img.shape[0]
    # 最佳判决门限：费用条亮色灰度255，暗色灰度67。
    return np.mean(img[height * 181 // 240, -height // 6:] >= 160)

# 计算部署费用的整数部分。
def integer_cost(img):
    height = img.shape[0]
    return ocr_natural_number(cv2.cvtColor(img[height * 41 // 60 + 1:height * 3 // 4 - 1, -height // 9:], cv2.COLOR_BGR2GRAY), OCR_NOVECENTO)

# 计算待命中的各干员左边界横坐标（浮点数）。
# screen_size是(屏幕宽度, 屏幕高度)，n是待命中的干员及装置种类数，index是None。
# 本来试图计算选中干员时的挤压情况的，但似乎这块逻辑在更新中有过变动，现在难以推测。
# Unity对象坐标总是存储为浮点数。最终显示时，舍入坐标的方法是round。
# Unity（.NET CLR）和Python提供的round函数都舍入到最近的整数，在.5时舍入到最近的偶数。
# 返回值保留小数的原因是该坐标可能继续用于计算其他坐标（例如职业与费用的位置），使用舍入后的值将使最终坐标差1。
def operator_xs(screen_size, n, index):
    width, height = screen_size
    if index is None:
        return np.linspace(max(width - n * height * 89 / 540, 0.0), width, n, endpoint=False)
    else:
        raise NotImplementedError()

# 判断截图是否处在战斗内。
# 方法是将费用标志所在位置的图像与费用标志模板比较。
def in_battle(img):
    height, width = img.shape[:2]
    phash = cv2.img_hash.AverageHash_create()
    return phash.compare(
        phash.compute(img[height * 41 // 60:height * 3 // 4, -height // 6:-height // 9]),
        np.uint8([[0x00, 0x00, 0x18, 0x44, 0x74, 0x28, 0x10, 0x00]])
    ) < 5

def main():
    import database
    cv2.namedWindow("", cv2.WINDOW_KEEPRATIO)
    img0 = cv2.imread("b1.png")
    assert in_battle(img0), "b1.png不是战斗界面截图？"
    print(f"Cost = {integer_cost(img0) + fractional_cost(img0)}")
    img1 = cv2.imread("b2.png")
    img2 = cv2.imread("b3.png")
    img3 = cv2.imread("b4.png")
    with open("level_a001_06.json") as f:
        level = database.level_map(json.load(f))
    homography, bullet_time_homography = Perspective(level, img0, img1, img2, img3, 1)
    draw_reseau(img0, homography, level.shape)

    cv2.imshow("", img0)
    cv2.waitKey()

if __name__ == "__main__":
    main()
