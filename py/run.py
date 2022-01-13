import os
import base64
from urllib import request, parse

hostname = "192.168.1.3"

def rq(method, command, arguments = None):
    global hostname
    x = f"http://{hostname}:11451/{command}"
    if method == "POST":
        x = request.Request(x, data=parse.urlencode(arguments).encode())
    print(command, request.urlopen(x).read())


rq("GET", "reset")
for root, dirs, files in os.walk("."):
    for name in files:        
        filename = os.path.join(root, name)
        print(filename)
        with open(filename, "rb") as f:
            rq("POST", "", {
                "filename": filename.replace("\\", "/"),
                "base64": base64.b64encode(f.read()).decode(),
            })
    if "__pycache__" in dirs:
        dirs.remove("__pycache__")
rq("GET", "reload")
