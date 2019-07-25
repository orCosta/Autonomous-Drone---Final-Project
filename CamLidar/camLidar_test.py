from picamera import PiCamera
from time import sleep
from lidar_lite import Lidar_Lite
import numpy as np
import json
from datetime import datetime


camera = PiCamera()
camera.resolution = (1024, 768)

lidar = Lidar_Lite()
connected = lidar.connect(1)

if connected < -1:
  print("Not Connected")
  
l_samples = {}

camera.start_preview(fullscreen=False, window=(100, 20, 640, 480))

for i in range(5):
    try:
        input("sample number {}".format(i+1))
    except SyntaxError:
        pass
    s = []
    for j in range(5):
        s.append(lidar.getDistance())
    t = datetime.now().time()
    l_samples[str(t)] = (np.median(s))
    camera.capture('{}.jpg'.format(str(t)))
    #sleep(2)

print(l_samples)

with open('data.json', 'w') as fp:
    #feeds = json.load(fp)
    json.dump(l_samples, fp)
#camera.capture('test1_{0}_{1}.jpg'.format(time, date))
#camera.capture("{}.jpg".format(time))
print("finish test")