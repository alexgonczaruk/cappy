import serial,time
import numpy as np

ser = serial.Serial("/dev/ttyUSB0", 115200,timeout=0) # mini UART serial device

def read_tfluna_data():
    while True:
        counter = ser.in_waiting # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9) # read 9 bytes
            ser.reset_input_buffer() # reset buffer

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3]*256 # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5]*256 # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7]*256 # temp in next two bytes
                temperature = (temperature/8.0) - 256.0 # temp scaling and offset
                return distance/100.0,strength,temperature

# while True:
#     # print("checking if open")
#     if ser.isOpen() == False:
#         print("opening")

#         ser.open() # open serial port if not open
#     # print("already open")
#     distance,strength,temperature = read_tfluna_data() # read values
#     # note that when strength < 100, distance = -1. Also, we should probs ignore strengths of under ~1k? maybe 500
#     print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
#               format(distance,strength,temperature)) # print sample data
#     ser.close() # close serial port
   
#     time.sleep(2)


import time
import serial
import adafruit_gps

uart1 = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
gps = adafruit_gps.GPS(uart1, debug=False)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')

lat_avg = []
lon_avg = []
MAX_LIST_SIZE = 20
CAP = 20

last_print = time.monotonic()

def get_rpi_coordinates(last = time.monotonic(), lat_avg = [], lon_avg = []):
    print("before updating gps")
    gps.update()
    print("gps updated")
    time.sleep(2)
    print("sleep for 2 seconds")
    current = time.monotonic()
    print("current time: {current}, last time: {last}")
    
    # if current - last >= 1.0:
    print("inside if")
    if not gps.has_fix:
        print("gps does not have fix so printing {0}, {0}, {last}, {lat_avg}, {lon_avg}")
        return 0, 0, last, lat_avg, lon_avg

    lat_avg.append(gps.latitude)
    lon_avg.append(gps.longitude)

    if len(lat_avg) > MAX_LIST_SIZE:
        lat_avg.pop(0)
    if len(lon_avg) > MAX_LIST_SIZE:
        lon_avg.pop(0)

    print('Latitude: {0:.6f} degrees'.format(sum(lat_avg)/len(lat_avg)))
    print('Longitude: {0:.6f} degrees'.format(sum(lon_avg)/len(lon_avg)))
    print("returning {last} {lat_avg} {lon_avg}")
    return sum(lat_avg)/len(lat_avg), sum(lon_avg)/len(lon_avg), last, lat_avg, lon_avg

while True:
    gps.update()

    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            print('Waiting for fix...')
            continue

        lat_avg.append(gps.latitude)
        lon_avg.append(gps.longitude)

        if len(lat_avg) > CAP:
            lat_avg.pop(0)
        if len(lon_avg) > CAP:
            lon_avg.pop(0)

        print('=' * 40)  # Print a separator line.
        # print('Latitude: {0:.6f} degrees'.format(gps.latitude))
        # print('Longitude: {0:.6f} degrees'.format(gps.longitude))

        print('Latitude: {0:.6f} degrees'.format(sum(lat_avg)/len(lat_avg)))
        print('Longitude: {0:.6f} degrees'.format(sum(lon_avg)/len(lon_avg)))

        if ser.isOpen() == False:
            print("opening")

            ser.open() # open serial port if not open
        # print("already open")
        distance,strength,temperature = read_tfluna_data() # read values
        # note that when strength < 100, distance = -1. Also, we should probs ignore strengths of under ~1k? maybe 500
        print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
                format(distance,strength,temperature)) # print sample data
        ser.close() # close serial port