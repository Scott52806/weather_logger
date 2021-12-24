
#!/usr/bin/env python3
########################################################################
# Filename    : data_logger.py
# Description : Caputure sensor data and write to csv file
# Author      : Scott Anderson
# modification: 3/5/2021
########################################################################
import RPi.GPIO as GPIO
# import Freenove_DHT as DHT
import smbus2
import bme280
import csv
from time import sleep, strftime
from datetime import datetime
from datetime import timedelta
import serial
import time
import string
import pynmea2
import traceback

port = 1
address = 0x76
address_ext = 0x77
bus = smbus2.SMBus(port)
ledPin = 11       # define ledPin
port = "/dev/ttyAMA0"
tz_offset = 5

calibration_params = bme280.load_calibration_params(bus, address)
calibration_params_ext = bme280.load_calibration_params(bus, address_ext)
print('init complete')
print(dir(bme280))
#b280 = bme280(bus, address)

def setup():
    """
    Inputs:
        none
    Outputs:
        Setup tasks complete for GPIO
    """
    GPIO.setmode(GPIO.BOARD)        # use PHYSICAL GPIO Numbering
    #GPIO.setup(sensorPin, GPIO.IN)  # set sensorPin to INPUT mode
    GPIO.setup(ledPin, GPIO.OUT)    # set ledPin to OUTPUT mode
    GPIO.output(ledPin, GPIO.LOW)   # make ledPin output LOW level to turn off led
    ser = serial.Serial(port, baudrate=9600, timeout=0.5)
    dataout = pynmea2.NMEAStreamReader()

 
def get_time_now():
    """
    Inputs:
        none
    Outputs:
        Current system time
    """
    return datetime.now().strftime('%H:%M:%S')

def get_date_now():
    """
    Inputs:
        none
    Outputs:
        Current system daate
    """
    return datetime.now().strftime('%m/%d/%y')

def append_csv(temp_list):
    """
    Inputs:
        list that will be written as a row in the csv file
    Outputs:
        none
    """
    with open ('temp_data.csv', 'a') as graphFile:
        graphFileWriter=csv.writer(graphFile)
        graphFileWriter.writerow(temp_list)
        #print('.')

def read_temp_hum(bus, address, calibration_params):
    """
    Input:
        dht sensor object
    Output:
        Temp in F. and Humidity
    """
    data = bme280.sample(bus, address, calibration_params)
    ftemp = data.temperature*9/5+32
    return ftemp, data.humidity, data.pressure

def blink_led():
    """
    Input:
        Input none
    Output: Blink Light, not return
    """
    GPIO.output(ledPin, GPIO.HIGH)  # make ledPin output HIGH level to turn on led
    sleep(1)                   # Wait for 1 second
    GPIO.output(ledPin, GPIO.LOW)   # make ledPin output LOW level to turn off led


def read_gps(debug=False):
	"""
	Input:
	    Input debug=False
	Output: Long, Lat, Alt, Date, Time
	"""
	if debug:
		print('read_gps called')
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	not_found = True
	ser_line_counter = 0

	while not_found:
		if debug:
			print('Inside while loop: ', ser_line_counter)
		#read from serial port and convert to a string
		newdata = ser.readline()
		new_string = newdata.decode(encoding='iso-8859-1')
		new_string = new_string[new_string.find('$'):]
		if debug:
			print('Sting: ',new_string)
		ser_line_counter += 1
		#check to see if blank data is coming out of serial port, likely not connected to sat.
		if ser_line_counter > 100:
			if debug:
				print('serial line counter tripped: ', ser_line_counter)
			not_found = False
			lng = 0
			lat = 0
			alt=0
			dt = datetime.now()
			break
		#if GPRMC string is found then we hae lat and long data
		if "$GPRMC" in new_string:
			if debug:
				print('GPRMC String Found: ', new_string)
			newmsg = pynmea2.parse(new_string)
			lat = newmsg.latitude
			lng = newmsg.longitude
			if lat == 0.0:
				dt=datetime.now()
			else:
				dt = newmsg.datetime
				dt -= timedelta(hours = tz_offset)
			#Altitude data is two lines past long and lat
			newdata=ser.readline()
			newdata=ser.readline()
			new_string  = newdata.decode(encoding='iso-8859-1')
			new_list = new_string.split(',')
			alt=new_list[9]
			not_found = False

	if debug:
		print('leaving read GPS: ',lat,lng)
	return lat, lng, alt, dt.strftime('%m/%d/%y'),dt.strftime('%H:%M:%S')

def loop():
    counts = 0 # Measurement counts
    blink_counter = 0
    sleep_amt = 8
    blink_amt = 10
    while(True):
        counts += 1
        temp, humidity, pressure = read_temp_hum(bus, address, calibration_params)
        temp_ext, humidity_ext, pressure_ext = read_temp_hum(bus, address_ext, calibration_params_ext)
        lat, lng, alt, gps_date, gps_time = read_gps()

        # append time, temp and humidity to data file
        temp_list = [get_date_now(), get_time_now(), temp, humidity, pressure, temp_ext, humidity_ext, pressure_ext, lng, lat, alt, gps_date, gps_time]
        append_csv(temp_list)
        if blink_counter > blink_amt:
            blink_led()
            blink_counter = 0
        blink_counter += 1

        #print("Humidity : %.2f, \t Temperature : %.2f \n"%(humidity, temp))
        #print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.humidity,ftemp))

        sleep(sleep_amt)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':
    print ('Program is starting ... ')
    setup()

    try:
        loop()

    except KeyboardInterrupt:
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
        print('keyboardInterrupt')
        destroy()

    except Exception:
    # this catches ALL other exceptions including errors.  
    # You won't get any error messages for debugging  
    # so only use it once your code is working  
        print('general except triggered')
        traceback.print_exc()
        destroy()

    finally:
        print('finally triggered')
        destroy()

