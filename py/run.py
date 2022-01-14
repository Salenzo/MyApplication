#!/usr/bin/env python
import os
import base64
import requests

hostname = '192.168.1.103'

def rq(method, command, arguments = None):
    global hostname
    x = f'http://{hostname}:11451/{command}'
    if method == 'POST':
        x = requests.post(x, data=arguments)
    else:
        x = requests.get(x)
    print(command, x)


rq('GET', 'reset')
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
rq('GET', 'reload')
