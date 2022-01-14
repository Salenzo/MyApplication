#!/usr/bin/env python
import os
import base64
import requests

# 设置目标手机的地址。
hostname = '192.168.1.3'

# 向目标手机发送GET或POST请求。
def rq(method, command, arguments={}):
    x = f'http://{hostname}:11451/{command}'
    if method == 'POST':
        x = requests.post(x, data=arguments)
    else:
        x = requests.get(x, params=arguments)
    print(command, x)

# 首先清除目标。
rq('GET', 'reset')
# 遍历当前目录下的所有源文件，依次提交。
for root, dirs, files in os.walk('.'):
    for name in files:
        filename = os.path.join(root, name)
        print(filename)
        with open(filename, 'rb') as f:
            rq('POST', '', {
                'filename': filename.replace('\\', '/'),
                'base64': base64.b64encode(f.read()).decode(),
            })
    if '__pycache__' in dirs:
        dirs.remove('__pycache__')
# 最后重新运行。
rq('GET', 'reload')
