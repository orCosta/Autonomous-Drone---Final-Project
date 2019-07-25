import time
from picamera import PiCamera
from time import sleep, strftime
from dronekit import connect, VehicleMode
from lidar_lite import Lidar_Lite


def take_pic():
    camera = PiCamera()
    camera.resolution = (1024, 768)
    print("capturing an image...")
    time = strftime("%H:%M:%S")
    date = strftime("%d/%m/%Y")
    camera.start_preview()
    sleep(3)
    camera.capture('test1_{0}_{1}.jpg'.format(time, date))
    # camera.capture("test1_{}.jpg".format(time))
    print("finish pic")



if __name__ == '__main__':

    lidar = Lidar_Lite()
    connected = lidar.connect(1)
    if connected < -1:
        print("Not Connected")
        exit()

    vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)
    vehicle.mode = VehicleMode('GUIDED')
    vehicle.armed = True
    time.sleep(5)
    if vehicle.armed:
        print("Taking off")
        vehicle.simple_takeoff(10)
        time.sleep(15)
        take_pic()
        height = lidar.getDistance()
        print("Height from LiDAR: ", height)
        time.sleep(4)
        print("Sea level alt: ", vehicle.location.global_frame.alt)
        print("Global location: ", vehicle.location.global_frame)
        print("Battery level: ", vehicle.battery.level)
    else:
        print("Vehicle not armed")
    print("Landing")
    vehicle.mode = VehicleMode('LAND')
    time.sleep(15)
    vehicle.close()
