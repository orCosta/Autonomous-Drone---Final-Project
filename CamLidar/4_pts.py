import math
import time
import sys
import dronekit
import json
import numpy as np
from dronekit import connect, VehicleMode, LocationGlobal,\
    LocationGlobalRelative
from picamera import PiCamera
from time import sleep, strftime
from lidar_lite import Lidar_Lite
from datetime import datetime
from click._compat import raw_input

l_samples = {}



def goto(dNorth, dEast, gotoFunction):
    currentLocation=vehicle.location.global_relative_frame
    targetLocation=get_location_metres(currentLocation, dNorth, dEast)
    targetDistance=get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        remainingDistance=get_distance_metres(vehicle.location.global_frame, targetLocation)
        print( "Distance to target: ", remainingDistance)
        if remainingDistance<=targetDistance*0.01: #Just below target, in case of undershoot.
            print("Reached target")
            break
        time.sleep(2)


def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.

    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
    else:
        raise Exception("Invalid Location object passed")

    return targetlocation;


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two `LocationGlobal` or `LocationGlobalRelative` objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
 
 
def point_handler(i, cam, lid):
    s = []
    for j in range(5):
        s.append(lid.getDistance())
    t = datetime.now().time()
    l_samples[str(t)] = (np.median(s))
    cam.capture('4pts_dump/{}.jpg'.format(str(t)))
    print(i, "- Sea level alt: ", vehicle.location.global_frame.alt)
    print(i, "- Global location: ", vehicle.location.global_frame)
    print(i, "- Battery level: ", vehicle.battery.level)
    sleep(2)
    

def four_points(connect_str):
    print("connect to: " + connect_str)
    vehicle = connect(connect_str, wait_ready=True)
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
    time.sleep(15)
    goto(10, 0, vehicle.simple_goto)
    point_handler(1, camera, lidar)
    goto(0, 10, vehicle.simple_goto)
    point_handler(2, camera, lidar)
    goto(-10, 0, vehicle.simple_goto)
    point_handler(3, camera, lidar)
    goto(0, -10, vehicle.simple_goto)
    point_handler(4, camera, lidar)
    
    print("Landing")
    vehicle.mode = VehicleMode('LAND')
    sleep(15)
    raw_input("Press any key to turn off the drone")
    vehicle.close()
    
    with open('4pts_dump/logs.json', 'w') as fp:
        json.dump(l_samples, fp)


if __name__ == '__main__':
    four_points(sys.argv[1])
    
    
    
    

