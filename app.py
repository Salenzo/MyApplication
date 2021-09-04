from app.config import cfg
from app.adb import ADBClient
from app.img import image

IMG = image('./app/img/a_3.jpg', 140)
IMG.crop('./app/template/b.png')
IMG.sift('./app/template/b.png')
