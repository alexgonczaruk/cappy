import time
import serial
import adafruit_gps

uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
gps = adafruit_gps.GPS(uart, debug=False)
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