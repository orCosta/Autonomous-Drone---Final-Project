import sys
from dronekit import connect, VehicleMode
from picamera import PiCamera
from time import sleep
from lidar_lite import Lidar_Lite
import numpy as np
import json
from datetime import datetime

l_samples = {}

def takeSample(lid, cam):
    s = []
    for j in range(5):
        s.append(lid.getDistance())
    t = datetime.now().time()
    l_samples[str(t)] = (np.median(s))
    cam.capture('takeoff_dump/takeoff_land{}.jpg'.format(str(t)))
    sleep(2)

def takeoffLand(connect_str):
    print("connect to: " + connect_str)
    vehicle = connect('udp:172.29.113.100:14550', wait_ready=True)
    vehicle.mode = VehicleMode('GUIDED')
    vehicle.armed = True
    sleep(5)
    if not vehicle.armed:
        print("Vehicle not armed")
        return
    
    print("tern on devices...")
    camera = PiCamera()
    camera.resolution = (1024, 768)

    lidar = Lidar_Lite()
    connected = lidar.connect(1)

    if connected < -1:
        print("Lidar not Connected")
        return
        
    print("Taking off")
    vehicle.simple_takeoff(10)
    sleep(15)
    takeSample(lidar, camera)
    takeSample(lidar, camera)
    
    
    print("Landing")
    vehicle.mode = VehicleMode('LAND')
    sleep(15)
    vehicle.close()
    
    with open('takeoff_dump/takeoff_land_logs.json', 'w') as fp:
        json.dump(l_samples, fp)
        
if __name__ == "__main__":
    takeoffLand(sys.argv[1])
    
    
    
    