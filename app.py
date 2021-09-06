from app.config import cfg
from app.adb import ADBClient
from app.img import image

IMG = image('./app/img/a_3.jpg', 140)
# IMG.crop('./app/template/a.png')
print(IMG.sift('./app/template/a.png'))
