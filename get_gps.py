import serial
import time
import string
import pynmea2
from datetime import datetime
from datetime import timedelta

while True:
	port="/dev/ttyAMA0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()
	print('----------------starting new data read-----------------------')
	print(newdata)
	new_string  = newdata.decode(encoding='iso-8859-1')
	new_list = new_string.split(',')
	print(new_list)
	new_string = new_string[new_string.find('$'):]
	#print(new_string)

	if "$GPRMC" in new_string:
		print('inside if statement')
		newmsg=pynmea2.parse(new_string)
		lat=newmsg.latitude
		print('lat= ', lat)
		lng=newmsg.longitude
		if lat == 0.0:
			dt=datetime.now()
		else:
			timestmp=newmsg.timestamp
			dt=newmsg.datetime
		delta = timedelta(hours=5)
		dt -= delta
		newdata=ser.readline()
		print(newdata)
		newdata=ser.readline()
		print(newdata)
		new_string  = newdata.decode(encoding='iso-8859-1')
		new_list = new_string.split(',')
		alt=new_list[9]
		#alt=0
		gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng) + " and Altitude=" + str(alt) + " and datetime=" + str(dt)
		print(gps)
		field_dict = ['%s: %s' % (newmsg.fields[i][0], newmsg.data[i]) 
			for i in range(len(newmsg.fields))]
		print(field_dict)
