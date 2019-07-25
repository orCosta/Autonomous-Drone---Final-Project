from dronekit import connect, Command, LocationGlobal, VehicleMode
from pymavlink import mavutil
import time, sys, argparse, math

print "Connecting..."
vehicle = connect('/dev/ttyS0', baud=57600, wait_ready=True)

print vehicle.mode
print "changing mode"
vehicle.mode = VehicleMode("LOITER")
time.sleep(5)
print "current mode:", vehicle.mode

