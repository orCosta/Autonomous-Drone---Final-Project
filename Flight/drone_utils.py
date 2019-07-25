import time
import math
import numpy as np
import json
from click._compat import raw_input
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
from datetime import datetime

# ================================================================
# ========================  Globals ==============================
# ================================================================
DEBUG = 0
LIVE = 1
MODE = DEBUG
ANGLE = 20
DEBUG_CONNECTION_STR = 'tcp:127.0.0.1:5760'
LIVE_CONNECTION_STR = '/dev/ttyACM0'
CAM_RES = (768, 768)


if MODE == LIVE:
    from lidar_lite import Lidar_Lite
    from picamera import PiCamera

# ================================================================
# ================  Auxiliary functions ==========================
# ================================================================

def get_location_metres(original_location, dNorth, dEast, dAlt):
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
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    newalt = dAlt - original_location.alt
    print("original alt: ", original_location.alt, "new alt: ", newalt)
    if type(original_location) is LocationGlobal:
        print("Creating global location")
        targetlocation = LocationGlobal(newlat, newlon, original_location.alt)
        #targetlocation = LocationGlobal(newlat, newlon,
                                        #original_location.alt + newalt)
    elif type(original_location) is LocationGlobalRelative:
        print("Creating relative location")
        #targetlocation = LocationGlobalRelative(newlat, newlon, original_location.alt)
        targetlocation = LocationGlobalRelative(newlat, newlon, original_location.alt + newalt)
    else:
        raise Exception("Invalid Location object passed")

    return targetlocation


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two `LocationGlobal` or `LocationGlobalRelative` objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5


def get_pic_size(height):
    """
    Returns the picture capture size, based on the height of the picture
    :param height:
    :return:
    """
    return 2 * height * math.tan(math.radians(ANGLE))


# ================================================================
# =========================== Classes  ===========================
# ================================================================


