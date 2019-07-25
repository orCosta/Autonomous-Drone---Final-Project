import time
from dronekit import connect, VehicleMode

vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)
print("Global location: ", vehicle.location.global_frame)
print("Sea level alt: ", vehicle.location.global_frame.alt)
vehicle.close()