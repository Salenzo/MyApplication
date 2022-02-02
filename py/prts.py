"""原始罗德岛终端服务，将用代理指挥出现失误为博士烧水。
*它可能无法理解你的操作。*

代理指挥需要模拟操作和知晓点按位置。迫真传奇重犯提供了模拟操作的接口，本模块则包含识别作战界面元素、计算坐标的子程序。

名称以generate开头的函数需要足够的已知参数来返回理论结果；名称以estimate开头的函数从截图中推测变量的值。前缀不是在任何时候都必要的，你知道光学字符识别是一种估计。
"""

import cv2
import numpy as np

def resize(img, height, **kwargs):
    """根据目标高度，锁定原图比例缩放。"""
    return cv2.resize(img, (img.shape[1] * height // img.shape[0], height), **kwargs)

def video_between_two(video_filename, img0, img1):
    """创建对比两张图的视频。"""
    if img0.shape[:2] != img1.shape[:2]:
        raise ValueError("两个图的大小怎么不一样啊？")
    height, width = img0.shape[:2]
    video = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*"avc1"), 60, (width, height))
    for x in range(0, width, width // 500):
        video.write(np.hstack((img0[:, :x], img1[:, x:])))
    video.release()

def line_line_intersection(a0, b0, a1, b1):
    """求两直线a0 -- b0和a1 -- b1的交点，各点以元组给出，共计八个数值。"""
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

def average_nearby_numbers(array, threshold):
    """合并列表中相近的数值簇。

    例如，[1, 1, 4, 5, 1, 4, 1, 9, 1, 9, 8, 1, 0]在阈值略超过1时的结果是[6/7、4 1/3、8 2/3]。
    """
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

def perspective_on_z(perspective, z):
    """通过指定z坐标，降三维透视矩阵到二维。"""
    if perspective.shape != (4, 4):
        raise ValueError("在非三维透视矩阵上调用perspective_on_z")
    perspective = np.delete(perspective, 2, axis=0)
    perspective[:, -1] += perspective[:, 2] * z
    perspective = np.delete(perspective, 2, axis=1)
    return perspective

def generate_perspective(screen_size, level_map, view: int, bullet_time: bool = False):
    """计算视角的理论值。

    该算法由GitHub @yuanyan3060通过逆向工程得到。
    https://github.com/yuanyan3060/Arknights-Tile-Pos
    参数view指定一种摄像机角度，取值0~3，具体值在关卡对应的asset bundle中指定。
    参数bullet_time表示查询放置干员时的倾斜视角。
    """
    width, height = screen_size
    aspect_ratio = height / width
    # 从可能的摄像机位置中选择。
    matrix = np.cumsum([
        [[0.0, -4.81, -7.76], [0.5975104570388794, -0.5, -0.882108688354492]],
        [[0.0, -5.6, -8.92], [0.7989424467086792, -0.5, -0.86448486328125]],
        [[0.0, -5.08, -8.04], [0.6461319923400879, -0.5, -0.877854309082031]],
        [[0.0, -6.1, -9.78], [0.948279857635498, -0.5, -0.85141918182373]],
    ], axis=1, dtype=np.float32)[view, int(bullet_time)]
    # 适应纵横比。
    # 屏幕比16:9更窄的话，摄像机也会移到后方更高处。
    # 数值详见CameraController。有很多个，但数值都一样。
    from_ratio = 9 / 16 # _fromResolution
    to_ratio = 3 / 4 # _toResolution
    matrix += np.float32([0, -1.4, -2.8]) * (max(0, aspect_ratio - from_ratio) / (to_ratio - from_ratio))
    # 构造透视矩阵。
    matrix = np.float32([
        [1, 0, 0, -matrix[0]],
        [0, 1, 0, -matrix[1]],
        [0, 0, 1, -matrix[2]],
        [0, 0, 0, 1],
    ])
    if bullet_time:
        matrix = np.float32([
            [np.cos(np.deg2rad(10)), 0, np.sin(np.deg2rad(10)), 0],
            [0, 1, 0, 0],
            [-np.sin(np.deg2rad(10)), 0, np.cos(np.deg2rad(10)), 0],
            [0, 0, 0, 1],
        ]) @ matrix
    matrix = np.float32([
        [1, 0, 0, 0],
        [0, np.cos(np.deg2rad(30)), -np.sin(np.deg2rad(30)), 0],
        [0, -np.sin(np.deg2rad(30)), -np.cos(np.deg2rad(30)), 0],
        [0, 0, 0, 1],
    ]) @ matrix
    matrix = np.float32([
        [aspect_ratio / np.tan(np.deg2rad(20)), 0, 0, 0],
        [0, 1 / np.tan(np.deg2rad(20)), 0, 0],
        [0, 0, -(1000 + 0.3) / (1000 - 0.3), -(1000 * 0.3 * 2) / (1000 - 0.3)],
        [0, 0, -1, 0],
    ]) @ matrix
    # 透视矩阵初等列变换，移动输入坐标原点到地图中心，并设置高台高度。
    matrix = matrix @ np.float32([
        [1, 0, 0, -level_map.shape[1] / 2],
        [0, 1, 0, -level_map.shape[0] / 2],
        [0, 0, -0.4, 0],
        [0, 0, 0, 1],
    ])
    # 透视矩阵初等行变换，将输出坐标从OpenGL坐标系变换到OpenCV坐标系。
    matrix = np.float32([
        [width, 0, 0, width],
        [0, -height, 0, height],
        [0, 0, 1, 0],
        [0, 0, 0, 2],
    ]) @ matrix
    return matrix

def generate_bullet_time_buildable_mask(screen_size, level_map, perspective, operator_position: int):
    """绘制选中干员时的可放置位蒙版。"""
    width, height = screen_size
    img = np.zeros((height, width), dtype=np.uint8)
    grid_points = np.moveaxis([calculate_grid_points(perspective_on_z(perspective, h), level_map.shape) for h in [0, 1]], 0, 2)
    # 从远到近绘制，产生高台遮挡。
    for row in reversed(range(level_map.shape[0])):
        # 先绘制地面，后绘制高台。
        for h in [0, 1]:
            for col in range(level_map.shape[1]):
                # 获取当前地块的高度类和可放置标志。
                if level_map[row, col] >> 7 & 1 != h: continue
                color = bool(level_map[row, col] >> 5 & 3 & operator_position) * 255
                # 无需绘制不可放置的地面块，因为图像初值为黑（np.zeros）。
                if h == 0 and color == 0: continue
                cv2.fillConvexPoly(img, np.array([
                    grid_points[row, col, h],
                    grid_points[row, col + 1, h],
                    grid_points[row + 1, col + 1, h],
                    grid_points[row + 1, col, h],
                ]), color, cv2.LINE_4)
                if h == 1:
                    # 绘制高台的前面。
                    cv2.fillConvexPoly(img, np.array([
                        grid_points[row, col, 0],
                        grid_points[row, col + 1, 0],
                        grid_points[row, col + 1, 1],
                        grid_points[row, col, 1],
                    ]), 0, cv2.LINE_4)
    # 1920×1080的屏幕测量结果表明，干员立绘蒙版渐变区域横坐标514:785。
    # 考虑到两端全透明和全不透明像素，认定渐变区宽为屏幕高度之¼。
    img = np.uint8(img * np.pad(
        np.linspace(0, 1, height // 4),
        (height * 19 // 40, width - height // 4 - height * 19 // 40),
        "edge"
    ))
    return img

def estimate_perspective_ii(level_map, img2, img3, operator_position):
    """用可部署地块选出从地图坐标到通常视角的透视矩阵。

    同名参数含义与estimate_perspective函数一致，返回值也一致，但是透视矩阵是三维的。
    """
    height, width = img2.shape[:2]
    mask = cv2.compare(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY), cv2.CMP_NE)
    perspectives = [
        generate_perspective((width, height), level_map, view, True)
        for view in range(4)
    ]
    # 寻找最匹配的一种视角。
    view = np.argmax([
        # 峰值信噪比是一种评价图像质量的客观标准……
        cv2.PSNR(
            mask,
            cv2.inRange(generate_bullet_time_buildable_mask((width, height), level_map, perspective, operator_position), 16, 255)
        )
        for perspective in perspectives
    ])
    return generate_perspective((width, height), level_map, view, False), perspectives[view]

def estimate_bullet_time_transform(img0, img1):
    """从通常截图img0与选中干员的子弹时间中的截图img1推断选中干员带来的视角变化。"""
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

def estimate_buildable_mask(homography, img2, img3):
    """从两张选中干员且暂停时的截图找出闪烁的可部署地块在通常视角下的二值图像。

    homography是选中干员带来的视角变化。

    闪烁色与关卡主题有关，一般是绿色，密林悍将归来等部分活动关卡中为褐色。
    画中人活动关卡中地块不闪烁，使识别失效。
    """
    height, width = img2.shape[:2]
    # 先反变换到通常视角，再比较两张图的不同之处，以避免反变换抗锯齿使得得到的图像不是二值的。
    img2, img3 = [cv2.warpPerspective(img, homography, (width, height), flags=cv2.WARP_INVERSE_MAP) for img in [img2, img3]]
    return cv2.inRange(cv2.cvtColor(cv2.absdiff(img2, img3), cv2.COLOR_BGR2GRAY), 1, 255)

def estimate_vanishing_point_y(img1):
    """根据任意地块的二值图像推断通常视角的透视消失点纵坐标。"""
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

def estimate_perspective(level, img0, img1, img2, img3, operator_position):
    """综合练习：估计从地图坐标到通常视角的透视矩阵。

    level：level_map函数返回的地图图像。
    img0：通常视角截图；img1：子弹时间截图；img2、img3：选中干员且暂停时的截图。
    operator_position：位域，选中干员的可部署位置，1 = 可部署在近战位，2 = 可部署在远程位。
    """
    height, width = img0.shape[:2]
    bullet_time_homography = estimate_bullet_time_transform(img0, img1)
    # mask：二值可放置位视图。
    mask = estimate_buildable_mask(bullet_time_homography, img2, img3)
    vanishing_point_y = estimate_vanishing_point_y(mask)
    # 按消失点解除图像的透视，使地块对齐坐标轴，以便借助矩形包围框。
    # 基于可放置位不会出现在偏僻地的假设，此处的透视反变换将丢弃左上和右上的像素。
    inset = width / 2 * height / (height - vanishing_point_y)
    inset_homography = cv2.getPerspectiveTransform(
        np.float32([[0, 0], [0, height], [width, height], [width, 0]]),
        np.float32([[inset, 0], [0, height], [width, height], [width - inset, 0]])
    )
    img0 = cv2.warpPerspective(mask, inset_homography, (width, height), flags=cv2.WARP_INVERSE_MAP)
    # 高台可能遮挡可部署位，因此寻找不可放置近战单位的高台地形并上移一定程度。
    # 假设遮挡物处在地面上，从0到17/18格枚举遮挡物格中占比，计算每种情况的误差。
    # template是每格图块占用18行1列的矩阵，求出的透视矩阵y分量还需变换。
    # TODO operator_position
    # TODO 左右对称修正
    template1 = np.repeat(cv2.compare(cv2.bitwise_and(np.flipud(level), 32), 0, cv2.CMP_NE), 18, axis=0)
    template2 = np.repeat(cv2.compare(cv2.bitwise_and(np.flipud(level), 128 | 32), 128, cv2.CMP_EQ), 18, axis=0)
    best_homography, minimum_error = None, np.inf
    for i in range(18):
        # template是二值地图数据。
        template = cv2.subtract(
            template1,
            np.r_[template2[i:], np.zeros((i, template2.shape[1]), dtype=np.uint8)]
        )
        # 获取矩形包围框，按包围框计算透视矩阵。
        x, y, w, h = cv2.boundingRect(template)
        x0, y0, w0, h0 = cv2.boundingRect(img0)
        # 用矩形包围框确定缩放和平移量。
        homography = cv2.getPerspectiveTransform(
            np.float32([x, template.shape[0] - y])
                + np.float32([[0, 0], [0, -h], [w, -h], [w, 0]]),
            cv2.perspectiveTransform(
                np.float32([[[x0, y0], [x0, y0 + h0], [x0 + w0, y0 + h0], [x0 + w0, y0]]]),
                inset_homography
            )[0]
        )
        # 计算归一化误差，以找出最佳高台遮挡修正量。
        error = np.mean(cv2.absdiff(cv2.resize(template[y:y + h, x:x + w], (w0, h0), interpolation=cv2.INTER_NEAREST), img0[y0:y0 + h0, x0:x0 + w0])) / 255
        if error < minimum_error:
            best_homography, minimum_error = homography, error
    best_homography[:, 1] *= 18
    return best_homography, bullet_time_homography

def calculate_grid_points(homography, shape):
    """计算透视中的所有格点坐标。"""
    # 一并生成格点，批量送入cv2.perspectiveTransform计算透视结果。
    return np.int32(cv2.perspectiveTransform(np.float32(
        np.dstack(np.flipud(np.mgrid[:shape[0] + 1, :shape[1] + 1]))
    ), homography))

def draw_reseau(img, homography, shape):
    """在图上绘制算得的网格线，用于调试。"""
    # 如果输入的透视矩阵是三维的，先降维。
    if homography.shape[1] == 4:
        homography = perspective_on_z(homography, 0)
    # 绘制网格线。
    points = calculate_grid_points(homography, shape)
    for row in range(shape[0] + 1):
        cv2.line(img, tuple(points[row, 0]), tuple(points[row, shape[1]]), [row * 20, 192, 192], 5)
    for col in range(shape[1] + 1):
        cv2.line(img, tuple(points[0, col]), tuple(points[shape[0], col]), [192, 192, col * 15], 5)
    # 绘制网格点。
    for row, col in np.ndindex(shape[0] + 1, shape[1] + 1):
        cv2.circle(img, tuple(points[row, col]), 10, (row * 20, 255, col * 15), -1)

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

def visualize_phash(cls, h):
    """可视化感知散列到微型二值图像。
    
    cls是cv2.img_hash中的类，如cv2.img_hash.averageHash。
    散列的计算方法参照OpenCV C++代码，本函数执行相反的操作。
    https://github.com/opencv/opencv_contrib/tree/4.x/modules/img_hash/src
    """
    if type(h) is str: h = bytes.fromhex(h)
    if type(h) is bytes: h = np.uint8(list(h))
    if cls is cv2.img_hash.averageHash:
        return np.unpackbits(h, bitorder="little").reshape(8, 8) * 255
    elif cls is cv2.img_hash.blockMeanHash:
        # OpenCV实现的块均值散列省略了文档引用的论文中算法的加密，且所谓块“中位数”实为均值，使得它除了大一点以外，和均值散列没什么两样。
        return np.unpackbits(h, bitorder="little").reshape(16, 16) * 255
    raise ValueError("我没用过这种感知散列")

def ocr_natural_number(img, font):
    """识别背景较暗、前景白色的自然数。"""
    if len(img.shape) > 2:
        raise ValueError("你这图片怎么不是灰度的啊？")
    # 曲线“_/”：使较暗的灰色转换为黑色。
    img = cv2.addWeighted(img, 2, 255, -1, 0)
    phash = cv2.img_hash.AverageHash_create()
    # 以字形连续原理切开每个数字。
    value = 0
    for x0, x1 in np.where(np.diff(np.concatenate(([False], np.bitwise_or.reduce(img != 0, axis=0), [False]))))[0].reshape(-1, 2):
        # 裁切到最小包围框，然后用感知散列识别数字。
        _, y0, _, h = cv2.boundingRect(img[:, x0:x1])
        h = np.ravel(phash.compute(img[y0:y0 + h, x0:x1]))
        value *= 10
        value += np.argmin([phash.compare(g, h) for g in font])
    return value

def fractional_cost(img):
    """计算部署费用的小数部分。"""
    height = img.shape[0]
    # 最佳判决门限：费用条亮色灰度255，暗色灰度67。
    return np.mean(img[height * 181 // 240, -height // 6:] >= 160)

def integer_cost(img):
    """计算部署费用的整数部分。"""
    height = img.shape[0]
    return ocr_natural_number(cv2.cvtColor(img[height * 41 // 60 + 1:height * 3 // 4 - 1, -height // 9:], cv2.COLOR_BGR2GRAY), OCR_NOVECENTO)

def operator_xs(screen_size, n, index):
    """计算待命中的各干员左边界横坐标（浮点数）。

    screen_size是(屏幕宽度, 屏幕高度)，n是待命中的干员及装置种类数，index是None。
    本来试图计算选中干员时的挤压情况的，但似乎这块逻辑在更新中有过变动，现在难以推测。
    Unity对象坐标总是存储为浮点数。最终显示时，舍入坐标的方法是round。
    Unity（.NET CLR）和Python提供的round函数都舍入到最近的整数，在.5时舍入到最近的偶数。
    返回值保留小数的原因是该坐标可能继续用于计算其他坐标（例如职业与费用的位置），使用舍入后的值将使最终坐标差1。
    """
    width, height = screen_size
    if index is None:
        return np.linspace(max(width - n * height * 89 / 540, 0.0), width, n, endpoint=False)
    else:
        raise NotImplementedError()

def in_battle(img):
    """判断截图是否处在战斗内。

    方法是将费用标志所在位置的图像与费用标志模板比较。
    """
    height, width = img.shape[:2]
    phash = cv2.img_hash.AverageHash_create()
    return phash.compare(
        phash.compute(img[height * 41 // 60:height * 3 // 4, -height // 6:-height // 9]),
        np.uint8([[0x00, 0x00, 0x18, 0x44, 0x74, 0x28, 0x10, 0x00]])
    ) < 5

def main():
    import ptilopsis
    cv2.namedWindow("", cv2.WINDOW_KEEPRATIO)
    img0 = cv2.imread("b1.png")
    assert in_battle(img0), "b1.png不是战斗界面截图？"
    print(f"Cost = {integer_cost(img0) + fractional_cost(img0)}")
    img1 = cv2.imread("b2.png")
    img2 = cv2.imread("b3.png")
    img3 = cv2.imread("b4.png")
    level = ptilopsis.level_map(ptilopsis.read_json("level_a001_06.json"))
    homography, bullet_time_homography = estimate_perspective_ii(level, img2, img3, 1)
    draw_reseau(img0, homography, level.shape)

    cv2.imshow("", img0)
    cv2.imshow("", visualize_phash(cv2.img_hash.blockMeanHash, "10087c3efffffe7f00008001c003fe3ffc3f003c003e9c07fe03fe03e7ffc2ff"))
    cv2.waitKey()

if __name__ == "__main__":
    main()