class Drone:

    def __init__(self):
        self.alt = None
        self.cam = None
        self.lidar = None
        self.logs = {}
        self.h_logs = {}
        self.vehicle = self._connect_drone()
        self.vehicle.mode = VehicleMode('GUIDED')
        self.f = open("dump/logs.txt", "w")
        self.num_samples = 0
        self.num_rows = 0
        self.row_size = 0

    def _connect_drone(self):
        '''
        Connect to the drone's control unit (Pixhawk4)
        :return: dronekit lib object.
        '''
        print("connecting...")
        print("Mode: ", MODE)
        if MODE == DEBUG:
            str = DEBUG_CONNECTION_STR
            print(str)
        else: # MODE == LIVE:
            str = LIVE_CONNECTION_STR
        vehicle = connect(str, wait_ready=True)
        print("connected successfully")
        return vehicle

    def _arming(self):
        self.vehicle.armed = True
        self.alt = 0
        time.sleep(5)
        if not self.vehicle.armed:
            print("Vehicle not armed")
            return False
        if MODE == LIVE:
            print("Activating devices...")
            self.cam = PiCamera()
            self.cam.resolution = CAM_RES

            self.lidar = Lidar_Lite()
            connected = self.lidar.connect(1)

            if connected < -1:                                       #TODO: check this cond
                print("Lidar not Connected")
                return False
        print("Armed successfully")
        return True

    def take_off(self, height):
        '''
        Arming the drone and taking off to the given height.
        :param height: in meters
        '''
        if not self._arming():
            return
        print("Taking off...")
        self.vehicle.simple_takeoff(height)
        self.alt = height
        time.sleep(height * 1.4)
        self.goto(-14.14, 14.14) #TODO: Delete this line

    def land(self):
        '''
        Landing.
        '''
        print("Landing...")
        self.vehicle.mode = VehicleMode('LAND')
        time.sleep(20)

    def goto(self, dNorth, dEast):
        '''
        Go x meters to North and y meters to East.
        '''
        currentLocation = self.vehicle.location.global_relative_frame
        targetLocation = get_location_metres(currentLocation, dNorth, dEast,
                                             self.alt)
        targetDistance = get_distance_metres(currentLocation, targetLocation)
        self.vehicle.simple_goto(targetLocation)

        while self.vehicle.mode.name == "GUIDED":  # Stop action if we are no longer in guided mode.
            remainingDistance = get_distance_metres(self.vehicle.location.global_frame, targetLocation)
            print("Distance to target: ", remainingDistance, ", Heading: ",
                  self.vehicle.heading)
            # if remainingDistance <= targetDistance * 0.05:  # Just below target, in case of undershoot.
            if remainingDistance <= 0.4:
                print("Reached target")
                break
            time.sleep(2)

    def take_sample(self):
        '''
        Capture image and takes height sample with the Lidar sensor.
        '''
        print("taking sample...")
        if MODE == DEBUG:
           sea_level_alt = self.vehicle.location.global_frame.alt
           print("sea level alt:" + str(sea_level_alt))
           return

        # *** LiDAR ****
        self.num_samples += 1
        s = []
        for j in range(5):
            s.append(self.lidar.getDistance())
        t = datetime.now().time()
        sea_level_alt = self.vehicle.location.global_frame.alt
        height_median = np.median(s) / 100                          
        relative_alt = sea_level_alt - height_median
        # self.h_logs[str(t)] = (height_median, sea_level_alt, relative_alt)
        self.h_logs["s_" + str(self.num_samples)] = {"Time" : str(t), "Height" : str(relative_alt), "Hading" : str(self.vehicle.heading)}

        # ==== write to file - DEBUG ====
        self.f.write(str(self.num_samples) + "- LiD height:" + str(height_median) + "| Sea level:" + str(
            sea_level_alt) + "| Relative: " + str(relative_alt) + "| Heading: " +
                  str(self.vehicle.heading) +'\n')

        # *** Camera ****
        self.cam.capture('dump/{}.jpg'.format("im_"+str(self.num_samples)))
        time.sleep(2)


    def close_connection(self):
        '''
        Close the connection of the dronekit object and save the flight logs.
        '''
        if MODE == LIVE:
            self.logs["Logs"] = self.h_logs
            self.logs["num_imgs"] = self.num_samples
            self.logs["num_rows"] = self.num_rows
            self.logs["row_size"] = self.row_size
            with open('dump/logs.json', 'w') as fp:
                json.dump(self.logs, fp)

        self.vehicle.close()
        self.f.close()
        time.sleep(2)
        print("drone disconnected")


    def _scan_straight(self, height, length, width, adv_size):
        raw_input("Place the drone in the South-East corner of the scan "
                  + "area, and press any key to start the scan")
        self.take_off(height)
        for i in range(int(length // (2 * adv_size))):
            self.take_sample()
            for j in range(int(width // adv_size)):
                self.goto(0, -adv_size)
                self.take_sample()
            self.goto(adv_size, 0)
            self.take_sample()
            for j in range(int(width // adv_size)):
                self.goto(0, adv_size)
                self.take_sample()
            self.goto(adv_size, 0)
        takeoff_return = int(length // adv_size) * adv_size + adv_size
        self.goto(int(-takeoff_return), 0)
        self.land()
        raw_input("Press any key to turn off the drone")
        self.close_connection()


    def _scan_diagonal(self, height, length, width, north, east, adv_size):
        fly_size = math.sqrt(adv_size ** 2 / 2)

        self.take_off(height)
        for i in range(int(length // (2 * adv_size))):
            self.take_sample()
            for j in range(int(width // adv_size)):
                self.goto(north * fly_size, -fly_size)
                self.take_sample()
            self.goto(fly_size, east * fly_size)
            self.take_sample()
            
            time.sleep(7)
            for j in range(int(width // adv_size)):
                self.goto(-north * fly_size, fly_size)
                self.take_sample()
            self.goto(fly_size, east * fly_size)
        takeoff_return = int(length // adv_size) * adv_size
        fly_return = math.sqrt(takeoff_return ** 2 / 2)
        self.goto(-fly_return, -east * fly_return)
        self.land()
        raw_input("Press any key to turn off the drone")
        self.close_connection()


    def scan(self, height, width, length):

        pic_size = get_pic_size(height)
        adv_size = 0.6 * pic_size

        self.num_rows = int(length // (2 * adv_size))
        self.row_size = int(width // adv_size)
        found = False
        while not found:

            print("Select the orientation of the scan area: \n" +
                "1. North \n" +
                "2. North - East \n" +
                "3. North - West")
            direction = int(input())

            if direction == 1:
                found = True
                self._scan_straight(height, length, width, adv_size)

            elif direction == 2:
                found = True
                raw_input("Place the drone in the Southern corner of the scan "
                          + "area, and press any key to start the scan")
                self._scan_diagonal(height, length, width, 1, 1, adv_size)

            elif direction == 3:
                found = True
                raw_input("Place the drone in the Eastern corner of the scan "
                        + "area, and press any key to start the scan")
                self._scan_diagonal(height, length, width, -1, -1, adv_size)

            else:
                print("Bad direction")








