# 重重障碍
迫真传奇重犯作为无障碍服务，提供自动在屏幕上模拟滑动和实时屏幕截图到cv2图像的功能，由手机上执行的Python线程控制。

## 运行的方法

1. 安装迫真应用，不用打开。
2. 打开设置 > 更多设置 > 无障碍 > 已下载的服务 > 迫真传奇重犯 > 使用迫真传奇重犯。路径随手机制造商和操作系统版本而变化，请自行变通。
    * 正确执行该步骤后，画面底部将出现一行黑底白字。
    * 这行文字是迫真控制台™，用于显示程序输出。粗体字是迫真传奇重犯自身给出的提示，而常规字是Python程序要求的。
3. 如果需要使用屏幕截图，点击平视显示器中的“获取截屏权限”按钮两次。
    * 第一次按下时，将弹出权限对话框。第二次按下时，将启动媒体投射（可能在状态栏中显示表示正在录制的图标）。
4. 访问刚开启服务时迫真控制台中显示的的地址。
    * 该地址指向局域网内的一个站点。你可以使用网域内的设备（包括手机自己）上的浏览器登陆该站点。有时应用检测到的IP地址有误（因为我不知道怎么写获取局域网IP地址），可以用别的应用找到本机局域网IP，也可以用局域网扫描工具……
    * 然而，该网页简陋的样式暗示你更应该将其集成到代码编辑工作流中而不是通过浏览器手工填写表单。直接使用该页面将遇到代码丢失等问题。
    * 因为这个页面就是代码服务器的文档。回忆爬虫的制作方法，并将自动提交表单和访问网页的方法其套用在该站点上，所谓不言自明是也。
    * 表单提交的时刻，指定文件将被覆盖。会自动创建不存在的中间目录。
    * 单击“运行”链接时，当前正在执行的Python脚本将被终止，新的脚本将被加载和运行。
5. 确认过可以访问，和该网页简陋的设计后，用run.py从工作区向手机传输py文件夹内的所有内容。需要修改脚本开头的hostname变量以适应你的网络情况。
    * 必须在py文件夹内运行run.py。

## 控制的方法

提供infamous_recidivist_service模块，该模块的实现在Kotlin侧，但文档在infamous_recidivist_service.py stub中。

出于历史和便利原因，通常以`import infamous_recidivist_service as adb`导入，但该对象与Android debug bridge没有关系。

此外，有numpy和cv2库可用。但是，诸如cv2.setMouseCallback这样的图形界面函数无法使用，将抛出“The function is not implemented”的异常。

## 试验的方法

下面的代码通过不间断截取60张屏幕截图来测试截图的帧率。截图将被保存在应用私有数据文件夹中。

```python
import time
import cv2
import numpy as np
import infamous_recidivist_service as adb

t0 = time.time()

j = 0
list = [None] * 60
for i in range(60):
    list[i] = adb.screenshot()
    if list[i] is not None:
        print(f"截了第{i}张（丢了{i - j}张）。")
        j = j + 1

t1 = time.time()

for i in range(60):
    if list[i] is not None:
        print(f"正在保存第{i}张。")
        cv2.imwrite(f"{i}.png", list[i])

print(f"截取{j}帧到OpenCV图像共计{t1 - t0}秒。")
```

## 巧妙的方法

print函数被改写，因而输出到迫真控制台。没有修改sys.stdout和sys.stderr，它们被Chaquopy重定向到Android日志。

cv2.imshow被改写，因而输出到坐标拾取器。当前实现无视窗口标题参数，只能显示一张图像。
