# import serial, time, pynmea2

# port = "/dev/serial0"
# baud = 9600

# serialPort = serial.Serial(port, baudrate=baud, timeout=1.0)

# while True:
#     st = ""
#     try:
#         st = serialPort.readline().decode().strip()
#     except Exception as e:
#         print(e)

#     if st.find("GGA") > 0:
#         try:
#             msg = pynmea2.parse(st)
#             print(('Lat: ', msg.latitude, ', Lon: ', msg.longitude))
#         except Exception as e:
#             print(e)
#     time.sleep(0.1)

import serial
import pynmea2
port = "/dev/serial0"
def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.latitude,msg.lat_dir,msg.longitude,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats))
 
serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
while True:
    str = serialPort.readline().decode()
    parseGPS(str)