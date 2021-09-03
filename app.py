from app.config import cfg
from app.adb import ADBClient
from app.img import image

IMG = image('./app/img/a_1.jpg', 140)
IMG.sift('./app/template/a.png')
