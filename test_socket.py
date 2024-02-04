import socket
import random
import time
import serial
import adafruit_gps
from test_obstacle_detection import detection
from math import cos, asin, sqrt, pi

serverIP = "192.168.2.52"
serverPORT = 8888

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverIP, serverPORT))
serverSocket.listen()

print("Waiting for connection")
connectionSocket, addr = serverSocket.accept()
print("connected to client!")

ACTION = "ACTION"
COORDINATE = "COORDINATE"

lat_avg = []
lon_avg = []
last = time.monotonic()
MAX_LIST_SIZE = 20

uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,1000')

GLOBAL_OBSTACLE_STOP = False

def get_rpi_coordinates(last = time.monotonic(), lat_avg = [], lon_avg = []):
    for i in range(10):
        gps.update()

        time.sleep(2)
        current = time.monotonic()
        print(f"current time: {current}, last time: {last}")
        if current - last >= 1.0:
            if not gps.has_fix:
                print(f"Latitude: {gps.latitude} degrees")
                print(f"Longitude: {gps.longitude} degrees")
                print(f"gps does not have fix so printing {0}, {0}, {last}, {lat_avg}, {lon_avg}")
                continue
                # return 0, 0, last, lat_avg, lon_avg

            lat_avg.append(gps.latitude)
            lon_avg.append(gps.longitude)

            if len(lat_avg) > MAX_LIST_SIZE:
                lat_avg.pop(0)
            if len(lon_avg) > MAX_LIST_SIZE:
                lon_avg.pop(0)

            print('Latitude: {0:.6f} degrees'.format(sum(lat_avg)/len(lat_avg)))
            print('Longitude: {0:.6f} degrees'.format(sum(lon_avg)/len(lon_avg)))
            print(f"returning {last} {lat_avg} {lon_avg}")
            
        return sum(lat_avg)/len(lat_avg), sum(lon_avg)/len(lon_avg), last, lat_avg, lon_avg

# for latitude, if the diff lat2>lat1, the phone is more north. Move north
# for longitude, if the diff lon2>lon1, the phone is more east. Move east
def distance(lat1, lon1, lat2, lon2):
    r = 6371000 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2

    dist = 2 * r * asin(sqrt(a))

    return dist

def calculate_angle_offset(lat1, lon1, lat2, lon2):
    # Convert latitudes and longitudes to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Calculate the angle offset (bearing) using simplified tangent approximation
    angle_offset = math.atan2(lon2_rad - lon1_rad, lat2_rad - lat1_rad)

    # Convert angle offset from radians to degrees
    angle_offset_deg = math.degrees(angle_offset)
    direction = "NW"
    if lat2>lat1:
        if lon2>lon1:
            direction = "NE"
    else:
        if lon2>lon1:
            direction = "SE"
        else:
            direction = "SW"

    return angle_offset_deg, direction

def parse_location(content):

    # Parse the phone's coordinates
    phone_location = content.split(", ")
    phone_location_lat = float(phone_location[0])
    phone_location_lon = float(phone_location[1])

    print(f"Coordinates: {phone_location_lat}, {phone_location_lon}")

    return phone_location_lat, phone_location_lon


while True:
    message = connectionSocket.recv(1024).decode()
    code, content = message.split(":", 1)

    # Obstacle detection case, wait for phone to transmit "ACTION:START"
    if GLOBAL_OBSTACLE_STOP is True:
        if code == ACTION and content == "START":
            GLOBAL_OBSTACLE_STOP = False
        else:
            # TURN OFF MOTORS
            while code != ACTION and content != "START":
                message = connectionSocket.recv(1024).decode()
                code, content = message.split(":", 1)

    if code == ACTION:
        print(f"Incoming action: {content}")
    else:
        if lat_avg == []:
            pi_location_lat, pi_location_lon, last, lat_avg, lon_avg = get_rpi_coordinates()
        else:
            pi_location_lat, pi_location_lon, last, lat_avg, lon_avg = get_rpi_coordinates(last, lat_avg, lon_avg)

        print(f"pi lat: {pi_location_lat}, pi lon: {pi_location_lon}")

        phone_location_lat, phone_location_lon = parse_location(content)

        distance_from_phone = distance(pi_location_lat, pi_location_lon, phone_location_lat, phone_location_lon)
        distance_from_phone = "PI:" + str(round(distance_from_phone, 2))

        # compute direction to turn towards
        direction_to_turn, cardinal_direction = calculate_angle_offset(pi_location_lat, pi_location_lon, phone_location_lat, phone_location_lon)

        # FOR NOW KEEPING THE BELOW CODE HERE BECAUSE WE HAVE THE SOCKET HERE AS WELL
        obstacle_distance, strength = detection()

        # pre-screening, may need to adjust strength threshold
        if obstacle_distance >= 0.2 obstacle_distance <= 5 and strength >= 900:
            connectionSocket.send("ACTION:STOP".encode())
            GLOBAL_OBSTACLE_STOP = True
        
        # probably should be else. Ideally, we receive one message, then send one message.
        else:
            print(f"Pi's distance from phone: {distance_from_phone}")
            connectionSocket.send(distance_from_phone.encode())
        