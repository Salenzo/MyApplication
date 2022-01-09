# 重重障碍
迫真传奇重犯作为无障碍服务，提供自动在屏幕上模拟滑动和实时屏幕截图到cv2图像的功能，由手机上执行的Python线程控制。

## 运行的方法

1. 安装迫真应用，不用打开。
2. 打开设置 > 更多设置 > 无障碍 > 已下载的服务 > 迫真传奇重犯 > 使用迫真传奇重犯。路径随手机制造商和操作系统版本而变化，请自行变通。
   * 正确执行该步骤后，画面底部将出现淡蓝色的一行文字。
   * 这行文字是迫真控制台™，用于显示程序输出。粗体字是迫真传奇重犯自身给出的提示，而常规字是Python程序要求的。
3. 如果需要使用屏幕截图，打开迫真应用，在右上角的菜单中选择“获取截屏权限”。
4. 访问刚开启服务时迫真控制台中显示的的地址。
    * 该地址指向局域网内的一个站点。你可以使用网域内的设备（包括手机自己）上的浏览器登陆该站点。
    * 然而，该网页简陋的样式暗示你更应该将其集成到代码编辑工作流中而不是通过浏览器手工填写表单。直接使用该页面将遇到代码丢失等问题。
    * 请回忆爬虫的制作方法，并将自动提交表单的方法其套用在该站点上。
    * 表单提交的时刻，当前正在执行的Python脚本将被终止，新的脚本将被保存、加载、运行。

## 控制的方法

提供adb对象。该对象与Android debug bridge没有关系。

- `adb.tap(x, y)`：模拟点击。
  - 不阻塞，操作固定定时20毫秒。
  - 其实是在指定点附近两像素区域内滑动。
- `adb.swipe(x0, y0, x1, y1, duration)`：模拟直线滑动。
  - 不阻塞，duration单位为秒。
  - Android 11及以后才能流畅模拟，早期版本的系统高傲地以为100毫秒的采样周期能满足所有人的需求。
- `adb.screenshot()`：截取屏幕。如果没有权限，或者画面距上次截图以来没有变化，或者还没来得及截到最新一张图，返回None。成功截到的话，返回的是Java字节数组，以奇怪顺序存储色值。
  - 目前固定分辨率1920 × 1080。
  - 转换到适用于cv2的方法是`import cv2; import numpy as np; cv2.cvtColor(np.array(a, dtype=np.uint8).reshape(1080, 1920, 4), cv2.COLOR_BGRA2RGB)`。
- `adb.log(object)`：在迫真控制台中打印信息。迫真控制台只能显示最近的一行文本，没有任何滚屏手段。

此外，有numpy和cv2库可用。

## 试验的方法

下面的代码通过不间断截取60张屏幕截图来测试截图的帧率。截图将被保存在应用私有数据文件夹中。

```python
import cv2
import numpy as np
import time

t0 = time.time()

j = 0
list = [None] * 60
for i in range(60):
    a = adb.screenshot()
    if not (a is None):
        a = cv2.cvtColor(np.array(a, dtype=np.uint8).reshape(1080, 1920, 4), cv2.COLOR_BGRA2RGB)
        list[i] = a
        adb.log(f"截了第{i}张（丢了{i - j}张）。")
        j = j + 1

t1 = time.time()

for i in range(60):
    if not (list[i] is None):
        adb.log(f"正在保存{i}")
        cv2.imwrite(f"/data/data/io.github.salenzo.myapplication/files/{i}.png", list[i])
adb.log(f"截取{j}帧到OpenCV图像共计{t1 - t0}秒。")
```
