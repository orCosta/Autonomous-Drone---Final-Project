from picamera import PiCamera
from time import sleep
from lidar_lite import Lidar_Lite

camera = PiCamera()
camera.resolution = (1024, 768)

lidar = Lidar_Lite()
connected = lidar.connect(1)

if connected < -1:
  print("Not Connected")
  


camera.start_preview(fullscreen=False, window=(100, 20, 640, 480))

while True:
    print(lidar.getDistance())
    

print("finish test")