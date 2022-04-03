#!/usr/bin/env python
import os
import zlib
import base64
import requests

# 设置目标手机的地址。
hostname = "192.168.1.6"

# 向目标手机发送GET或POST请求。
def rq(method, command, arguments={}):
    x = f"http://{hostname}:11451/{command}"
    if method == "POST":
        x = requests.post(x, data=arguments)
    else:
        x = requests.get(x, params=arguments)
    print(command, x)
    return x.content.decode()

# 首先获取目标的状态。
old = {}
for line in rq("GET", "ls").splitlines():
    filename, size, crc = line.split("\t")
    old[filename] = (int(size), int(crc, base=16))
# 遍历当前目录下的所有源文件，依次提交。
for root, dirs, files in os.walk("."):
    for name in files:
        filename = os.path.normpath(os.path.join(root, name)).replace("\\", "/")
        print(filename, end="...")
        with open(filename, "rb") as f:
            b = f.read()
            if filename in old and len(b) == old[filename][0] and zlib.crc32(b) == old[filename][1]:
                print("skipped.")
            else:
                rq("POST", "", {
                    "filename": filename,
                    "base64": base64.b64encode(b).decode(),
                })
    if "__pycache__" in dirs:
        dirs.remove("__pycache__")
    if ".git" in dirs:
        dirs.remove(".git")
# 最后重新运行。
rq("GET", "reload")
