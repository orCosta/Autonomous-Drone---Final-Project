import time
from dronekit import connect, VehicleMode

vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)
vehicle.mode = VehicleMode('GUIDED')
vehicle.armed = True
time.sleep(5)
if vehicle.armed:
    print("Taking off")
    vehicle.simple_takeoff(10)
    time.sleep(15)
else:
    print("Vehicle not armed")
print("Landing")
vehicle.mode = VehicleMode('LAND')
time.sleep(15)
vehicle.close()
