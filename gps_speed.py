# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from math import *
from datetime import datetime
import csv


def gps_distance(lon1, lat1, lon2, lat2):
    """
    inputs two gps coordinates and outputs distance between coordinates

    Parameters
    ----------
    lon1 : float
        first longitude.
    lat1 : float
        first latitude.
    lon2 : float
        second longitude.
    lat2 : float
        second latitude.

    Returns distance in between to coordinates in kilometers
    -------
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return 6371 * c

def gps_bearing(lon1, lat1, lon2, lat2):
    """
    inputs two gps coordinates and outputs bearing


    Parameters
    ----------
    lon1 : float
        first longitude.
    lat1 : float
        first latitude.
    lon2 : float
        second longitude.
    lat2 : float
        second latitude.

    Returns
    -------
    TYPE float
        bearing between gps coordinates.

    """
    return atan2(cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1), sin(lon2-lon1)*cos(lat2)) 

def horizontal_speed(lon1, lat1, lon2, lat2, time1, time2):
    """
    inputs two gps coordinates and timestamps and returns speed in km/hr

    Parameters
    ----------
    lon1 : float
        first longitude.
    lat1 : float
        first latitude.
    lon2 : float
        second longitude.
    lat2 : float
        second latitude.
    time1 : datetime
        first timestamp.
    time2 : datetime
        second timestamp.

    Returns
    -------
    float
        speed between coordinates in km/hr

    """
    distance = gps_distance(lon1, lat1, lon2, lat2)
    elapsed_time = time2 - time1
    elapsed_hours = elapsed_time.seconds/3600
    return distance / elapsed_hours

with open('ballon_data_19Sep.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    balloon_data = list(reader)

last_lat = 0.0
last_long = 0.0
for row in range(len(balloon_data)):
    lat = float(balloon_data[row]['Latitude'])
    long = float(balloon_data[row]['Longitude'])
    dt = balloon_data[row]['Date'] + ' ' + balloon_data[row]['Time']
    time = datetime.strptime(dt, '%m/%d/%Y %H:%M:%S')
    speed = 0
    distance = 0
    bearing = 0
    if long != 0:
        if last_lat != 0:
            distance = gps_distance(last_long, last_lat, long, lat)
            speed = horizontal_speed(last_long, last_lat, long, lat, last_time, time)
            speed = speed * 0.621371
            bearing = degrees(gps_bearing(last_long, last_lat, long, lat))
            print(distance, speed, bearing)
    last_lat = lat
    last_long = long
    last_time = time
    balloon_data[row]['Distance'] = distance
    balloon_data[row]['Speed'] = speed
    balloon_data[row]['Bearing'] = bearing

    
    
# data from row and 29 and 30 from 9/19/21 spreadsheet
Aaltitude = 256
Oppsite  = 1270.9
lat1 = 41.88329117
lat2 = 41.88403167
lon1 = -92.10593833
lon2 = -92.1057815
time1 = datetime.strptime('9/19/21 10:29:14', '%m/%d/%y %H:%M:%S')
time2 = datetime.strptime('9/19/21 10:29:23', '%m/%d/%y %H:%M:%S')


Base = gps_distance(lon1, lat1, lon2, lat2)
Bearing = gps_bearing(lon1, lat1, lon2, lat2)
speed = horizontal_speed(lon1, lat1, lon2, lat2, time1, time2)
Bearing = degrees(Bearing)

print("")
print("")
print("--------------------")
print("Horizontal Distance:")
print(Base)
print("--------------------")
print("Horizontal Speed")
print(speed, ' kmph')
print("--------------------")
print("Bearing:")
print(Bearing)
print("--------------------")


Base2 = Base * 1000
distance = Base * 2 + Oppsite
Caltitude = Oppsite - Aaltitude

a = Oppsite/Base
b = atan(a)
c = degrees(b)

distance = distance / 1000

print("The degree of vertical angle is:")
print(c)
print("--------------------")
print("The distance between the Balloon GPS and the Antenna GPS is:")
print(distance)
print("--------------------")