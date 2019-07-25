from dronekit import connect, VehicleMode
from time import sleep
from click._compat import raw_input


def takeoffLand():
    print("connect...")
    vehicle = connect('/dev/ttyUSB0', wait_ready=True)
    vehicle.mode = VehicleMode('GUIDED')
    vehicle.armed = True
    sleep(5)
    if not vehicle.armed:
        print("Vehicle not armed")
        return

    print("Taking off")
    vehicle.simple_takeoff(2)
    sleep(5)
    raw_input("Press any key to land")

    print("Landing")
    vehicle.mode = VehicleMode('LAND')
    sleep(10)
    vehicle.close()

if __name__ == "__main__":
    takeoffLand()



